# Mercadona Web Scraping

This project is a web scraper built using Selenium and Python that extracts product information from the Mercadona website. The scraper collects product details such as description, technical attributes, price, and category, and stores this data in a structured format (JSON and Excel).

## Features

- **Extracts Product Information**: Extracts product details such as description, technical attributes, price, and category from the Mercadona website.
- **Exports Data**: The scraped data is saved in both a JSON file and an Excel file for further analysis.
- **WebDriver Integration**: Uses Selenium WebDriver to interact with the Mercadona website.
- **Configurable**: Uses a configuration file (`config.toml`) for postal code and ChromeDriver path settings.

## Requirements

- Python 3.x
- Selenium
- ChromeDriver (compatible with your version of Chrome)
- Pandas
- Toml

### Install Dependencies

To install the necessary libraries, run:

```bash
pip install selenium pandas toml openpyxl
```

## Setup

1. **Create a config.toml file**

In the project root, create a (`config.toml`) file with the following structure:

```toml
[settings]
codigo_postal = "12345"
driver_path = "path_to_your_chromedriver"
```
2. **Download ChromeDriver**

Ensure ChromeDriver is installed and matches your Chrome browser version. Download it from here https://developer.chrome.com/docs/chromedriver?hl=es-419.

3. **Folder Structure**

Your project folder should look like this:
```
project_root/
├── imgs/                  # Stores downloaded images
├── scripts/               # Python script files (optional)
├── config.toml            # Configuration file
├── main.py                # Main scraper script
└── requirements.txt       # Dependencies list
```

## Usage

1. **Run the scraper**

Once everything is set up, you can run the scraper by executing the following command:

```bash
python main.py
```

This will start the scraping process, and the product data will be saved in the following formats:

**products.json** (JSON format)
**products.xlsx** (Excel format)

2. **View the output**

The scraped data includes:

- Product description
- Technical attributes
- Price
- Categories (L1 and L2)
- Product URL
- Image paths (if applicable)