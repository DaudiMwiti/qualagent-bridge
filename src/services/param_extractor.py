
from typing import Type, TypeVar, Tuple, Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from src.core.config import settings
import logging
import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

T = TypeVar('T', bound=BaseModel)
logger = logging.getLogger(__name__)

class ParamExtractor:
    """Service for extracting structured parameters from unstructured text using LLMs"""
    
    def __init__(self):
        self.openai_client = httpx.AsyncClient(
            timeout=60.0,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        )
        
        self.replicate_client = httpx.AsyncClient(
            timeout=120.0,
            headers={"Authorization": f"Token {settings.REPLICATE_API_TOKEN}"}
        )
    
    async def extract(
        self,
        text: str,
        schema: Type[T],
        max_retries: int = 2
    ) -> Tuple[T, str]:
        """
        Extracts and validates parameters with automatic error recovery
        
        Args:
            text: The input text to extract parameters from
            schema: Pydantic schema defining the expected parameters
            max_retries: Number of retry attempts if validation fails
            
        Returns:
            Tuple containing (parsed_params, debug_rationale)
            
        Raises:
            ValueError: If unable to extract valid parameters after retries
        """
        # Determine which provider to use
        provider = settings.PARAM_EXTRACTION_PROVIDER
        
        try:
            if provider == "mixtral" and settings.REPLICATE_API_TOKEN:
                return await self._extract_replicate(text, schema, max_retries)
            else:
                # Default to OpenAI
                return await self._extract_openai(text, schema, max_retries)
        except Exception as e:
            logger.error(f"Error with primary provider: {str(e)}")
            # Fall back to OpenAI if other provider fails
            return await self._extract_openai(text, schema, max_retries)
    
    async def _extract_openai(
        self,
        text: str,
        schema: Type[T],
        max_retries: int = 2
    ) -> Tuple[T, str]:
        """Extract parameters using OpenAI"""
        parser = PydanticOutputParser(pydantic_object=schema)
        
        # Create a prompt template that instructs the model to extract parameters
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Extract structured parameters from the provided text.
            Follow these rules:
            1. Be strict about required fields
            2. Infer missing values when logical
            3. Return ONLY valid JSON matching the schema
            
            Schema: {schema}
            Format instructions: {format_instructions}
            """),
            ("user", "{input_text}")
        ])
        
        # Create the chain: prompt -> LLM -> parser
        llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            temperature=0.0,
            api_key=settings.OPENAI_API_KEY
        )
        chain = prompt | llm | parser
        last_error = None
        
        # Try extraction with retries on validation failure
        for attempt in range(max_retries + 1):
            try:
                # Run the extraction chain
                result = await chain.ainvoke({
                    "schema": schema.model_json_schema(),
                    "format_instructions": parser.get_format_instructions(),
                    "input_text": text
                })
                return result, "Success"
                
            except ValidationError as e:
                last_error = e
                logger.warning(f"Validation error (attempt {attempt+1}): {str(e)}")
                # Inject error feedback into next attempt
                text = f"{text}\n\nERROR FEEDBACK: {str(e)}\nPlease fix these issues and try again."
                
        # If we got here, all retries failed
        error_msg = f"Failed to extract valid parameters after {max_retries+1} attempts: {last_error}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _extract_replicate(
        self,
        text: str,
        schema: Type[T],
        max_retries: int = 2
    ) -> Tuple[T, str]:
        """Extract parameters using Replicate (Mixtral)"""
        schema_json = schema.model_json_schema()
        
        # Format the system prompt with the schema information
        system_prompt = f"""
        You are a parameter extraction specialist. Extract structured parameters from the provided text.
        
        Schema: {json.dumps(schema_json, indent=2)}
        
        Follow these rules:
        1. Be strict about required fields
        2. Infer missing values when logical
        3. Return ONLY valid JSON matching the schema, nothing else
        """
        
        last_error = None
        
        # Try extraction with retries on validation failure
        for attempt in range(max_retries + 1):
            try:
                # Set up the user prompt with any error feedback from previous attempts
                user_prompt = text
                if last_error:
                    user_prompt = f"{text}\n\nERROR FEEDBACK: {str(last_error)}\nPlease fix these issues and try again."
                
                # Send request to Replicate API
                response = await self.replicate_client.post(
                    "https://api.replicate.com/v1/predictions",
                    json={
                        "version": "42f9217799ec518e5427e59fc1afda4fbb7e2572089267c2197c520d46617ab8",  # Mixtral 8x7B Instruct v0.1
                        "input": {
                            "system_prompt": system_prompt,
                            "prompt": user_prompt,
                            "temperature": 0.1,
                            "max_tokens": 1024,
                            "top_p": 0.95
                        }
                    }
                )
                response.raise_for_status()
                prediction = response.json()
                
                # Poll for completion
                prediction_id = prediction["id"]
                prediction_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                
                # Wait for the prediction to complete
                while True:
                    poll_response = await self.replicate_client.get(prediction_url)
                    poll_response.raise_for_status()
                    prediction_status = poll_response.json()
                    
                    if prediction_status["status"] == "succeeded":
                        break
                    elif prediction_status["status"] == "failed":
                        raise ValueError(f"Replicate prediction failed: {prediction_status.get('error')}")
                
                # Extract the output
                output = prediction_status["output"]
                
                # The output might be a string or a list of strings, handle both cases
                if isinstance(output, list):
                    content = "".join(output)
                else:
                    content = output
                
                # Extract JSON from the response
                try:
                    # Try to extract JSON if it's wrapped in markdown code blocks
                    if "```json" in content:
                        json_str = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        json_str = content.split("```")[1].strip()
                    else:
                        # Otherwise just try to parse the whole thing
                        json_str = content.strip()
                    
                    # Parse JSON
                    parsed_json = json.loads(json_str)
                    
                    # Validate against the schema
                    result = schema(**parsed_json)
                    return result, "Success"
                    
                except (json.JSONDecodeError, ValidationError) as e:
                    last_error = e
                    logger.warning(f"Validation error (attempt {attempt+1}): {str(e)}")
                    # Continue to next retry
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Error with Replicate (attempt {attempt+1}): {str(e)}")
                # Continue to next retry
                
        # If we got here, all retries failed
        error_msg = f"Failed to extract valid parameters after {max_retries+1} attempts: {last_error}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    async def extract_with_fallback(
        self,
        text: str,
        schema: Type[T],
        default_values: Dict[str, Any]
    ) -> Tuple[T, bool]:
        """
        Extracts parameters with a fallback to default values
        
        Args:
            text: Input text
            schema: Pydantic schema
            default_values: Default parameter values
            
        Returns:
            Tuple of (parameters, used_extraction)
        """
        try:
            # First try LLM extraction
            params, _ = await self.extract(text, schema)
            return params, True
        except Exception as e:
            # Fall back to defaults with whatever we can extract manually
            logger.info(f"Using fallback parameters: {str(e)}")
            
            # Basic keyword extraction for fallback
            simple_params = self._extract_simple_params(text, default_values)
            
            # Merge with defaults and validate
            merged_params = {**default_values, **simple_params}
            try:
                return schema(**merged_params), False
            except ValidationError:
                # Last resort: just use defaults
                return schema(**default_values), False
    
    def _extract_simple_params(self, text: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Very simple rule-based extraction for fallback cases"""
        params = {}
        
        # Extract text parameter if needed
        if "text" in defaults and isinstance(defaults["text"], str):
            # Just use the input text trimmed to a reasonable length
            max_length = 5000  # Reasonable limit
            params["text"] = text[:max_length]
        
        # Extract query parameter if needed
        if "query" in defaults and isinstance(defaults["query"], str):
            # Use the first sentence or a portion as the query
            first_sentence = text.split('.')[0]
            params["query"] = first_sentence[:100]
        
        return params

# Create a singleton instance for app-wide use
param_extractor = ParamExtractor()
