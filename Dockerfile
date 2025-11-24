# Use the official Playwright image which includes browsers and dependencies
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only to save space/time if that's all we use)
# The base image might have them, but ensuring they are installed is good practice.
# Since we use 'sync_playwright().chromium.launch()', we need chromium.
RUN playwright install chromium

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
# We use the array form for CMD
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
