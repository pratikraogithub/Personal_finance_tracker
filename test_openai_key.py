# test_openai_key.py
import os
from dotenv import load_dotenv
import openai

def test_openai_key():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Make a simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello World' in a creative way"}
            ],
            max_tokens=50
        )
        
        answer = response.choices[0].message.content
        print(f"✅ API Key is working! Response: {answer}")
        
        # Check usage and limits
        print(f"✅ Model used: {response.model}")
        print(f"✅ Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except openai.AuthenticationError:
        print("❌ Authentication failed - Invalid API key")
        return False
    except openai.RateLimitError:
        print("❌ Rate limit exceeded - Key is valid but you've hit limits")
        return True  # Key is valid, just rate limited
    except openai.APIError as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_openai_key()