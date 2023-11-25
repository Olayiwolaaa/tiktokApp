from selenium import webdriver
from bs4 import BeautifulSoup
import time, json, re, requests, browser_cookie3
from tqdm import tqdm 

headers = {'Accept-Encoding': 'gzip, deflate, sdch',
           'Accept-Language': 'en-US,en;q=0.8',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive'}
cookies = browser_cookie3.load()
base_url = 'https://www.tiktok.com'
# this function scrapes usernames and links into the user_links.json file
def usernames_n_links(file_name, hashtags, data, number_of_scrolls=3):
    driver = webdriver.Chrome()
    for tag in tqdm(hashtags, desc="Processing hashtags"):
        try:
            # Go to the TikTok hashtag search page
            driver.get(f'{base_url}/tag/{tag}')

            # Scroll down x times
            for scroll_index in range(number_of_scrolls):
                # Scroll to the bottom of the page
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                # Wait for the page to load
                time.sleep(5)

            # Get the page source and parse it with Beautiful Soup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract users from the parsed HTML
            for user_link in soup.find_all('a', class_="css-nafpq5-StyledLink exdlci12"):
                user_href = user_link.get("href")
                user_profile_link = f'{base_url}{user_href}'
                username = user_link.get_text()
                # Check if the user_profile_link is already in the data dictionary
                # if any(user_profile_link in d.values() for d in data.values()):
                #     continue
                if tag not in data:
                    data[tag] = {}
                if username in data[tag]:
                    continue
                data[tag][username] = {}
                data[tag][username]['link'] = user_profile_link
            # Save data to file after processing each hashtag
            with open(file_name, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f'An error occurred while processing hashtag {tag}: {e}')
    driver.close()
   
# this function updates the users_data.json file and adds emails to account with it on their bio, otherwise it removes the user from the file
def emails(file_name, emails, data, num_datas_scraped=0, num_emails_found=0):
    # print number of users found per hashtags
    total_bio_left = 0
    for hashtag, users in data.items():
        print(f'Number of usernames found in {hashtag}: {len(users)}')
        total_bio_left += len(users)

    for hashtag in data:
        users = list(data[hashtag].keys())
        for user in users:
            if 'email' in data[hashtag][user]:
                continue
            try:
                res = requests.get(data[hashtag][user]["link"], headers=headers, cookies=cookies)
                soup = BeautifulSoup(res.content, 'html.parser')
                num_datas_scraped += 1

                # Extract the JSON data from the script tag
                json_script = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
                json_data = json_script.contents[0]
                # Load the JSON data using a different variable name
                json_parsed_data = json.loads(json_data)
                # Extract the "signature" from the JSON data
                signature = json_parsed_data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['user']['signature']
                # # Extract user bio from the parsed HTML
                if signature is None:
                    del data[hashtag][user]
                    continue

                # Extract the email using a regular expression
                email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                email_match = re.search(email_regex, signature)
                if email_match is not None:
                    num_emails_found += 1
                    emails.append(email_match.group())
                    print(f'Email found: {email_match.group()}')
                if email_match is None:
                    del data[hashtag][user]
                    continue
                num_datas_scraped += 1
                print(f'{len(emails)} emails found, {num_datas_scraped} bios scraped, {total_bio_left-num_datas_scraped} bios left, Total Number of bios : {total_bio_left}')

                data[hashtag][user]['email'] = email_match.group()
                with open(file_name, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                print(f'An error occurred while processing user {data[hashtag][user]["link"]}: {e}')

    # print number of users found per hashtags
    for hashtag, users in data.items():
        print(f'Number of usernames remaining in {hashtag}: {len(users)}')
