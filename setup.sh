#!/bin/sh

# Shell script to set-up the environment for the project

# First ensure Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: Docker is not installed.' >&2
  exit 1
fi

# Run Ollama in a Docker container
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama