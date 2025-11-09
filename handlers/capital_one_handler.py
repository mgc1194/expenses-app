import os
import logging
from capital_one.savings import process as co_savings
from capital_one.checking import process as co_checking
from capital_one.quicksilver import process as quicksilver

# Setup logging
logging.basicConfig(level=logging.INFO)


def process(file_path):
    try:
        logging.info(f'Starting to process the file: {file_path}')
        processed_data = __handle_files(file_path)
        if processed_data is not None:
            logging.info(f'File processed successfully: {file_path}')
        return processed_data
    except FileNotFoundError as e:
        logging.error(f'File not found: {e}')
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')


def __handle_files(file_path):
    try:
        file_name = os.path.basename(file_path)

        # Check if the file extension is .csv
        if not file_name.lower().endswith('.csv'):
            logging.error(f'The file {file_name} is not a CSV file')
            return

        if '360Checking' in file_name:
            return co_checking(file_path)
        elif '360PerformanceSavings' in file_name:
            return co_savings(file_path)
        elif 'transaction_download' in file_name:
            return quicksilver(file_path)
        else:
            logging.error(f'The file {file_name} is not a recognized Capital One CSV')
    except Exception as e:
        logging.error(f'Error handling file: {e}')
        raise


# Example usage
if __name__ == "__main__":
    processed_df = process('path_to_your_file.csv')
    if processed_df is not None:
        print(processed_df.head())
