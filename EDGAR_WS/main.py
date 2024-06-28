#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#     CODE DEVELOPED BY      # 
#   Miguel Ant. Linares S.   #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from selenium import webdriver
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import requests
import json
import time

def get_ticker_information(ticker):
    
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

    ticker_information = requests.get(f"https://efts.sec.gov/LATEST/search-index?keysTyped={ticker}", headers=headers)

    response = ticker_information.content.decode()#["hits"]["hits"][0]["_source"]["entity"]
    entity_name = json.loads(response)["hits"]["hits"][0]["_source"]["entity"]
    
    return entity_name

class Consolidated_Schedule_Investments():
    def __init__(self, ticker, entity_name, url):
        self.ticker = ticker
        self.entity_name = entity_name
        self.url = url
    
    def save_File(self, data, filename):
        path = Path(filename)
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)
    
    def get_table_of_url(self, driver):

        urls = []

        table = driver.find_element(By.XPATH, '//*[@id="hits"]/table')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        
        for i in range(1, len(rows)):
            cell = driver.find_element(By.XPATH, f'//*[@id="hits"]/table/tbody/tr[{i}]/td[1]/a')
            data_adsh = cell.get_attribute('data-adsh')
            data_adsh = data_adsh.replace('-','')
            data_file_name = cell.get_attribute('data-file-name')

            url = f"https://www.sec.gov/Archives/edgar/data/{self.ticker}/{data_adsh}/{data_file_name}"
            urls.append(url)
        
        return urls

    
    # Function to extract the target table based on specific heuristics
    def extract_table(self, soup):
        tables = soup.find_all('table')
        candidate_tables = []

        for table in tables:
            # Heuristics to identify the correct table
            # Example: Select tables with more than 2 rows and 2 columns
            rows = table.find_all('tr')
            if len(rows) > 10:
                cols = rows[5].find_all(['td'])
                if len(cols) > 12:
                    candidate_tables.append(table)
        
        # If multiple tables match, refine selection logic
        if len(candidate_tables) > 1:
            # Example: Further refine based on specific row or column content
            choices = ["Co-Investments", "Primary Private Investment Funds", "Secondary Private Investment Funds"]
            for table in candidate_tables:
                if any(x in str(table) for x in choices):
                    continue
                else:
                    remove_idx = candidate_tables.index(table)
                    candidate_tables.pop(remove_idx)
            return candidate_tables  # Fallback to the first candidate

        return None
    
    def amg_pantheon_fund(self):
        data = {
            "type": [],
            "security": [],
            "initial_acquisition_date": [],
            "shares": [],
            "value": [],
            "percent_of_net_assets": []
        }

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.implicitly_wait(5)
        driver.maximize_window()
        driver.get(self.url)
        time.sleep(4)

        

        urls = self.get_table_of_url(driver)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
        r = requests.get(urls[0], headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        target_table = self.extract_table(soup)

        for table in target_table:
            if target_table:
                with open("EDGAR_WS/ouput.txt", "w", encoding="utf-8") as txt:
                    txt.write(f"\n----------------------------------------------------------------------------------\n{table.text}")
                # print(type(table))

        # for file in urls:

        #     driver.get(file)

        #     first_table = driver.find_element(By.XPATH, "/html/body/document/type/sequence/filename/description/text/table[120]")
        #     rows = first_table.find_elements(By.CSS_SELECTOR, 'tr[style*="page-break-inside:avoid"][style*="font-family:ARIAL"][style*="font-size:8pt"]')
        #     print(rows)

ticker = 1609211
entity = get_ticker_information(1609211)
url = f"https://www.sec.gov/edgar/search/#/category=custom&ciks=000{ticker}&entityName={entity}(CIK 000{ticker})&forms=N-CSR,N-CSRS"


Consolidated_Schedule_Investments(ticker, entity, url).amg_pantheon_fund()