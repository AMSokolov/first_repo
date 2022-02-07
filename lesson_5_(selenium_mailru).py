"""
Написать программу, которая собирает входящие письма из своего или тестового
почтового ящика и сложить данные о письмах в базу данных (от кого, дата отправки,
тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172#
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['news_on_mail_ru']
mail_ru = db.mailru

driver = webdriver.Chrome(executable_path='./chromedriver')
driver.implicitly_wait(10)

driver.get('https://mail.ru/')

elem = driver.find_element(By.NAME, 'login')
elem.send_keys('study.ai_172@mail.ru')
elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.NAME, 'password')
elem.send_keys('NextPassword172#')
elem.send_keys(Keys.ENTER)

mail_one = driver.find_element(By.XPATH, "//div[contains(@class, 'Grid__inner')]/a[1]").get_attribute('href')
driver.get(mail_one)

while True:

    mail_base = {}

    title = driver.find_element(By.XPATH, "//h2[@class='thread-subject']").text
    content = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'BODY')]"))).text
    date = driver.find_element(By.XPATH, "//div[@class='letter__author']//div[@class='letter__date']").text
    sender = driver.find_element(By.XPATH, "//div[@class='letter__author']/span[@class='letter-contact']").get_attribute('title')

    mail_base['title'] = title
    mail_base['date'] = date
    mail_base['sender'] = sender
    mail_base['content'] = content
    # Понятное дело, данные в "сыром виде"

    mail_ru.insert_one(mail_base) #Запись в БД

    #Выход из цикла если стрелка не активна в последнем письме
    button_down = driver.find_element(By.XPATH, "//span[contains(@class, 'arrow-down')]")
    if 'button2_disabled' in button_down.get_attribute('class'):
        break

    #Переход на след. страницу
    actions = ActionChains(driver).key_down(Keys.CONTROL).send_keys('\ue015')
    actions.perform()
    time.sleep(3)


print('Перебор закончен')
driver.quit()


