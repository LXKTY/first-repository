import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # 1. 사용할 요소들(Locators) 정의
        self.username_field = (By.NAME, "username")
        self.password_field = (By.NAME, "password")
        self.login_button = (By.XPATH, '//*[@id="app"]/div/div[6]/div/form/button')
        
    
    # 동작 정의
    def enter_username(self, username):
        username_input = self.wait.until(EC.presence_of_element_located(self.username_field))
        username_input.send_keys(username)
        
    def enter_password(self, password):
        password_input = self.wait.until(EC.presence_of_element_located(self.password_field))
        password_input.send_keys(password)
        
    def click_login_button(self):
        login_button = self.wait.until(EC.element_to_be_clickable(self.login_button))
        try:
            login_button.click()
            print("로그인 버튼 클릭 성공! 5초간 대기합니다...")
            time.sleep(5)
        except:
            self.driver.execute_script("arguments[0].click();", login_button)
            
    
    def login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
    
    