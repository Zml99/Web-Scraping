#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#     CODE DEVELOPED BY      # 
#   Miguel Ant. Linares S.   #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import pandas as pd
from pathlib import Path

def get_mailto_links(card_list):
    """Gets a list of all mailto links on the current web page.

    Args:
    driver: A Selenium WebDriver object.

    Returns:
    A list of all mailto links on the current web page.
    """
    # Filter the list of links to only include mailto links.
    mailto_links = []

    for element in card_list:

        find_action_btns = element.find_element(By.CLASS_NAME, "p-0")

        # Get all of the links on the web page.
        links = find_action_btns.find_elements(By.TAG_NAME, 'a')
        if_mail = False

        for link in links:
            href = link.get_attribute('href')
            if href and href.startswith('mailto:'):
                if_mail = True
                href = href.replace('mailto:', '')
                mailto_links.append(href)
        
        if not if_mail:
            mailto_links.append(None)

    return mailto_links

#Function to get the general information of the person
def card_data_parse(driver):
    no_stop = True
    no_first = 1
    old_page_no = None
    new_page_no = None

    #We create a dictionary to store the data temporarily
    dic_card = {
        "name": [],
        "job_title": [],
        "corp": [],
        "address": [],
        "phone_no": [],
        "email":[]
    }

    while no_stop:
        if no_first != 1:
            new_page_no = driver.find_element(By.XPATH, "/html/body/form/main/div[2]/div/div/div/div[1]/div/div/div/div[3]/div[6]/div/nav/ul/li[3]/span")
            new_page_no = new_page_no.text
            if old_page_no == new_page_no:
                break
                
        else:
            old_page_no = driver.find_element(By.XPATH, "/html/body/form/main/div[2]/div/div/div/div[1]/div/div/div/div[3]/div[6]/div/nav/ul/li[3]/span")
            old_page_no = old_page_no.text
            no_first +=1
        
        print(new_page_no)

        #Find cards and emails
        card_list = driver.find_elements(By.CLASS_NAME, "contact-detail")
        mailto_links = get_mailto_links(card_list)
        for element in mailto_links:
            dic_card["email"].append(element)


        #Loop to get the data from all the cards
        for element in card_list:
            try:
                name = element.find_element(By.CLASS_NAME, "card-title")
                dic_card["name"].append(name.text)
            except:
                dic_card["name"].append(None)
            
            try:
                job_title = element.find_element(By.CLASS_NAME, "card-subtitle")
                dic_card["job_title"].append(job_title.text)
            except:
                dic_card["job_title"].append(None)
            
            try:
                corp = element.find_element(By.CLASS_NAME, "font-weight-bold")
                dic_card["corp"].append(corp.text)
            except:
                dic_card["corp"].append(None)

            try:
                address = element.find_element(By.CLASS_NAME, "sectionA")
                fix_address = str(address.text)
                fix_address = fix_address.replace('\n', ', ')
                dic_card["address"].append(fix_address)
            except:
                dic_card["address"].append(None)
            
            try:
                phone_no = element.find_element(By.CLASS_NAME, "sectionB")
                dic_card["phone_no"].append(phone_no.text)
            except:
                dic_card["phone_no"].append(None)
        
        print(pd.DataFrame(dic_card))

        old_page_no = new_page_no
        next_btn = driver.find_element(By.XPATH, "/html/body/form/main/div[2]/div/div/div/div[1]/div/div/div/div[3]/div[6]/div/nav/ul/li[4]/a")
        driver.execute_script("arguments[0].click();", next_btn)

    #We create the final dataframe with all the data
    df_card = pd.DataFrame(dic_card)

    #The function returns that dataframe
    return df_card

def main():
    #Web page URL
    URL = "https://my.turnaround.org/Directories/Members"

    #Load the Chromium Driver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.implicitly_wait(5)
    driver.maximize_window()
    driver.get(URL)
    driver.execute_script("document.body.style.zoom='70%'")

    #We search for the "search" button
    search_btn = driver.find_element(By.ID,"dnn_ctr635_Find_ctl00_btnSearch")

    # Click on the target element.
    driver.execute_script("arguments[0].click();", search_btn)

    # #Find cards and emails
    cards_info = card_data_parse(driver)

    path = Path("TMA_Members_Directory.xlsx")
    cards_info.to_excel(path, index=False)

    print("END!!!!!")

if __name__ == "__main__":
    main()