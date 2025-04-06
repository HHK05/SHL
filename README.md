# 📘 Configurable Web Scraper for Course Data

A flexible, configuration-driven web scraping pipeline built with Python. Designed to extract structured course information from educational websites and export clean, well-formatted JSON files.

---

## 🚀 Features

- ✅ **Configurable scraping via JSON**
- 🧩 **Modular architecture** (separated config, scraping, and orchestration)
- 🛠️ **Robust error handling** and logging
- 📤 **Clean JSON output** for downstream use
- 🌐 **Easily adaptable** to multiple domains

---

## 📂 Project Structure
├── app4.py # Main orchestration script
├──scrape2.py # Core scraping logic using BeautifulSoup 
├── app_config.json # Configuration file for target URLs, selectors, and fields 
├── shl_courses2.json # Output: structured course data 
├── requirements.txt # List of Python dependencies


---

## ⚙️ Configuration

The scraper behavior is fully controlled by the `app_config.json` file. It includes:

- Target base URL(s)
- CSS selectors or HTML tags for:
  - Titles
  - Links
  - Durations
  - Tags or categories
- Output formatting options

This allows you to customize the scraper for different sites without modifying the codebase.

---

## 🧪 How It Works

1. Load configuration from `app_config.json`
2. Fetch HTML content using `requests`
3. Parse and extract content using `BeautifulSoup`
4. Clean and format the data
5. Export to `shl_courses2.json`

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/course-scraper.git
cd course-scraper

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

##Usage
first run the scrap2 file then u eill get an JSON file which contains all the data, and then run the strealit filr byt using
python -m streamlit run app4.py

