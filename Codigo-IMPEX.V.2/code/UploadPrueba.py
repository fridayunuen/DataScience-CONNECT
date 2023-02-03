# this program will open a web page, log in, and upload a file
# will use selenium and chrome
# and will use the chrome driver

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time

import datetime as dt
from datetime import datetime, timedelta
import time
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup # this module helps in web scrapping.
from pynput.keyboard import Key, Controller

path = r"C:\Users\fcolin\Desktop"
path_chromedriver = r'C:/Users/fcolin/AppData/Local/rasjani/WebDriverManager/bin/chromedriver.exe'

chrome_options = Options()

page_login = '''https://backoffice.c1s9x93c4p-servicios1-s1-public.model-t.cc.commerce.ondemand.com/backoffice/login.zul''' 
#page_login ="https://backoffice.c1s9x93c4p-servicios1-s1-public.model-t.cc.commerce.ondemand.com/backoffice/"

import json 
credenciales_path = r"C:\Users\fcolin\Desktop\input\CredencialesSAP.json"


with open(credenciales_path) as f:
    credenciales = json.load(f)

usuario = credenciales['usuario']
contrasena = credenciales['password']

#webdriver = path_chromedriver
#driver = webdriver.Chrome(webdriver, options=chrome_options)

####3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.google.com")
#####




driver = webdriver.Chrome(executable_path=path_chromedriver, options=chrome_options)
driver.get(page_login)
time.sleep(5)

# log in
driver.find_element(By.NAME, 'j_username').send_keys(usuario)
driver.find_element(By.NAME, 'j_password').send_keys(contrasena)
driver.find_element(By.CSS_SELECTOR , 'button').click()
#print(driver.page_source)
time.sleep(4)
# get all html code from the page


html = driver.page_source

two_tables_bs= BeautifulSoup(html, 'html.parser')
table_rows=two_tables_bs.find_all('button')

# last element
button = table_rows[-1]

# get id of the button
button_id = button.get('id')

driver.find_element(By.ID, button_id).click()

time.sleep(10)

driver.find_element(By.CLASS_NAME, "z-bandbox-input").send_keys("Import")
time.sleep(2)


def click_element(etiqueta, texto, by, sleep):
    html = driver.page_source
    two_tables_bs= BeautifulSoup(html, 'html.parser')
    table_rows=two_tables_bs.find_all(etiqueta)
    for row in table_rows:
        if row.text == texto:
            id = row.get('id')
            break
    driver.find_element(by, id).click()   
    time.sleep(sleep) 

keyboard = Controller()

# create a function to press the keys certain times
def press_key(key, times):
    for i in range(times):
        keyboard.press(key)
        time.sleep(0.5)

#######
impex_files = ["impex1.impex", "impex2.impex"]
for impex_file in impex_files:

    click_element('span', 'Importación', By.ID, 5)

    click_element('button', 'cargar', By.ID, 2)


    # it apperas a option to select the file
    # it shows our local files on the computer

    press_key(Key.tab, 5)
    press_key(Key.enter, 1)

    keyboard.type(r"C:\Users\fcolin\Documents\GitHub\Codigo-IMPEX.V.2\output\Resultados\13-10-2022(10-58-44)\Lote1")
    time.sleep(1)

    press_key(Key.enter, 1)
    press_key(Key.tab, 6)
    press_key(Key.enter, 1)
    keyboard.type(impex_file)
    time.sleep(1)

    press_key(Key.enter, 1)

    click_element('button', 'crear', By.ID,2)

    click_element('button', 'Siguiente', By.ID, 5)

    click_element('button', 'cargar', By.ID, 1)

    keyboard.type("Lote1.zip")
    time.sleep(1)

    keyboard.press(Key.enter)
    time.sleep(60)  ##### agregar un try 30 seg

    click_element('button', 'crear', By.ID,3)

    click_element('button', 'Start', By.ID, 2)

    click_element('button', 'Listo', By.ID, 2)
