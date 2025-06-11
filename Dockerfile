# Use an official Python image
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8080

# Run the app
CMD ["python3", "app.py"]