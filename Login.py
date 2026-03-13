from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# 크롬 드라이버 실행
driver = webdriver.Chrome()

# 사이트 접속
driver.get("http://222.239.248.185:8010/#/login")

# 페이지 로딩 대기
wait = WebDriverWait(driver, 10)

# 아이디 입력
id_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
id_input.send_keys("sjlee")

# 비밀번호 입력
pw_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
pw_input.send_keys("132435ab!")

# 로그인 버튼 클릭
xpath_value = '//*[@id="app"]/div/div[6]/div/form/button'
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_value)))

try:
    login_button.click()
    print("로그인 버튼 클릭 성공! 5초간 대기합니다...")
    print("파일 내용 수정 완료")
    time.sleep(5)
except:
    driver.execute_script("arguments[0].click();", login_button)
