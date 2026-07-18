# Use the official Microsoft Playwright image which includes all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.61.0-jammy

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/ ./backend/

# Set environment variables for the database and runtime
ENV PORT=8000
ENV HOST=0.0.0.0

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
