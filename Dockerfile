FROM python:3.10-slim

# Install ALL system dependencies needed for Blender 4.0 headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xz-utils \
    # X11 and rendering libs
    libx11-6 \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxrender1 \
    libgl1 \
    libglu1-mesa \
    # Audio (Blender needs these even headless)
    libopenal1 \
    libsndfile1 \
    # XKB - THE MISSING LIBRARY
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    # Other Blender deps
    libdbus-1-3 \
    libsm6 \
    libice6 \
    libxext6 \
    libxcursor1 \
    libxinerama1 \
    libxrandr2 \
    # Font support
    fontconfig \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Install Blender 4.0.2
WORKDIR /opt
RUN wget -q https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz \
    && tar -xf blender-4.0.2-linux-x64.tar.xz \
    && mv blender-4.0.2-linux-x64 blender \
    && rm blender-4.0.2-linux-x64.tar.xz

# Add Blender to PATH
ENV PATH="/opt/blender:${PATH}"

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /app/output

# Copy font to system fonts
RUN mkdir -p /usr/share/fonts/truetype && \
    cp /app/assets/fonts/Roboto-Bold.ttf /usr/share/fonts/truetype/ 2>/dev/null || true && \
    fc-cache -f -v

# Expose Streamlit port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "src/web/app.py", "--server.address=0.0.0.0"]
