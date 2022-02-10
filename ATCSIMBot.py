import time
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

def getFajas(driver, frame):
    fajas = {}
    driver.switch_to.frame(frame)
    for faja in driver.find_elements(By.CLASS_NAME, 'ProgressStrip'):
        info =  faja.text.split()
        fajas[info.pop(0)] = info
    driver.switch_to.default_content()
    return fajas

def rumboCalc(height, left, top):
    if height == 1.0:
        angulo = 90.0
    else:
        angulo = math.degrees(math.acos(height/24))
     
    if left == 24.0:
        if top == 34.0:
            rumbo = 360 - angulo
        else:
            rumbo = 180 + angulo
    else:
        if top == 34.0:
            rumbo = angulo
        else:
            rumbo = 180 - angulo
    return rumbo

def getEco(driver, callSign):
    eco = {}
    blanco = driver.find_element(By.ID, callSign)
    table = blanco.find_element(By.XPATH, 'table/tbody/tr/td/img')  
    height = float(table.get_attribute('style').split()[5].replace('px;', ''))
    left = float(table.get_attribute('style').split()[7].replace('px;', ''))
    top = float(table.get_attribute('style').split()[9].replace('px;', ''))
    try:
        eco["PosX"] = int(blanco.get_attribute('style').split()[3].replace('px;', '')) + 24
        eco["PosY"] = int(blanco.get_attribute('style').split()[5].replace('px;', '')) + 34 
        eco["NivelVuelo"] = blanco.text.split('\n')[1][0:3]
        eco["Up-Down"] = blanco.text.split('\n')[1][3]
        eco["Ias"] = int(blanco.text.split('\n')[1][4:len(blanco.text.split('\n')[1])])
        eco["Rumbo"] = rumboCalc(height, left, top)
    except IndexError as error:
        print(blanco.get_attribute('Inner text'))
    return eco

print('Abriendo Simulador...')
driver = webdriver.Firefox()
driver.get('https://atc-sim.com/')
 
print('Seleccionando Aeropuerto...')
selectAirport = Select(driver.find_element(By.NAME, 'selAirport'))
selectAirport.select_by_visible_text('London Heathrow (LHR / EGLL)')

print('Seleccionando Dificultad...')
selectDifficulty = Select(driver.find_element(By.NAME, 'PlayMode'))
selectDifficulty.select_by_value('2')

print('Comenzando Simulación...')
beginSimButton = driver.find_element(By.XPATH, '/html/body/div[4]/div[1]/form/table/tbody/tr/td[1]/input[1]')
beginSimButton.click()

startNowButton = driver.find_element(By.XPATH, '//*[@id="btnclose"]')
startNowButton.click()

print('Inicializando Frame...')
frame = driver.find_element(By.XPATH, '/html/body/div[1]/div/iframe')

# De la Status Bar puedo sacar Ingresos a TMA, aterrizajes, y ACK
print('Inicializando Barra de Estado...')
statusBar = driver.find_element(By.XPATH, '//*[@id="statusbar"]')

print('Inicializando Input Box...')
inputBox = driver.find_element(By.XPATH, '/html/body/div[1]/div/form/input[1]')

time.sleep(2)

for i in range(120):
    fajas = getFajas(driver, frame)
    key =  list(fajas.keys())[0]
    
    print(i, getEco(driver, key))
    # print('Faja: ', key, fajas[key])
    # print(statusBar.text)
    # inputBox.send_keys(acftStrip[0], ' C ', i*100)
    # inputBox.send_keys(Keys.ENTER)
    
    time.sleep(1)
    
# STRIP: 
    # - CALLSIGN (key)
    # - INTENDED COURSE
    # - INTENDED FL+MAINT/UP/DOWN
    # - ACFT TYPE
    # - ARR/DEP
    
 # ECO: 
    # - POS X
    # - POS Y
    # - FL
    # - MAINT/UP/DOWN
    # - IAS
    # - RUMBO

# LAS AERONAVES GIRAN CON UNA TASA DE 3°/s ¿TODAS?
# LAS AERONAVES ASCIENDEN CON UNA TASA DE 2000 ft/min ¿TODAS?
# LAS AERONAVES DESCIENDEN CON UNA TASA DE 2000 ft/min ¿TODAS?
    