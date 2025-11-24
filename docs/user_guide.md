# User Guide: News Scraper & Analyzer

## 1. Installation

### Prerequisites
- Python 3.9 or higher
- Docker (Optional, for containerized deployment)

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd anti-grav
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

4. **Initialize the database**:
   The database will be automatically created on the first run. If you are upgrading, run the migration script:
   ```bash
   python scripts/migrate_category.py
   ```

## 2. Running the Application

### Using Python
Run the Streamlit app from the project root:
```bash
streamlit run src/app.py
```
The app will open in your default browser at `http://localhost:8501`.

### Using Docker
1. **Build the image**:
   ```bash
   docker build -t news-scraper .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8501:8501 news-scraper
   ```

## 3. Usage

### Adding a News Source
1. Open the sidebar on the left.
2. Expand the **"Add New Source"** section.
3. Enter the **Source Name** (e.g., "Hacker News") and **URL**.
4. (Optional) Enter a **Category** (e.g., "Tech").
5. If the site requires login, check **"Requires Login"** and fill in the credentials and CSS selectors.
6. Click **"Add Source"**.

### Managing Sources
1. In the sidebar, expand **"Manage Sources"**.
2. You can view all configured sources.
3. **Edit**: Update the Category or toggle "Include External Links".
4. **Delete**: Remove a source and its associated articles.

### Scraping News
1. In the sidebar, under **"Actions"**, click **"Run Scraper"**.
2. A status window will appear showing the progress for each source.
3. Once complete, the page will refresh to show the new articles.

### Viewing & Filtering
- **Dashboard**: The main view shows a list of articles sorted by date.
- **Filters**: Use the sidebar filters to narrow down results by:
  - **Source**
  - **Category**
  - **Sentiment**
  - **Date Range**
- **Analytics**: The right column displays statistics like Total Articles and Sentiment Distribution.
