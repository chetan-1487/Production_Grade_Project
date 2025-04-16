# Use official Python base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application files to container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8002

# Command to start FastAPI server
CMD ["uvicorn", "app.app1:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]