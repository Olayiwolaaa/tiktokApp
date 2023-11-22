# import lib.update_google_sheets as update_google_sheets, lib.scrape as scrape, json, os
import lib.scrape as scrape, json, os

# VARIABLES 
data = {}
hashtags = ['ugc', 'marketing', 'linkedIn', 'email', 'scaping']
file_name = f"{os.getcwd()}\data.json"
emails = []
number_of_scrolls = 10
sheet_id = '12-LQY1iQB6ZnyuqrWSAgmX2AU97O4aCasXbr5to4-TM'

# If file exists, load the data into data list, else: create an empty file
if os.path.isfile(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
else:
    with open(file_name, 'w') as f:
        json.dump(data, f)
    # SCRAPE USERNAMES and LINKS
    scrape.usernames_n_links(file_name, hashtags, data, number_of_scrolls)
    
# SCRAPE EMAILS
scrape.emails(file_name, emails,  data)

# SEND DATA.JSON TO GOOGLE SHEET (take out the comment below when the google sheet api is set)
# update_google_sheets.update_google_sheet(sheet_id,() file_name)