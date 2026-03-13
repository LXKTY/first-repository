from selenium import webdriver
from login_page import LoginPage
import time

driver = webdriver.Chrome()
driver.get("http://222.239.248.185:8010/#/login")

login_pg = LoginPage(driver)

login_pg.login("sjlee", "132435ab!")

print("로그인 완료")
time.sleep(5)
driver.quit()

