# EZ Runner - Transformers Engine
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip3 install --no-cache-dir \
    torch==2.1.0 \
    transformers==4.35.0 \
    accelerate==0.24.0 \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0

# Download model at build time
ARG MODEL_ID={{ model_id }}
ENV MODEL_ID=${MODEL_ID}
ENV MODEL_PATH=/models/{{ model_name }}

RUN python3 -c "from transformers import AutoTokenizer, AutoModelForCausalLM; \
    tokenizer = AutoTokenizer.from_pretrained('${MODEL_ID}'); \
    tokenizer.save_pretrained('${MODEL_PATH}'); \
    model = AutoModelForCausalLM.from_pretrained('${MODEL_ID}'); \
    model.save_pretrained('${MODEL_PATH}')"

# Create inline server
RUN cat > /app/server.py << 'EOFSERVER'
import os
import argparse
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import uvicorn

app = FastAPI(title="EZ Runner - Transformers")

# Load model at startup
model_path = os.environ.get("MODEL_PATH", "/models")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

class ChatRequest(BaseModel):
    model: str
    messages: list
    max_tokens: int = 100
    temperature: float = 0.7

class ModelList(BaseModel):
    object: str = "list"
    data: list

@app.get("/v1/models")
def list_models():
    return ModelList(data=[{
        "id": os.environ.get("MODEL_ID", "model"),
        "object": "model",
        "created": 1234567890,
        "owned_by": "ezrunner"
    }])

@app.post("/v1/chat/completions")
def chat_completions(request: ChatRequest):
    # Extract user message
    messages = request.messages
    if not messages:
        return {"error": "No messages provided"}

    # Format prompt
    prompt = messages[-1]["content"] if messages else ""

    # Generate
    result = pipe(prompt, max_new_tokens=request.max_tokens, temperature=request.temperature)
    generated_text = result[0]["generated_text"]

    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": generated_text
            },
            "finish_reason": "stop"
        }]
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
EOFSERVER

# Expose port
EXPOSE {{ port }}

# Run server
CMD ["python3", "/app/server.py", "--port", "{{ port }}"]
