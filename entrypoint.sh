#!/bin/bash

echo 'Starting ollama server...'
ollama serve &

sleep 3

echo '⬇️ Pulling llama3.2... This may take a few minutes ⏳'
ollama pull llama3.2

echo '✅ Model llama3.2 is ready to use! Try running the app now: localhost:8501'

wait -n