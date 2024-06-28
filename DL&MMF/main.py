#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#     CODE DEVELOPED BY      # 
#   Miguel Ant. Linares S.   #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from dotenv.main import load_dotenv
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import time
import os

class Scrape():
    def __init__(self, user, pswd, url):
        self.user = user
        self.pswd = pswd
        self.url = url
    
    def login(self, driver):
        # get_started_btn = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/button")
        get_started_btn = WebDriverWait(driver, 10).until( 
            EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/button"))
        )
        get_started_btn.click()
        time.sleep(1)

        email_txt = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/div[1]/div/div[1]/form/div[1]/div/div[2]/div[1]/div/input")
        email_txt.send_keys(self.user)
        continue_email_btn = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/div[1]/div/div[1]/form/div[2]/button[2]")
        continue_email_btn.click()
        time.sleep(1)

        password_txt = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/div[1]/div/div[1]/form/div[2]/div/div[2]/div/div/span/input")
        password_txt.send_keys(self.pswd)
        # login_btn = driver.find_element(By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/div[1]/div/div[1]/form/div[3]/button[2]")
        login_btn = WebDriverWait(driver, 10).until( 
            EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/div[1]/div/div[1]/form/div[3]/button[2]"))
        )
        login_btn.click()
    
    def save_File(self, data, filename):
        path = Path(filename)
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)


    def scrape_fullAttendeeList(self):
        data = {
            "name": [],
            "last_name": [],
            "company": [],
            "job_title": []
        }
        #Load the Chromium Driver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.implicitly_wait(5)
        driver.maximize_window()
        driver.get(self.url)

        self.login(driver)
        while True:
            find_table = driver.find_element(By.XPATH, "/html/body/div/div/div/section/section/div/main/div/div[2]")
            find_table_rows = find_table.find_elements(By.CLASS_NAME, "e1iolry05")

            if len(data["name"]) > 0:

                find_table_rows = find_table_rows[len(data["name"]):]

            for element in find_table_rows:
                text = element.find_element(By.CLASS_NAME, "e1iolry03")
                names = text.find_element(By.CLASS_NAME, "e1iolry02").text
                names = names.split()

                try:
                    company = text.find_element(By.CLASS_NAME, "e1iolry01").text
                except:
                    company = 'n/a'
                
                try:
                    job_title = text.find_element(By.CLASS_NAME, "e1iolry00").text
                except:
                    job_title = 'n/a'

                data["name"].append(names[0])
                data["last_name"].append(names[1])
                data["company"].append(company)
                data["job_title"].append(job_title)
            
            try:
                load_more_btn = WebDriverWait(driver, 10).until( 
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/section/section/div/main/div/div[3]/button"))
                )
                load_more_btn.click()
                time.sleep(5)
            except:
                break
        filename = "FullAttendeeList.csv"
        
        self.save_File(data, filename)

    def scrape_ReadyToNetwork(self):

        data = {
            "name": [],
            "last_name": [],
            "company": [],
            "job_title": [],
            "introduction": [],
            "persona": [],
            "interests": [],
            "operates": [],
            "industry": [],
            "function": []
        }

        #Load the Chromium Driver
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.implicitly_wait(5)
        driver.maximize_window()
        driver.get(self.url)

        self.login(driver)

        readytoNetwork_btn = WebDriverWait(driver, 10).until( 
            EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/section/aside/div/div[1]/div[2]/div/ul/li[2]"))
        )
        readytoNetwork_btn.click()
        time.sleep(5)

        allreadytoNetwork_btn = WebDriverWait(driver, 10).until( 
            EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/section/section/div/main/header/div[1]/label[3]"))
        )
        allreadytoNetwork_btn.click()

        profile_id_list = []
        count = 0
        while True:
            count += 1
            print(count)
            find_table = driver.find_element(By.CLASS_NAME, "e4uvspw7")
            find_table_cards = find_table.find_elements(By.CLASS_NAME, "eud73668")

            for element in find_table_cards:
                profile_id = element.get_attribute("data-test")
                profile_id = profile_id.split('-')
                profile_id_list.append(profile_id[2])
            
            
            #i = 0
            routes = ["/html/body/div/div/div/section/section/div/main/div/ul/li[11]/button",
                      "/html/body/div/div/div/section/section/div/main/div/ul/li[9]/button", 
                      "/html/body/div/div/div/section/section/div/main/div/ul/li[10]/button"]
            for element in routes:
                try:
                    next_btn = driver.find_element(By.XPATH, element)
                    break
                except NoSuchElementException:
                    continue
            
            if next_btn.is_enabled():
                next_btn.click()
                time.sleep(2)
            else: 
                break
        
        for element in tqdm(profile_id_list):
            url = f"{os.getenv("URL2")}{element}"
            driver.get(url)
            time.sleep(3)

            try:
                names = driver.find_element(By.CLASS_NAME, "e1xzssbw2").text
                names = names.split()
                if len(names) > 2:
                    for i in range(2, len(names)):
                        names[1] = f"{names[1]} {names[i]}"
                    names = names[:2]
            except NoSuchElementException:
                continue

            try:
                job_title_company = driver.find_element(By.CLASS_NAME, "e1xzssbw1").text
                job_title_company = job_title_company.split('•')
                job_title = job_title_company[0]
                company = job_title_company[1]
            except NoSuchElementException:
                job_title = "n/a"
                company = "n/a"

            try:
                introduction = driver.find_element(By.CLASS_NAME, "ej6u1rk4").text
                introduction = introduction.encode("utf-8").decode("utf-8")
            except NoSuchElementException:
                introduction = "n/a"

            try:
                persona = driver.find_element(By.CLASS_NAME, "ej6u1rk2").text
            except:
                persona = "n/a"
            
            try:
                interests_tab = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div/div/section[2]/div/div[1]/div[1]/div/div[2]/div")
                interests_tab.click()
                
                interests_cards = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div/div/section[2]/div/div[2]/div/div[2]/div/section/ul")
                interests_rows = interests_cards.find_elements(By.CLASS_NAME, "e1lxdoct0")
                interests = ""

                for i in range(len(interests_rows)):
                    max_number = len(interests_rows)-1
                    if i == max_number:
                        interests += interests_rows[i].text
                    else:
                        interests += f"{interests_rows[i].text}, "
            except :
                interests = "n/a"
            
            introduction_tab = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div/div/section[2]/div/div[1]/div[1]/div/div[1]/div")
            introduction_tab.click()

            operates = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div/div/section[2]/div/div[2]/div/div/section/article/ul/li").text

            try:
                industry = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div/div/section[2]/div/div[2]/div/div/section/section[2]/section[1]/span").text
                function = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div/div/section[2]/div/div[2]/div/div/section/section[2]/section[2]/span").text
            except:
                industry = "n/a"
                function = "n/a"

            data["name"].append(names[0].strip())
            data["last_name"].append(names[1].strip())
            data["company"].append(company.strip())
            data["job_title"].append(job_title.strip())
            data["introduction"].append(introduction)
            data["persona"].append(persona)
            data["interests"].append(interests)
            data["operates"].append(operates)
            data["industry"].append(industry)
            data["function"].append(function)

        filename = "AllReadyToNetwork.csv"
        
        self.save_File(data, filename)







def main():
    load_dotenv()
    user = os.getenv("USER")
    pswd = os.getenv("PASSWORD")
    url = os.getenv("URL")

    scrape_class = Scrape(user, pswd, url)
    #scrape_class.scrape_fullAttendeeList()
    scrape_class.scrape_ReadyToNetwork()

if __name__ == "__main__":
    main()