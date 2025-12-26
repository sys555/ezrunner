# EZ Runner - vLLM Engine
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

# Install Python
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

# Install vLLM
RUN pip3 install --no-cache-dir \
    vllm==0.2.2 \
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

# Expose port
EXPOSE {{ port }}

# Run vLLM server with OpenAI-compatible API
CMD python3 -m vllm.entrypoints.openai.api_server \
    --model "${MODEL_PATH}" \
    --host 0.0.0.0 \
    --port {{ port }}
