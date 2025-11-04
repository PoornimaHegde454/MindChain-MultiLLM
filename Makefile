.PHONY: init run load-models run-backend run-frontend stop kill-ports

# Default target
.DEFAULT_GOAL := help

# Variables
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
BACKEND_PORT := 8000
FRONTEND_PORT := 1000
REDIS_PORT := 6379

# Initialize project: create venv, install dependencies, setup .env
init:
	@echo "🚀 Initializing MultiLLM project..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "📦 Creating virtual environment..."; \
		python3 -m venv $(VENV); \
	fi
	@echo "📥 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from env.example..."; \
		cp env.example .env; \
		echo "⚠️  Please edit .env with your API keys!"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "✅ Initialization complete!"

# Run both backend and frontend in separate threads
run:
	@echo "🚀 Starting MultiLLM servers in separate threads..."
	@$(PYTHON) run_servers.py

# Run backend server
run-backend:
	@echo "🚀 Starting backend server..."
	@$(PYTHON) main.py

# Run frontend server
run-frontend:
	@echo "🌐 Starting frontend server..."
	@cd frontend && $(PYTHON) server.py

# Load models configuration
load-models:
	@echo "📦 Loading models configuration..."
	@$(PYTHON) apply_working_models.py
	@echo "✅ Models loaded!"

# Stop all running servers (kills processes on backend and frontend ports)
stop:
	@echo "🛑 Stopping servers..."
	@-lsof -ti:$(BACKEND_PORT) | xargs kill -9 2>/dev/null || true
	@-lsof -ti:$(FRONTEND_PORT) | xargs kill -9 2>/dev/null || true
	@-lsof -ti:$(REDIS_PORT) | xargs kill -9 2>/dev/null || true
	@echo "✅ Servers stopped!"

# Kill all processes on application ports (backend, frontend, redis)
kill-ports:
	@echo "🔪 Killing processes on ports $(BACKEND_PORT), $(FRONTEND_PORT), and $(REDIS_PORT)..."
	@-for port in $(BACKEND_PORT) $(FRONTEND_PORT) $(REDIS_PORT); do \
		pid=$$(lsof -ti:$$port 2>/dev/null); \
		if [ ! -z "$$pid" ]; then \
			echo "   Killing process $$pid on port $$port"; \
			kill -9 $$pid 2>/dev/null || true; \
		else \
			echo "   Port $$port is already free"; \
		fi; \
	done
	@echo "✅ All ports checked and cleared!"

# Help target
help:
	@echo "MultiLLM Router - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  init         - Initialize project (venv, dependencies, .env)"
	@echo "  run          - Run both backend and frontend servers"
	@echo "  run-backend  - Run only backend server"
	@echo "  run-frontend - Run only frontend server"
	@echo "  load-models  - Load working models configuration"
	@echo "  stop         - Stop all running servers"
	@echo "  kill-ports   - Kill all processes on ports 8000, 1000, and 6379"
	@echo "  help         - Show this help message"

