FROM manimcommunity/manim:stable

# Make sure to use root user for installations
USER root

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    libcairo2-dev \
    libpango1.0-dev \
    python3-pip \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install additional Python packages
RUN pip3 install --no-cache-dir \
    ipython \
    jupyter \
    notebook \
    tqdm \
    pydub

# Create directories for mounting
RUN mkdir -p /manim/omega /manim/media /manim/omega/scripts
WORKDIR /manim

# Copy the installation script
COPY install_in_container.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install_in_container.sh

# Add manim to PATH and ensure it's in the PATH when using docker exec
ENV PATH="/opt/conda/bin:${PATH}"
RUN echo 'export PATH="/opt/conda/bin:$PATH"' >> /etc/bash.bashrc

# Create a simple wrapper for manim command
RUN echo '#!/bin/bash\n\
export PATH="/opt/conda/bin:$PATH"\n\
cd /manim\n\
manim "$@"' > /usr/local/bin/manim-wrapper && \
    chmod +x /usr/local/bin/manim-wrapper

# Make sure media directory is writable
RUN chmod -R 777 /manim/media /manim/omega

# Keep the container running
CMD ["tail", "-f", "/dev/null"] 