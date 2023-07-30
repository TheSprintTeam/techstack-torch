# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container's working directory
COPY . .

# Expose the port that the Flask app will be running on (change this to match your Flask app)
EXPOSE 8080

# Define the command to run your Flask app
CMD ["python", "app.py"]
