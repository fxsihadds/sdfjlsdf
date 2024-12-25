# Use the official Arch Linux base image
FROM archlinux:latest

# Set the working directory
WORKDIR /app

# Update system and install required dependencies
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm git curl base-devel p7zip && \
    pacman -Scc --noconfirm  # Clean up pacman cache to reduce image size

# Install a specific version of Python (e.g., 3.11.5)
RUN pacman -S --noconfirm python=3.11.5-1

# Check Python version (optional)
RUN python --version

# Copy the application code to the Docker image
ADD . /app

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 80
EXPOSE 80

# Command to run your Python application
CMD ["python", "bot.py"]
