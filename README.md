# Project Title: Boataround Testing Suite

## Description

This project consists of two main components:

1. **Data Scraper**: A Python script designed to scrape boat rental data from Boataround, focusing on listings in the city of Split for Saturday-to-Saturday bookings between May and September 2024.

2. **Automated Testing with Selenium**: A set of automated tests using Selenium WebDriver to validate the functionality of the Boataround website. This includes navigation, search functionality, date selection, and reservation processes.

## Getting Started

### Dependencies

- Python 3.11
- Libraries: `aiohttp`, `pandas`, `selenium`, `unittest`
- Chrome WebDriver (for Selenium tests)
- An internet connection to access the Boataround website.

### Installing

- Clone the repository to your local machine.
- Ensure Python 3.11 is installed.
- Install required Python libraries by running `pip install -r requirements.txt` in the project directory.

### Executing Program

#### Data Scraper

1. Navigate to the `data_scraper` directory.
2. Run the script: `python task1.py`
3. The output will be an Excel file containing the scraped data.

#### Automated Testing

1. Navigate to the `automated_tests` directory.
2. Run the tests: `python -m unittest task2.py`
3. Observe the output in the console for test results.

## Features

### Data Scraper

- Scrapes boat rental data from the API.
- Filters data based on location and date range.
- Exports data to an Excel file.

### Automated Testing

- Navigates to the Boataround homepage and verifies its load.
- Searches for boats based on specified criteria.
- Validates functionality of date selection and reservation process.
- Ensures correct handling of different web elements and scenarios.

## Testing

- The data scraper has been tested to ensure accurate data extraction.
- Automated tests cover key user journey aspects on the Boataround website.


## Authors

Sabeel
