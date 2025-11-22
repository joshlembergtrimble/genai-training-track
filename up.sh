#!/bin/bash

# Start the FastAPI backend
echo "Starting API server..."
uv run uvicorn my_api.my_agent_api:app --reload --port 8000 --host 0.0.0.0 &
API_PID=$!

# Start the Streamlit UI
echo "Starting UI server..."
uv run streamlit run my_ui/ui_main.py --server.port 8501 --server.address 0.0.0.0 &
UI_PID=$!

echo "API running on http://localhost:8000 (PID: $API_PID)"
echo "UI running on http://localhost:8501 (PID: $UI_PID)"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait

