# EPFO Website Scraper

## Overview

This project aims to scrape data from the EPFO (Employees' Provident Fund Organisation) website using Python Selenium. The script automates the process of searching for a company, solving the captcha, navigating through pages, and downloading Excel files containing payment details.

## Methodology

The script utilizes Selenium, a Python library for automating web browsers, to interact with the EPFO website. Here's a brief overview of the methodology used:

1. **Initialization**: The `epfs_scraper` class is initialized, setting up the download directory and the website URL.
2. **Scraping Page**: The `_scrapePage` method is responsible for scraping data from the EPFO website. It searches for the company, solves the captcha, navigates through multiple pages if necessary, and downloads the Excel files containing payment details.
3. **Downloading Files**: The `_downloadFile` method clicks on the "Excel" button to download the payment details file. It renames the downloaded file based on the establishment name.
4. **Renaming Files**: The `renameMostRecentFile` method renames the most recent file in the download directory using the establishment ID. This method is called after each file download if the rename variable is set `True`.
5. **Driver Function:** `scrape_data` is the main driver function that initiates the scraping process. It accepts the company name(s) as input and initiates the scraping process. If multiple company names are provided, it utilizes multithreading for concurrent scraping.

   **`rename` variable in `scrape_data`**
   The rename variable in the scrape_data function controls whether to rename the downloaded file(s). When set to True, it calls the renameMostRecentFile method to rename the most recent file in the download directory.
6. **Testing**: The `test_scrape_data` function tests the scraped data to ensure its correctness.

## Usage

To run the scraper:

1. Install Python 3.11 or higher.
2. Install the required dependencies using pip:

   ```bash
   $ pip install -r requirements.txt
   ```

   Note: Alternatively, you can use Poetry for managing dependencies. Install Poetry using the following command:

   ```bash
   $ pip install poetry
   ```

   Then, navigate to the project directory and run:

   ```bash
   $ poetry install
   ```
3. Set up the environment variables by creating a `.env` file with the following variables:

   - `DOWNLOAD_DIR`: Directory to save the downloaded files (default is "data/").
   - `SCRAPE_SITE`: URL of the EPFO website (default is "https://unifiedportal-epfo.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome").

     ```plaintext
     DOWNLOAD_DIR=<path_to_download_directory>
     SCRAPE_SITE=https://unifiedportal-epfo.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome
     ```
4. Run the `main()` function in `main.py`.

   ```bash
   $ python main.py
   ```

## Sample Usage

```python
from main import epfs_scraper

# Initialize scraper
scraper = epfs_scraper()

# Scrape data for a single company
scraper.scrape_data(company_name="MGH LOGISTICS PVT LTD")

# Scrape data for multiple companies
scraper.scrape_data(company_name=["Company1", "Company2"], rename = [False, True])

# Rename files without renaming
scraper.scrape_data(company_name="Company3", rename=False)
```
