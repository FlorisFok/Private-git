passs = "PythonPower"
import pandas as pd
from selenium import webdriver
import time

from selenium.webdriver.chrome.options import Options

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

from apscheduler.schedulers.blocking import BlockingScheduler

def background_driver():
    CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" #"C:\Program Files (x86)\Google\Chrome"
    CHROMEDRIVER_PATH = r'C:/Webdrivers/chromedriver.exe'
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.binary_location = CHROME_PATH

    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                              chrome_options=chrome_options
                             )

    return driver

def start_driver(url, driver = None):
    if driver == None:
        driver = webdriver.Chrome(executable_path=r'C:/Webdrivers/chromedriver.exe')
    driver.get(url)
    return driver

def get_content(driver,css_header):    
    games = driver.find_elements_by_css_selector(css_header)
    return games

def select_value(item, value = '666'):
    for num,i in enumerate(item):
        if i.text == value:
            return i

def select_value_in(item, value = '666'):
    for num,i in enumerate(item):
        if value in i.text:
            return i
def layer_click(driver, css = "span.nav-line-1", value= 'Winkel-'):
    item = get_content(driver, css)
    web_item = select_value(item, value)
    web_item.click()

def login(driver):
    mail = driver.find_element_by_id("ap_email")
    password = driver.find_element_by_id("ap_password")
    mail.send_keys("florisfok5@gmail.com")
    password.send_keys(passs)
    driver.find_element_by_id("signInSubmit").click()

def skip_special_price(driver, no_go=['Tweedehands']):
    try:
        for no in no_go:
            if driver.page_source.find(no) != -1:
                return True
        prices = get_content(driver,"i.a-icon.a-accordion-radio.a-icon-radio-inactive")
        prices[0].click()
        driver.implicitly_wait(5)
    except:
        pass

def skip_popup(driver, key_word = "siNoCoverage-announce"):
    try:
        close = driver.find_elements_by_css_selector("button.a-button-close.a-declarative")
        driver.implicitly_wait(5)
        close[0].click()  
        driver.implicitly_wait(5)
    except:
        try:
            close = driver.find_elements_by_css_selector("i.a-icon.a-icon-close")
            driver.implicitly_wait(5)
            close[0].click()
            close = driver.find_elements_by_css_selector("button.a-button-close.a-declarative")
            driver.implicitly_wait(5)
            close[0].click()  
            driver.implicitly_wait(5)  
        except:
            pass

def find_rank(driver):
    try:
        ranking = driver.find_elements_by_css_selector('ul.zg_hrsr')
        rankings = ranking[0].text
    except:
        try:
            ranking = driver.find_elements_by_css_selector('td.value')
            rankings = ranking[0].text
        except:
            rankings = 'None'
    return rankings

def check_stock(product_code, back = True):
    ## background or not
    if back:
        driver_background = background_driver()
        driver = start_driver(f"https://www.amazon.de/gp/product/{product_code}/"
                              "ref=ox_sc_act_title_1?language=nl_NL&psc=1&smid=A3MYSHBXOUSGH",
                              driver_background)
    else:
        driver = start_driver(f"https://www.amazon.de/gp/product/{product_code}/"
                              "ref=ox_sc_act_title_1?language=nl_NL&psc=1&smid=A3MYSHBXOUSGH")

    ## Find ranking of the product
    rankings = find_rank(driver)

    ## selects normal priceses
    skip_special_price(driver)

    ## selects the shopping cart
    layer_click(driver, css = "span.a-button-inner", value= 'In winkelwagen')
    driver.implicitly_wait(5)

    ## cancels special offers (Coverage)
    skip_popup(driver)

    ## Loging if nessecary
    try:
        layer_click(driver, css = "span.nav-line-1", value= 'Winkel-')
    except:
        try:
            login(driver)
            driver.implicitly_wait(5)
            layer_click(driver, css = "span.nav-line-1", value= 'Winkel-')
        except:
            pass

    ## Fill in the 999
    driver.implicitly_wait(5)
    layer_click(driver, css = "span.a-button-inner", value= '1')
    driver.implicitly_wait(5)
    layer_click(driver, css = "li.a-dropdown-item.quantity-option.quantity-option", value= '10+')
    driver.implicitly_wait(5)

    ## Get the error
    item5 = get_content(driver, "input.a-input-text.a-span8.sc-quantity-textfield.sc-hidden")
    item5[0].send_keys(999)
    driver.implicitly_wait(5)
    layer_click(driver, css = "span.a-button-inner", value= 'Updaten')

    ## Get the text and covert to numbers
    while True:
        try:
            driver.implicitly_wait(5)
            item7 = get_content(driver, "span.a-size-base")
            web_item = select_value_in(item7, value = 'Deze verkoper')

            cijfers = ''
            for letter in web_item.text:
                try:
                    int(letter)
                    cijfers += letter
                except:
                    pass
            print(cijfers)
            # driver.close()
            return int(cijfers), rankings
        except:
            pass


def take_note(client, name, count, rank):

    ts = time.localtime()
    now = f"{ts.tm_year}.{ts.tm_mon}.{ts.tm_mday}.{ts.tm_hour}.{ts.tm_min}"

    sheet  = client.open('Test').sheet1

    cell = sheet.find(name)
    col_start = cell.col - 1

    TIME_COL = col_start 
    RANK_COL = col_start + 1
    COUNT_COL = col_start + 2
    PYTHON_TIME = col_start + 3

    time_list = sheet.col_values(TIME_COL)
    time_sec = time.time()

    row = len(time_list) + 1
    sheet.update_cell(row, TIME_COL, now)
    sheet.update_cell(row, RANK_COL, rank)
    sheet.update_cell(row, COUNT_COL, count)
    sheet.update_cell(row, PYTHON_TIME, time_sec)
    return True

def main():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']   

    creds = ServiceAccountCredentials.from_json_keyfile_name(
                r"C:\Users\s147057\Documents\CS50\Database-6141813cd99e.json", scope)

    client = gspread.authorize(creds)  

    BACKGROUND = True
    my_list = [{"name":"smart_houder", "code": "B07F1JWGTF"},
               {"name":"stekkerdoos", "code": "B07MNGHH7M"},
               {"name":"cloth", "code" : "B07HRCDDL1"},
               {"name":"spray", "code": "B0194SH1AU"},
               {"name":"mok", "code": "B008TLGFVU"}]

    ## test tray
    # my_list = [{"name":"oordoppen", "code": "B07BXNKJ5P"}]
    # BACKGROUND = False
    ## end test tray

    for product in my_list:
        print("Fetch:" + product["name"])
        count, rankings = check_stock(product["code"], BACKGROUND)
        take_note(client, product["name"], count, rankings)

if __name__ == '__main__':
    main()
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'interval', hours=1)
    scheduler.start()

    #https://www.amazon.de/gp/product/B07F1JWGTF/ref=ox_sc_act_title_1?language=nl_NL&psc=1