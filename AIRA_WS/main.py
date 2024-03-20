#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#     CODE DEVELOPED BY      # 
#   Miguel Ant. Linares S.   #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import pandas as pd
from pathlib import Path
from tqdm import tqdm

path = Path("AIRA_Members_Directory.xlsx")
writer = pd.ExcelWriter(path, engine = 'openpyxl')

def parse_info(cards):
    # Create a dictionary to store the parsed contact information.
    contact_info = {
        "name": [],
        "corp": [],
        "address": [],
        "email": []
    }

    for element in tqdm(cards):
        # Extract text and check for <em> tag indicating a corporation
        text = element.text.replace("\nContact", "")
        if_corp = element.find_elements(By.TAG_NAME, 'em')

        # Split the text string into lines
        lines = text.split('\n')

        # Extract the name and corporation from the first two lines
        contact_info["name"].append(lines[0])

        if if_corp:
            contact_info["corp"].append(lines[1])
        else:
            contact_info["corp"].append(None)

        # Extract the address from the remaining lines
        if if_corp:
            address = ', '.join(lines[2:])
        else:
            address = ', '.join(lines[1:])
        contact_info['address'].append(address)

        # Extract email
        find_email = element.find_element(By.TAG_NAME, 'a')
        email = find_email.get_attribute('href').replace("mailto:", "")
        contact_info['email'].append(email)

    df_aira = pd.DataFrame(contact_info)
    return df_aira

def main():
    locations = ["USA", "Canada", "United+States", "United+Kingdom"]

    #Load the Chromium Driver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.implicitly_wait(5)
    driver.maximize_window()
    for location in locations:
        URL = f"https://aira.org/directories/search/Membership?q={location}&w=country"
        driver.get(URL)

        cards = driver.find_elements(By.CLASS_NAME, "member")
        df_aira = parse_info(cards)
        df_aira.to_excel(writer, sheet_name=location, index=False)

    writer.close()

if __name__ == "__name__":
    main()