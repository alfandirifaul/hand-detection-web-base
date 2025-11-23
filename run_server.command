#!/bin/bash

# Change to the project directory
cd "/Users/macbookpro/Documents/Project/hand-detection-web-base"

# Activate virtual environment
source "/Users/macbookpro/Documents/Project/hand-detection-web-base/venv/bin/activate"

# Open browser after a short delay (in background)
(sleep 3 && open "http://localhost:5050") &

# Start the server
python3 server.py