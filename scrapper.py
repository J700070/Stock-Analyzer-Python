from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from aux_functions import *

def get_stock_basic_data(ticker):

    url = "https://roic.ai/company/"+ ticker
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    browser = webdriver.Chrome(options=options)
    browser.get(url)
    time.sleep(2)

    # Comprobamos que la dirección es la adecuada, en otro caso se trata de un error
    if browser.current_url == "https://roic.ai/404":
        # errores.append(ticker)
        browser.close()
        browser.quit()
        return
    try:
        name = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[1]/div[2]/div[2]/h1')[0].text
        currency = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[1]/div[3]/div[1]/div[1]/div[1]')[0].text
        sector = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/div[1]/div[1]/div[2]')[0].text
        industry = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div[2]')[0].text
        country = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[1]/div[1]/span')[0].text.split()[0]
        ipo = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[2]/div[2]/div[1]/div/div[2]/div[3]/div[1]/div[2]')[0].text
        insider = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[5]/div[3]')[0].text
        institution = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[6]/div[3]')[0].text
        summary = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[2]/div[2]/div[1]/div/div[3]')[0].text
        div_yield = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[1]/div[3]/div[3]/div[5]/span[1]')[0].text
        capex_per_share = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[7]')[0].text.split("\n")[-1]
        exchange = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[2]/div[1]/div[2]/div[2]/span/span[2]')[0].text
        eps = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[4]')[0].text.split("\n")[-1]
        revenue_per_share = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[3]')[0].text.split("\n")[-1]
        
        fcf_per_share = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[5]')[0].text.split("\n")[-1]
        div_per_share = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[6]')[0].text.split("\n")[-1]
        return_1_year_stock = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[13]/div/div[5]')[0].text
        return_1_year_sp500 = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[13]/div/div[6]')[0].text
        return_3_years_stock = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[13]/div/div[8]')[0].text
        return_3_years_sp500 = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[13]/div/div[9]')[0].text
        return_5_years_stock = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[13]/div/div[11]')[0].text
        return_5_years_sp500 = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div[1]/div/div[1]/div[1]/div[13]/div/div[12]')[0].text
    except:
        browser.close()
        browser.quit()
        return

    data = [name, currency, sector, industry, country, ipo, insider, institution, summary, div_yield, exchange, eps, div_per_share,
            return_5_years_stock, return_5_years_sp500, return_3_years_stock, return_3_years_sp500, return_1_year_stock, return_1_year_sp500,
            revenue_per_share, fcf_per_share, capex_per_share]

    # Creamos un dataframe con los datos la tabla
    index = ["Name", "Currency", "Sector", "Industry", "Country", "IPO","Insider Percentage", "Institution Percentage", "Summary", "Dividend Yield", "Exchange", "EPS",
            "Dividend per Share", "Return 5 Years Stock", "Return 5 Years S&P 500", "Return 3 Years Stock", "Return 3 Years S&P 500", "Return 1 Year Stock", "Return 1 Year S&P 500",
            "Revenue per Share", "FCF per Share", "Capex per Share"]

    df = pd.DataFrame(data, columns=["Information"],index = index)
    print(df.head(10))

    
    browser.close()
    browser.quit()

    return df



def get_stock_fundamental_data(ticker,reconstruct_df=True):

    url = "https://roic.ai/financials/" + ticker
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    
    time.sleep(1)
    
    cols = browser.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[3]/div/div/div/div[3]/div/div[2]')[0].text.split("\n")
    table_dict = {}

    # data
    
    for i in range (1,102):
        xpath = '//*[@id="__next"]/div/main/div[3]/div/div/div/div[4]/div['+ str(i) +']'
        row = browser.find_elements(By.XPATH, xpath)[0].text.split("\n")
        row_head = row[0]
        row_body = row[1:]
        table_dict[row_head] = row_body
    

    
    df = pd.DataFrame.from_dict(table_dict,orient="index", columns=cols)

    df =  clean_and_reconstruct_fundamentals(df,reconstruct_df = reconstruct_df)
    df = fundamental_calculator(df)

    browser.close()
    browser.quit()
    
    return df

