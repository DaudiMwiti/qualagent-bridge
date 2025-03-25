
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

@tool(return_direct=False)
async def summarize_memory(memories: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Summarize a collection of agent memories into a concise, context-relevant summary.
    
    Args:
        memories: List of memory dictionaries, each containing "text", "tags", "score", 
                 and optional "timestamp" or "source".
                 
    Returns:
        A JSON object with a concise summary (50-100 words) synthesizing the most relevant ideas.
    """
    logger.info(f"Summarizing {len(memories)} memories")
    
    if not memories:
        return {"summary": "No memories provided to summarize."}
    
    # Sort memories by relevance (score)
    sorted_memories = sorted(memories, key=lambda x: x.get("score", 0), reverse=True)
    
    # Prioritize important tags
    priority_tags = ["insight", "barrier", "theme", "recommendation", "observation"]
    prioritized_memories = []
    
    # First, add memories with priority tags
    for memory in sorted_memories:
        tags = memory.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]  # Convert single tag to list
            
        if any(tag in priority_tags for tag in tags):
            prioritized_memories.append(memory)
    
    # Then add remaining memories up to a reasonable limit
    remaining_memories = [m for m in sorted_memories if m not in prioritized_memories]
    all_memories = prioritized_memories + remaining_memories[:5]  # Limit to avoid token overload
    
    # Prepare the memories for the prompt
    memory_texts = []
    for i, memory in enumerate(all_memories, 1):
        text = memory.get("text", "")
        tags = memory.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        score = memory.get("score", 0)
        source = memory.get("source", "Unknown")
        
        memory_entry = f"Memory {i}:\nText: {text}\nTags: {', '.join(tags)}\nRelevance: {score:.2f}\nSource: {source}\n"
        memory_texts.append(memory_entry)
    
    # Join all memory texts
    all_memory_text = "\n".join(memory_texts)
    
    # Create the prompt for the LLM
    prompt = f"""
You are tasked with summarizing the following agent memories into a concise, context-relevant summary.

MEMORIES:
{all_memory_text}

INSTRUCTIONS:
1. Focus on the most relevant memories (highest relevance score or tagged as 'insight', 'barrier', or 'theme')
2. Group similar memories when possible
3. Do not include direct quotes, just themes and main points
4. Create a concise summary between 50-100 words
5. Focus on extracting the most important insights, patterns, and concepts

Your summary should be informative, neutral, and focus on key information that would be most useful for contextual understanding.
"""

    try:
        # Initialize the LLM
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",  # Use a smaller model for efficiency
            temperature=0.3  # Keep it factual and consistent
        )
        
        # Generate the summary
        response = await llm.ainvoke([
            {"role": "system", "content": "You are an AI assistant that summarizes information concisely and accurately."},
            {"role": "user", "content": prompt}
        ])
        
        summary = response.content.strip()
        
        # Ensure summary is within desired length (approximately 50-100 words)
        word_count = len(summary.split())
        if word_count > 150:  # Allow some flexibility
            logger.warning(f"Summary too long ({word_count} words), requesting shorter version")
            
            # Ask for a shorter version
            shorter_response = await llm.ainvoke([
                {"role": "system", "content": "You create extremely concise summaries."},
                {"role": "user", "content": f"Please create a shorter version of this summary (50-100 words max):\n\n{summary}"}
            ])
            
            summary = shorter_response.content.strip()
        
        logger.info(f"Generated memory summary with {len(summary.split())} words")
        return {"summary": summary}
        
    except Exception as e:
        logger.error(f"Error in summarize_memory: {str(e)}")
        return {"summary": "Failed to generate summary due to an error.", "error": str(e)}
