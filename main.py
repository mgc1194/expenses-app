import calendar
import os
import pandas as pd
import logging
import gspread
import argparse
from google.oauth2.service_account import Credentials
from handlers.capital_one_handler import process as co_handler
from handlers.sofi_handler import process as sofi_handler
from handlers.amex_handler import process as amex_handler
from handlers.chase_handler import process as chase_handler
from handlers.wells_fargo_handler import process as wf_handler
from handlers.discover_handler import process as discover_handler
import config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_files(data_dir):
    """
    Read and process all CSV files from the specified directory.
    
    Args:
        data_dir (str): Directory path containing CSV files
        
    Returns:
        pd.DataFrame: Concatenated DataFrame of all processed transactions
    """
    all_transactions = []
    co_files = set(config.BANK_FILE_PATTERNS['capital_one'])
    sofi_files = set(config.BANK_FILE_PATTERNS['sofi'])
    wf_files = set(config.BANK_FILE_PATTERNS['wells_fargo'])
    amex_files = set(config.BANK_FILE_PATTERNS['amex'])
    chase_files = set(config.BANK_FILE_PATTERNS['chase'])
    discover_files = set(config.BANK_FILE_PATTERNS['discover'])
    
    if not os.path.exists(data_dir):
        logging.error(f'Data directory not found: {data_dir}')
        return pd.DataFrame()
    
    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        if file.lower().endswith('.csv'):
            # Process Capital One transactions
            if any(substring in file for substring in co_files):
                try:
                    all_transactions.append(co_handler(file_path))
                except Exception as e:
                    logging.error(f'Error processing {file}: {e}')
            # Process SoFi transactions
            elif any(substring in file for substring in sofi_files):
                try:
                    all_transactions.append(sofi_handler(file_path))
                except Exception as e:
                    logging.error(f'Error processing {file}: {e}')
            # Process Wells Fargo transactions
            elif any(substring in file for substring in wf_files):
                try:
                    all_transactions.append(wf_handler(file_path))
                except Exception as e:
                    logging.error(f'Error processing {file}: {e}')
            # Process Chase transactions
            elif any(substring in file for substring in chase_files):
                try:
                    all_transactions.append(chase_handler(file_path))
                except Exception as e:
                    logging.error(f'Error processing {file}: {e}')
            # Process Discover transactions
            elif any(substring in file for substring in discover_files):
                try:
                    all_transactions.append(discover_handler(file_path))
                except Exception as e:
                    logging.error(f'Error processing {file}: {e}')
            # Process Amex transactions
            elif any(substring in file for substring in amex_files):
                try:
                    all_transactions.append(amex_handler(file_path))
                except Exception as e:
                    logging.error(f'Error processing {file}: {e}')
            else:
                logging.error(f'Error reading {file}. Unrecognized file name')
        else:
            logging.error(f'Unsupported file format: {file}. Please provide a CSV file')

    if not all_transactions:
        logging.warning('No valid transactions found')
        return pd.DataFrame()

    return pd.concat(all_transactions).drop_duplicates()


