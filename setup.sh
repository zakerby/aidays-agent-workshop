#!/bin/sh

# Shell script to set-up the environment for the project


# Parse command line arguments
while getopts "p:m:h" opt; do
  case ${opt} in
    h )
      echo "Usage: ./setup.sh"
      echo "Options:"
      echo "  -m  Model to run (default: gemma:2b)"
      echo "  -p  Port to run Ollama on (default: 11434)"
      echo "  -h  Display help"
      exit 0
      ;;
    m )
      echo "Model: $OPTARG"
      LLM_MODEL=$OPTARG
      ;;
    p )
      echo "Port: $OPTARG"
      OLLAMA_PORT=$OPTARG
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done

# If no model is specified, use the default model
if [ -z "$LLM_MODEL" ]; then
  LLM_MODEL="gemma:2b"
fi

# If no port is specified, use the default port
if [ -z "$OLLAMA_PORT" ]; then
  OLLAMA_PORT=11434
fi

# First ensure Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: Docker is not installed.' >&2
  exit 1
fi

# Check if the Ollama container is already running
if [ "$(docker ps -q -f name=ollama)" ]; then
  echo "Ollama container is already running."
else
  echo "Ollama container is not running."
  # Check if the Ollama container exists
  if [ "$(docker ps -aq -f name=ollama)" ]; then
    echo "Ollama container exists, but is not running, starting the container."
    # Start the Ollama container
    docker start ollama
  else
    echo "Ollama container does not exist, pulling the Ollama image and starting the container."
    # Pull the Ollama image
    docker pull ollama/ollama

    # Run Ollama in a Docker container
    docker run -d -v ollama:/root/.ollama -p $OLLAMA_PORT:11434 --name ollama ollama/ollama
  fi
fi

# Ollama run model gemma:2b
docker exec -d ollama ollama run $LLM_MODEL