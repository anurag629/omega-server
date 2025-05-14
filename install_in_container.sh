#!/bin/bash
set -e

# This script installs additional packages in the container

# Install additional Python packages if needed
pip install flask requests tqdm pydub

echo "Installation completed successfully" 