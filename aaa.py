import os

# Path to your model folder
model_folder = r"C:\Users\prati\.ollama\models\phi3-local"

# Ensure folder exists
os.makedirs(model_folder, exist_ok=True)

# Path for the Modelfile
modelfile_path = os.path.join(model_folder, "Modelfile")

# Content of the Modelfile
content = """FROM ./blobs/phi3-mini.gguf
TEMPLATE "You are a helpful AI assistant. {{ .Prompt }}"
PARAMETER temperature 0.7
"""

# Write the file
with open(modelfile_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Modelfile created successfully at {modelfile_path}")
