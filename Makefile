# Makefile to run the containers & run the agent

# Run the containers
run-app:
	docker-compose up -d

get-ollama-model:
	docker compose exec -it ollama run gemma:2b

# Run the agent
run-agent:
	python agent/main.py