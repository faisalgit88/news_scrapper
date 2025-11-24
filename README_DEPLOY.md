# Deployment Guide

## 🐳 Local Docker Deployment

You have successfully built and run the application using Docker!

**Access the App:**
Open your browser and go to: [http://localhost:8501](http://localhost:8501)

**Manage the Container:**
- **Stop:** `docker-compose down`
- **Start:** `docker-compose up -d`
- **View Logs:** `docker-compose logs -f`

---

## ☁️ Cloud Deployment Options

### Option 1: Streamlit Community Cloud (Easiest)
1.  Push your code to a GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Connect your GitHub account.
4.  Select your repository and the main file path (`src/app.py`).
5.  **Important:** In the "Advanced Settings", add the following to `packages.txt` (if asked, otherwise it reads `requirements.txt`):
    *   (Streamlit Cloud usually handles `requirements.txt` automatically)
    *   You might need to add a `packages.txt` file with `chromium` if Playwright fails, but the Python package often handles the binary download.
    *   *Note:* Streamlit Cloud has limited support for Playwright. If it fails, try Option 2.

### Option 2: Render / Railway (Docker Support)
Since you have a `Dockerfile`, this is a robust option.

**Render:**
1.  Create a new "Web Service".
2.  Connect your GitHub repo.
3.  Select "Docker" as the runtime.
4.  Render will automatically build and deploy using your `Dockerfile`.

**Railway:**
1.  Start a new project.
2.  Deploy from GitHub repo.
3.  Railway detects the `Dockerfile` and builds it.

### Option 3: VPS (DigitalOcean, AWS, etc.)
1.  SSH into your server.
2.  Clone your repo.
3.  Install Docker and Docker Compose.
4.  Run `docker-compose up -d --build`.
