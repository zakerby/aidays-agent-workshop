#!/bin/sh

# Shell script to set-up the environment for the project


# Parse command line arguments
while getopts "p:m:h" opt; do
  case ${opt} in
    h )
      echo "Usage: ./setup.sh"
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

# Run Ollama in a Docker container
docker run -d -v ollama:/root/.ollama -p $OLLAMA_PORT:11434 --name ollama ollama/ollama

# Ensure that the container is running
if ! [ "$(docker ps -q -f name=ollama)" ]; then
  echo 'Error: Ollama container is not running.' >&2
  exit 1
fi

# Ollama run model gemma:2b
docker exec -it ollama ollama run $LLM_MODEL