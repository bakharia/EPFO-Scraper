'''
Use Python Selenium to scrape data from the EPFO website. Make sure to use the Chrome driver.
Make sure to verify your requirements.txt file before submitting your code. You can use Python 3.11>= for this coding challenge.

Fill out the sections where TODO is written.
Ideally your code should work simply by running the main.py file.

This is a sample file to get you started. Feel free to add any other functions, classes, etc. as you see fit.
This coding challenge is designed to test your ability to write python code and your familiarity with the Selenium library.
This coding challenge is designed to take 2-4 hours and is representative of the kind of work you will be doing at the company daily.
'''

# Importing the required libraries
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
from io import BytesIO
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from fake_useragent import UserAgent
from dataclasses import dataclass
from datetime import datetime
import easyocr
from concurrent.futures import ThreadPoolExecutor


DOWNLOAD_DIR= ""


@dataclass
class scrapped_data:
    '''
    Dataclass to define the structure of scrapped data.
    '''
    TRRN: int
    DoC: datetime
    Amount: int
    WageMonth: str
    NoEmp: int
    ECR: str


class epfs_scraper: 
    '''
    Class for scraping data from the EPFO website.
    '''

    def __init__(self) -> None:
        '''
        Constructor method to initialize EPFS scraper object. Initializing required variables from the environment file.
        
        Input:
            None
        
        Output:
            None
        '''
        load_dotenv()        
        self.__DOWNLOAD_DIR= os.getenv(key= "DOWNLOAD_DIR", default="data/")
        self.__scrape_site= os.getenv(key= "SCRAPE_SITE", default="https://unifiedportal-epfo.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome")

        if not os.path.exists(self.__DOWNLOAD_DIR):
            os.makedirs(self.__DOWNLOAD_DIR)

    def _genRandomUserAgent(self) -> str:
        """
        Generates a random user agent using the fake_useragent library.
        
        Output:
            str: Random user agent string.
        """
        return UserAgent().random
    
    def _lookupCompany(
      self,
      company_name: str,
      driver: webdriver.Chrome,
      retry: bool = False  
    ) -> webdriver.Chrome:
        """
         Method to perform company lookup.
        
        Input:
            company_name (str): The name of the company to lookup.
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            retry (bool): Flag to check if the function is being retried.
        
        Output:
            webdriver.Chrome: The Selenium WebDriver instance.
        """
        # Initiliaze ocr reader
        reader = easyocr.Reader(lang_list=['en'])

        if retry is False:

            # Enter company name
            driver.find_element(
                by= By.NAME, 
                value= "estName"
            ).send_keys(
                company_name
            )
        
        # Solve captcha
        imgSrc= driver.find_element(
            by= By.ID,
            value= "capImg"
        ).screenshot_as_png

        # Save the screenshot to a file
        with open("captcha_screenshot.png", "wb") as file:
            file.write(imgSrc)

        captchaImg= Image.open(
            fp= BytesIO(
                initial_bytes= imgSrc
            )
        )

        # print(captchaImg)

        # Extract text from captcha img
        captchaImgText= reader.readtext(
            image= np.array(captchaImg),
            paragraph= True,
            min_size= 6,
            contrast_ths= 0.1
        )[0][1]

        captchaImgText = "".join(captchaImgText.split(' ')).upper()

        captchaImgText = captchaImgText.replace('$', 'S')
        captchaImgText = captchaImgText.replace('€', 'E')

        # Enter the extracted captcha text
        driver.find_element(
            by= By.NAME,
            value= "captcha"
        ).send_keys(
            captchaImgText
        )
    
        # Click on Search
        driver.find_element(
            by= By.NAME,
            value= "Search"
        ).click()

        time.sleep(10)

        return driver

    def _checkInvalidCaptcha(
            self,
            driver: webdriver.Chrome,
            company_name: str
    ) -> webdriver.Chrome:
        """
        Method to check if the entered captcha is valid.
        
        Input:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            company_name (str): The name of the company.
        
        Output:
            webdriver.Chrome: The Selenium WebDriver instance.
        """
        
        try:
            # Check if captcha entered was valid

            invalid_captcha = driver.find_element(
                    by= By.XPATH,
                    value="//*[contains(text(), 'Please enter valid captcha.')]"
                )

            while invalid_captcha:

                print(invalid_captcha.text, "\n Retrying...")

                driver = self._lookupCompany(
                    company_name= company_name,
                    driver= driver,
                    retry = True
                )

                invalid_captcha = driver.find_element(
                    by= By.XPATH,
                    value="//*[contains(text(), 'Please enter valid captcha.')]"
                )
        
        except NoSuchElementException:
            pass
        
        print("Passed Captcha")

        time.sleep(8)

        return driver

    def _findElement(
            self,
            driver:webdriver.Chrome
    ) -> webdriver.Chrome:
        """
        Method to find and click an element.
        
        Input:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
        
        Output:
            webdriver.Chrome: The Selenium WebDriver instance.
        """
        try: 
            driver.find_element(
                by= By.XPATH,
                value= '//*[@id="tablecontainer3"]/div/a'
            ).click()
        except ElementClickInterceptedException:
            driver.execute_script(
                "arguments[0].click",
                driver.find_element(
                    by= By.XPATH,
                    value= '//*[@id="tablecontainer3"]/div/a'
                )
            )
        
        time.sleep(10)

        return driver
    
    def renameMostRecentFile(
            self,
            new_name: str,
            directory: str,
            dataClass: scrapped_data = scrapped_data
        ):
        """
        Method to rename the most recent file in the specified directory.
        
        Input:
            new_name (str): The new name for the file.
            directory (str): The directory where the file is located.
            dataClass (scrapped_data, optional): The data class structure. Defaults to scrapped_data.
        
        Output:
            None
        """
        try:
            # Get list of files in the directory sorted by creation time
            files = sorted(os.listdir(directory), key=lambda x: os.path.getctime(os.path.join(directory, x)))
            
            if files:  # Check if there are any files in the directory
                most_recent_file = files[-1]  # Get the most recent file
                old_path = os.path.join(directory, most_recent_file)
                new_path = os.path.join(directory, f'{new_name}.xlsx')
                
                os.rename(old_path, new_path)
                print(f"File '{most_recent_file}' renamed to '{new_name}.xlsx' successfully.")

            else:
                print(f"No files found in directory '{directory}'.")
        except FileNotFoundError:
            print(f"Error: Directory '{directory}' not found.")
        except FileExistsError:
            print(f"Error: File '{new_name}' already exists.")

    def _downloadFile(
            self,
            driver: webdriver.Chrome,
            rename: bool= True
    ) -> webdriver.Chrome:
        """
        Method to download a file.
        
        Input:
            driver (webdriver.Chrome): The Selenium WebDriver instance.
            rename (bool, optional): Whether to rename the downloaded file. Defaults to True.
        
        Output:
            webdriver.Chrome: The Selenium WebDriver instance.
        """
        
        # Find Details
        details = driver.find_elements(
            by= By.XPATH,
            value= '//*[@id="example"]/tbody/tr/td[5]/a[1]'
        )

        # Establishment Name
        est_name = driver.find_elements(
            by= By.XPATH,
            value= '//*[@id="example"]/tbody/tr/td[1]'
        )
        
        for i, detail in enumerate(details[0:3:10]):
            
            if i > 0:
                print("Closed previous tab")

            try:
                detail.click()
            except ElementClickInterceptedException:
                print("ElementClickInterceptedException: Element is not clickable, Retrying!")
                time.sleep(7)
                element = driver.find_element(By.XPATH, f'//*[@id="example"]/tbody/tr[{i+1}]/td[5]/a[1]')
                driver.execute_script("arguments[0].click;", element)
                print("Success!")
            
            print(est_name[i].text)
            download_filename = est_name[i].text

            time.sleep(10)

            print("Find element")
            
            driver = self._findElement(driver)

            # Get handles of all currently open windows/tabs
            all_handles = driver.window_handles

            # print(all_handles)

            # Retry if new window didn't open
            while len(all_handles) == 1:

                driver = self._findElement(driver)

                # Get handles of all currently open windows/tabs
                all_handles = driver.window_handles


            # Switch to the newly opened window/tab
            new_window_handle = [handle for handle in all_handles if handle != driver.current_window_handle][0]
            driver.switch_to.window(new_window_handle)

            time.sleep(5)

            # print(driver.page_source)

            try:

                excel_file = driver.find_element(
                    by= By.CSS_SELECTOR,
                    value= "#table_pop_up_wrapper > div.dt-buttons > a"
                )
                excel_file.click()
                if rename:
                    self.renameMostRecentFile(new_name= download_filename, directory= self.__DOWNLOAD_DIR)

            except NoSuchElementException:
                print("Record doesn't exist!")

            # Close the newly opened window/tab
            driver.close()

            # Switch back to the original window/tab
            driver.switch_to.window(driver.window_handles[0])
            print("switched to main window")
            time.sleep(10)

        return driver

    def _scrapePage(
            self, 
            company_name: str,
            rename: bool = True,
        ):
        """
        Method to scrape data from the current EPFO page.
        
        Input:
            company_name (str): The name of the company to scrape data for.
            rename (bool, optional): Whether to rename the downloaded file. Defaults to True.
        
        Output:
            None
        """

        # Set download directory
        prefs = {
            "download.default_directory": os.path.join(os.getcwd(), self.__DOWNLOAD_DIR),
        }
        options= Options()
        options.add_argument(f"user-agent={self._genRandomUserAgent()}")
        options.add_experimental_option("prefs", prefs)

        driver= webdriver.Chrome(
            options= options
        )

        driver.get(self.__scrape_site)
        time.sleep(5)

        driver = self._lookupCompany(
            company_name= company_name,
            driver= driver
        )
        
        driver = self._checkInvalidCaptcha(
            driver= driver,
            company_name= company_name
        )

        
        try: 
            page_text = driver.find_element(
                by= By.XPATH,
                value= '//*[@id="example_info"]'
            )
            print("####################")
            print(page_text.text)

            
            current_page, total_pages = page_text.text.split('of')
            current_page = int(current_page.strip().split(' ')[-1])
            total_pages = int(total_pages.strip())

            while current_page <= total_pages:
                              
                driver = self._downloadFile(driver= driver, rename= rename)

                time.sleep(5)
            
                driver.find_element(
                        by= By.XPATH,
                        value= '//*[@id="example_next"]'
                ).click()
                
                current_page += 1
                time.sleep(5)
        except NoSuchElementException:
            print(f"Records for {company_name} don't exist")
        driver.quit()
    
    def scrape_data(
            self, 
            company_name: str|list,
            rename: bool|list = True
        ) -> None:
        """
        Method to scrape data from the EPFO website.
        
        Input:
            company_name (str|list): The name of the company or a list of company names to scrape data for.
            rename (bool|list, optional): Whether to rename the downloaded file(s). Defaults to True.
        
        Output:
            None
        """
        
        if isinstance(company_name, str):
            print("string", company_name)
            self._scrapePage(company_name, rename)

        elif isinstance(company_name, list):
            print("list", company_name)

            with ThreadPoolExecutor(max_workers= 5) as executor:
                executor.map(self._scrapePage, company_name, rename)


