# Use the official Playwright image which includes browsers and dependencies
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Ensure browsers install into writable path
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Set working directory
WORKDIR /app

# Install system dependencies (fonts for PDF/Playwright)
RUN apt-get update && apt-get install -y fonts-liberation && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only)
RUN playwright install chromium

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
