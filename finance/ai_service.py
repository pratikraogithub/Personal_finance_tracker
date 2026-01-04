import ollama
import logging

logger = logging.getLogger(__name__)

def query_llm(
    prompt: str, 
    model: str = "llama3.2:3b",
    temperature: float = 0.7,
    max_tokens: int = 500,
    stream: bool = False,
    system_message: str = None
) -> str:
    """
    Send a prompt to your local Ollama LLaMA model and get a response.
    
    Args:
        prompt: The user's question or request
        model: Ollama model name (default: "llama3.2")
        temperature: Creativity level 0-1 (default: 0.7)
        max_tokens: Maximum response length (default: 500)
        stream: Whether to stream the response (default: False)
        system_message: Custom system prompt (optional)
    
    Returns:
        str: The model's response
    """
    
    # Default system message for finance assistant
    if system_message is None:
        system_message = (
            "You are an intelligent personal finance assistant. "
            "You analyze user income and expenses, then give clear insights and advice "
            "on saving, spending, or budgeting. Be concise and human-like."
        )
    
    try:
        # Build messages
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]
        
        logger.info(f"Querying {model} with prompt: {prompt[:100]}...")
        
        # Make request to Ollama
        response = ollama.chat(
            model=model,
            messages=messages,
            stream=stream,
            options={
                "temperature": temperature,
                "num_predict": max_tokens,  # Ollama uses num_predict instead of max_tokens
            }
        )
        
        # Handle streaming vs non-streaming
        if stream:
            # Return generator for streaming
            return _handle_stream(response)
        else:
            # Extract message content
            content = response.get("message", {}).get("content", "")
            
            if not content:
                logger.warning("Empty response from model")
                return "I apologize, but I couldn't generate a response. Please try again."
            
            logger.info(f"Received response: {content[:100]}...")
            return content
            
    except ollama.ResponseError as e:
        logger.error(f"Ollama response error: {e}")
        return f"Error: The model returned an error - {str(e)}"
    
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return (
            "Error: Cannot connect to Ollama. "
            "Please make sure Ollama is running (run 'ollama serve')."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error querying model: {e}", exc_info=True)
        return f"Error querying local model: {str(e)}"


def _handle_stream(response):
    """Handle streaming responses from Ollama"""
    for chunk in response:
        if "message" in chunk and "content" in chunk["message"]:
            yield chunk["message"]["content"]


def query_llm_with_history(
    prompt: str,
    conversation_history: list = None,
    model: str = "llama3.2",
    temperature: float = 0.7,
    system_message: str = None
) -> tuple:
    """
    Query LLM with conversation history for multi-turn conversations.
    
    Args:
        prompt: The user's current message
        conversation_history: List of previous messages
        model: Ollama model name
        temperature: Creativity level
        system_message: Custom system prompt
    
    Returns:
        tuple: (response_text, updated_history)
    """
    
    if system_message is None:
        system_message = (
            "You are an intelligent personal finance assistant. "
            "You analyze user income and expenses, then give clear insights and advice "
            "on saving, spending, or budgeting. Be concise and human-like."
        )
    
    # Initialize history if None
    if conversation_history is None:
        conversation_history = []
    
    # Build messages with history
    messages = [{"role": "system", "content": system_message}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            options={"temperature": temperature}
        )
        
        content = response.get("message", {}).get("content", "")
        
        # Update history
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": content})
        
        return content, conversation_history
        
    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        return f"Error: {str(e)}", conversation_history


# Example usage for different scenarios
if __name__ == "__main__":
    
    # Basic usage
    response = query_llm("I spent $500 this month on groceries. Is that too much?")
    print(f"Basic response: {response}\n")
    
    # With custom system message
    response = query_llm(
        "Analyze my spending pattern",
        system_message="You are a data analyst specializing in financial patterns."
    )
    print(f"Custom system: {response}\n")
    
    # With conversation history
    history = []
    response1, history = query_llm_with_history(
        "My monthly income is $5000",
        conversation_history=history
    )
    print(f"Turn 1: {response1}\n")
    
    response2, history = query_llm_with_history(
        "Should I save more?",
        conversation_history=history
    )
    print(f"Turn 2: {response2}\n")
    
    # Streaming example
    print("Streaming response:")
    for chunk in query_llm("Give me 3 budgeting tips", stream=True):
        print(chunk, end="", flush=True)
    print("\n")