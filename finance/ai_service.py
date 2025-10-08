import subprocess
import json

def query_llm(prompt):
    """
    Query the local Ollama model (phi3-local) and return the response.
    Works on Windows even if Ollama is installed as a UWP app.
    """
    try:
        # Call Ollama via PowerShell to avoid WinError 2
        result = subprocess.run(
            ["powershell", "-Command", "ollama run phi3-local --json"],
            input=prompt.encode("utf-8"),
            capture_output=True
        )

        # Decode stdout
        stdout = result.stdout.decode("utf-8").strip()

        # Parse JSON output
        data = json.loads(stdout)
        return data.get("response", "No response from model.")

    except json.JSONDecodeError:
        # If the model output is not valid JSON
        return f"Error: Could not parse model response:\n{stdout}"
    except FileNotFoundError:
        return "Error: Ollama command not found. Make sure Ollama is installed and accessible."
    except Exception as e:
        return f"Error querying model: {e}"
