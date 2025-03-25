
from typing import Type, TypeVar, Tuple, Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from src.core.config import settings
import logging
import json

T = TypeVar('T', bound=BaseModel)
logger = logging.getLogger(__name__)

class ParamExtractor:
    """Service for extracting structured parameters from unstructured text using LLMs"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,  # Using the default model from settings
            temperature=0.0,  # Zero temperature for deterministic outputs
            api_key=settings.OPENAI_API_KEY
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
        chain = prompt | self.llm | parser
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
