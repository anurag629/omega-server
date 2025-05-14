#!/bin/bash
set -e

# Stop the existing container if it's running
docker stop omega-manim || true
docker rm omega-manim || true

# Start a new container using docker-compose
cd "$(dirname "$0")"
docker-compose -f docker-compose.manim.yml up -d

# Wait for the container to start
echo "Waiting for Manim container to start..."
sleep 5

# Install additional packages
echo "Installing additional packages..."
docker exec omega-manim bash -c "pip install flask requests tqdm pydub"

echo "Manim container restarted and ready" 