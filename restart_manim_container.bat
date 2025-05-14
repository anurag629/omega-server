@echo off
echo Stopping existing container if running...
docker stop omega-manim 2>nul || echo Container not running
docker rm omega-manim 2>nul || echo Container not existing

echo Starting new container...
cd /d "%~dp0"
docker-compose -f docker-compose.manim.yml up -d

echo Waiting for container to start...
timeout /t 5 /nobreak

echo Installing additional packages...
docker exec omega-manim bash -c "pip install flask requests tqdm pydub"

echo Manim container restarted and ready 