def test_scrape_data():
    '''
    Test the scraped data
    '''
    # Convert xlsx file to csv due to some issues with pandas
    from xlsx2csv import Xlsx2csv
    Xlsx2csv("data/Payment Details.xlsx", outputencoding="utf-8").convert("payment_details.csv")

    df= pd.read_csv("payment_details.csv")

    assert set(df.columns) == set(['TRRN', 'Date Of Credit', 'Amount', 'Wage Month', 'No. of Employee', 'ECR'])
    assert df['TRRN'].loc[0] == 3171702000767
    assert df['Date Of Credit'].loc[0] == '03-FEB-2017 14:35:15'
    assert df['Amount'].loc[0] == 334901
    assert df['Wage Month'].loc[0] == 'DEC-16'
    assert df['No. of Employee'].loc[0] == 83
    assert df['ECR'].loc[0] == 'YES'
    print("All tests passed!")

def main():

    # scrape_data("MGH LOGISTICS PVT LTD")

    # epfs_scraper().scrape_data(company_name="MGH LOGISTICS PVT LTD", rename = False)
    # epfs_scraper().scrape_data(company_name="MGH LOGISTICS PVT LTD")
    # epfs_scraper().scrape_data(company_name="EMPIRE")
    # epfs_scraper().scrape_data(company_name=["EMPIRE", "shufasfsa", "asfhusahf"])
    epfs_scraper().scrape_data(company_name=["MGH LOGISTICS PVT LTD", "MGH LOGISTICS PVT LTD"], rename= [False, True])
    # epfs_scraper().renameMostRecentFile(new_name= "KDMAL0094547000", directory="data/")

    test_scrape_data()


if __name__ == "__main__":
    main()