#!/bin/bash
set -e

# Start Ollama in the background
ollama serve &

# Start the API right away, in the background — this is what satisfies
# Cloud Run's startup check quickly, before the slow model prep even begins
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} &
API_PID=$!

# Now do the slow part: wait for Ollama, then download and register the model
until curl -s http://localhost:11434 >/dev/null; do
  echo "Waiting for Ollama to start..."
  sleep 1
done

python -u download_model.py || echo "MODEL DOWNLOAD FAILED"
ollama create incident-slm -f /app/models/Modelfile || echo "OLLAMA CREATE FAILED"
echo "Model setup step finished (check above for failures)"

# Keep the container alive by waiting on the API process
wait $API_PID