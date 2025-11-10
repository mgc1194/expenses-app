"""
Configuration settings for the Expenses App.

This module centralizes all configuration settings for the application,
making it easier to manage and modify settings without changing code.
"""

import os

# File paths
DEFAULT_DATA_DIR = "./data"
DEFAULT_OUTPUT_DIR = "./output"
DEFAULT_CREDENTIALS_FILE = "expenses_credentials.json"

# Get configuration from environment variables with defaults
DATA_DIR = os.environ.get("EXPENSES_DATA_DIR", DEFAULT_DATA_DIR)
OUTPUT_DIR = os.environ.get("EXPENSES_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
CREDENTIALS_FILE = os.environ.get("EXPENSES_CREDENTIALS_FILE", DEFAULT_CREDENTIALS_FILE)

# Processing settings
CURRENT_YEAR = int(os.environ.get("EXPENSES_YEAR", "2025"))
SPREADSHEET_NAME = os.environ.get("EXPENSES_SPREADSHEET_NAME", "Copy of Expenses 2025")

# Google Sheets API scopes
GSHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# File pattern mappings for bank recognition
BANK_FILE_PATTERNS = {
    'capital_one': ['360Checking', '360PerformanceSavings', 'transaction_download'],
    'sofi': ['SOFI-Checking', 'SOFI-Savings'],
    'wells_fargo': ['WF-Checking', 'WF-Savings'],
    'amex': ['activity'],
    'chase': ['Chase'],
    'discover': ['Discover']
}
