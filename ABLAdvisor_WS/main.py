#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#     CODE DEVELOPED BY      # 
#   Miguel Ant. Linares S.   #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import pandas as pd
from pathlib import Path
import time
from tqdm import tqdm

#Define the path and name of the result file
path = Path("ABL_Advisor_Deals_Data.csv")

#Function for scrapping the content from webpage 
def scrap_table(table):
    # Create a dictionary to store the scrapped data
    deal_info = {
        "date": [],
        "lender": [],
        "amount": [],
        "borrower": [],
        "industry": [],
        "structure": [],
        "description": [],
        "location": []
    }

    # First we find the rows with all the relevant info 
    rows = table.find_elements(By.TAG_NAME, 'tr')
    print(rows[1].text)
    first = True

    # Start going through every row scrapping the data
    for row in tqdm(rows):

        # Skip the row with the headers
        if first:
            first = False
            continue

        else:
            # From a row we find every cell and keep the value 
            cell = row.find_elements(By.TAG_NAME, 'td')
            deal_info['date'].append(cell[0].text)
            deal_info['lender'].append(cell[1].text)
            deal_info['amount'].append(cell[2].text)
            deal_info['borrower'].append(cell[3].text)
            deal_info['industry'].append(cell[4].text)
            deal_info['structure'].append(cell[5].text)

            # Find the url of the row that give us the other details that we need
            row_url = row.get_attribute('onclick')
            row_url = row_url.replace("window.location='", "")
            row_url = row_url.replace("';","")

            # Request the contents of that url
            page = requests.get(row_url)

            if page.status_code == 200:
                soup = BeautifulSoup(page.text, 'html.parser')
            else:
                continue
            
            # Find the table with the values and the rows
            detail_table = soup.find('table', attrs={'cellpadding': "4"})
            detail_rows = detail_table.find_all('tr')

            # Select the row where the Description is located and keep the value
            description = detail_rows[4].get_text()
            description = description.replace("Description", '').strip()
            deal_info['description'].append(description)
            
            # Try to look for the location value
            try:
                # Look for the location value in it's more common place
                location = detail_rows[6].get_text()

                # Make sure that we have the location value
                if "Location" in location:
                    location = location.replace("Location", "").strip()
                    # Keep the value found
                    deal_info['location'].append(location)
                else:
                    # Keep an empty value
                    deal_info['location'].append('')
            except:
                # If we couldn't, keep an empty value
                deal_info['location'].append('')
    
    # Make a dataframe out of the data in the dictionary and return it
    df_abl = pd.DataFrame(deal_info)
    return df_abl

# App function       
def main():
    #Open the web browser
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    #Navigate to the main webpage 
    main_page = "https://www.abladvisor.com/deal-tables"
    driver.get(main_page)

    # Look for the url for every quarter 
    quaters_table = driver.find_element(By.ID, 'ContentPlaceHolder1_dlDeals')
    quaters_elements = quaters_table.find_elements(By.CLASS_NAME, 'dealButtonBlue')
    # Store the routes in a list for iteration 
    routes = [element.get_attribute('href') for element in quaters_elements]
    first = True
    df_final = None

    for url in routes:
        # Navigate to the quater url
        driver.get(url)
        # Wait for the whole table to load
        time.sleep(5)
        # Look for the table with the data
        data_table = driver.find_element(By.ID, "ContentPlaceHolder1_gvDeals_ctl00")

        df_abl = scrap_table(data_table)
        if first:
            first = False
            df_final = df_abl.copy(deep=True)
        else:
            df_final = pd.concat([df_final, df_abl])
        
    df_final.to_csv(path, index=False)


if __name__ == "__main__":
    main()