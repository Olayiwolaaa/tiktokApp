from __future__ import print_function
import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import json, os, time
from tqdm import tqdm 

# Set up the Google Sheets API credentials
scope = ['https://www.googleapis.com/auth/spreadsheets']
path = (os.path.join(os.getcwd(), 'creds.json'))
creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
client = gspread.authorize(creds)

# Loop through each tag in the data
def update_google_sheet(sheet_id, file_name):
    # Load the data from the JSON file
    print(file_name)
    with open(file_name, 'r') as f:
        data = json.load(f)

    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.sheet1
    for tag, users in data.items():
        time.sleep(1)
        # Create a new sheet for the tag
        worksheet = sheet.add_worksheet(title=tag, rows=len(users)+1, cols=2)
        
        # Write the headers to the sheet
        worksheet.update_cell(1, 1, 'USERNAMES')
        worksheet.update_cell(1, 2, 'EMAILS')

        # Loop through each user in the tag's data
        row = 2
        for username, user_data in tqdm(users.items(), desc=f"Processing {tag}"):
            time.sleep(1)
            # Make the request and check the status code
            response = None
            while response is None:
                try:
                    response = worksheet.update_cell(row, 1, username)
                except gspread.exceptions.APIError as e:
                    if e.response.status_code == 429:
                        print("Quota exceeded. Sleeping for 30 seconds...")
                        time.sleep(30)
                    else:
                        raise e
            worksheet.update_cell(row, 2, user_data['email'])
            row += 1