def filter_transactions_by_date(transactions_df, target_month=None, target_year=None):
    """
    Filter transactions by month and/or year.
    
    Args:
        transactions_df (pd.DataFrame): DataFrame with transactions
        target_month (int, optional): Month number (1-12)
        target_year (int, optional): Year number
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    # Ensure 'Date' column is in datetime format
    transactions_df['Date'] = pd.to_datetime(transactions_df['Date'], errors='coerce')

    # Check for empty DataFrame
    if transactions_df.empty:
        logging.warning('No transactions to filter')
        return transactions_df

    if target_year:
        transactions_df = transactions_df[transactions_df['Date'].dt.year == target_year]

    if target_month:
        transactions_df = transactions_df[transactions_df['Date'].dt.month == target_month]

    return transactions_df


def export_monthly_csv(df, output_dir, target_month=None, target_year=None):
    # Create directory for the month if it doesn't exist
    month_name = calendar.month_name[target_month]
    # month_dir = os.path.join(output_dir, month_name)
    os.makedirs(output_dir, exist_ok=True)

    # Define the file path
    file_path = os.path.join(output_dir, f'transactions_{target_month:02d}.csv')
    month_data = filter_transactions_by_date(df, target_month, target_year)
    logging.info(f'Total transactions for {month_name}: {len(month_data)}')

    # Save the DataFrame to CSV
    month_data.to_csv(file_path, index=False)
    logging.info(f'Successfully saved data to {file_path}')


def export_to_csv(df, output_dir, target_month=None, target_year=None):
    """
    Export transactions to CSV file.
    
    Args:
        df (pd.DataFrame): DataFrame with transactions
        output_dir (str): Output directory path
        target_month (int, optional): Month number
        target_year (int, optional): Year number
    """
    # Create directory for the year if it doesn't exist
    if target_year:
        year_dir = os.path.join(output_dir, str(target_year))
        os.makedirs(year_dir, exist_ok=True)

        # Create directory for the month within the year directory if it doesn't exist
        if target_month:
            month_name = calendar.month_name[target_month]
            file_path = os.path.join(year_dir, f'transactions_{target_year}_{target_month:02d}.csv')
        else:
            file_path = os.path.join(year_dir, f'transactions_{target_year}.csv')
    else:
        # Only month is provided (without year)
        if target_month:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f'transactions_{target_month:02d}.csv')
        else:
            file_path = os.path.join(output_dir, 'transactions.csv')

    df.sort_values(by=['Account','Date'], inplace=True)
    # Save the DataFrame to CSV
    df.to_csv(file_path, index=False)
    logging.info(f'Successfully saved data to {file_path}')


def get_gspread_client(credentials_file=None):
    """
    Authenticate and return a gspread client with proper scopes.
    
    Args:
        credentials_file (str, optional): Path to credentials JSON file
        
    Returns:
        gspread.Client: Authenticated gspread client
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist
    """
    if credentials_file is None:
        credentials_file = config.CREDENTIALS_FILE
    
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
    
    creds = Credentials.from_service_account_file(credentials_file, scopes=config.GSHEETS_SCOPES)
    return gspread.authorize(creds)


def export_to_gsheet(df, spreadsheet_name, worksheet_name, credentials_file=None):
    """
    Exports DataFrame to a Google Sheets worksheet, appending data starting at row 4, column A.
    
    Args:
        df (pd.DataFrame): DataFrame with transactions
        spreadsheet_name (str): Name of the Google Spreadsheet
        worksheet_name (str): Name of the worksheet
        credentials_file (str, optional): Path to credentials JSON file
    """
    # Authenticate with Google Sheets
    try:
        client = get_gspread_client(credentials_file)
    except FileNotFoundError as e:
        logging.error(f"Google Sheets authentication failed: {e}")
        return
    except Exception as e:
        logging.error(f"Failed to authenticate with Google Sheets: {e}")
        return

    # Open the Google Sheet
    try:
        sheet = client.open(spreadsheet_name).worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        logging.error(f"Worksheet '{worksheet_name}' not found in '{spreadsheet_name}'.")
        return

    # Drop unwanted columns
    df.sort_values(by=['Date'], inplace=True)
    data = df.drop(columns=['ID', 'Label', 'Owner'], errors='ignore')

    # Convert Pandas Timestamp objects to strings
    data = data.applymap(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)
    # Define the starting cell (row 4, column A)
    start_row, start_col = 4, 1  # 'A4' is row 4, column 1 (A)

    # Convert dataframe to list of lists
    data_values = data.values.tolist()

    # Define the range to update dynamically
    end_row = start_row + len(data_values) - 1
    end_col = start_col + len(data.columns) - 1
    range_to_update = f"A{start_row}:{chr(64 + end_col)}{end_row}"
    # Update existing cells
    sheet.update(range_name=range_to_update, values=data_values)

    logging.info(f"Successfully exported {len(df)} transactions to '{worksheet_name}' in '{spreadsheet_name}'.")


def parse_arguments():
    """
    Parse command-line arguments for the application.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Process and consolidate financial transaction data from multiple banks.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process transactions for 2025
  python main.py --year 2025
  
  # Use custom data directory
  python main.py --data-dir /path/to/csv/files
  
  # Export only to CSV (skip Google Sheets)
  python main.py --no-gsheet
  
  # Use custom spreadsheet name
  python main.py --spreadsheet "My Expenses 2025"
        """
    )
    
    parser.add_argument(
        '--data-dir',
        default=config.DATA_DIR,
        help=f'Directory containing input CSV files (default: {config.DATA_DIR})'
    )
    
    parser.add_argument(
        '--output-dir',
        default=config.OUTPUT_DIR,
        help=f'Directory for output CSV files (default: {config.OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--year',
        type=int,
        default=config.CURRENT_YEAR,
        help=f'Year to process transactions for (default: {config.CURRENT_YEAR})'
    )
    
    parser.add_argument(
        '--credentials',
        default=config.CREDENTIALS_FILE,
        help=f'Path to Google Sheets credentials file (default: {config.CREDENTIALS_FILE})'
    )
    
    parser.add_argument(
        '--spreadsheet',
        default=config.SPREADSHEET_NAME,
        help=f'Google Spreadsheet name (default: {config.SPREADSHEET_NAME})'
    )
    
    parser.add_argument(
        '--no-gsheet',
        action='store_true',
        help='Skip exporting to Google Sheets (only export to CSV)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = parse_arguments()
    
    # Update logging level if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    source_path = args.data_dir
    output_path = args.output_dir
    current_year = args.year

    logging.info(f'Starting expense processing for year {current_year}')
    logging.info(f'Data directory: {source_path}')
    logging.info(f'Output directory: {output_path}')
    
    all_data = read_files(source_path)

    if not all_data.empty:
        for month in range(1, 13):
            month_name = calendar.month_name[month]
            filtered_data = filter_transactions_by_date(all_data, target_month=month, target_year=current_year)
            logging.info(f'Total transactions for {calendar.month_name[month]} {current_year}: {len(filtered_data)}')
            export_to_csv(filtered_data, output_path, target_month=month, target_year=current_year)
            
            # Only export to Google Sheets if not disabled
            if not args.no_gsheet:
                logging.info(f'Exporting {month_name} {current_year} to Google Sheets')
                export_to_gsheet(filtered_data, args.spreadsheet, month_name, args.credentials)
        
        logging.info('Processing complete!')
    else:
        logging.warning('No data to filter or export')

