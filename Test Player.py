from selenium import webdriver
from Login_Page import LoginPage
from Kanban_Page import KanbanPage
import time

# 크롬 드라이버 실행
driver = webdriver.Chrome()

# 브라우저 창 최대화 (사이트 접속 전이나 직후에 바로 넣어주세요!)
driver.maximize_window()

# 사이트 접속
driver.get("http://222.239.248.185:8010/#/login")

login_pg = LoginPage(driver)

login_pg.login("sjlee", "132435ab!")

print("로그인 완료")

kanban_pg = KanbanPage(driver)

# 1. 프로젝트 선택 및 진입
kanban_pg.select_project()

# 2. 이동 후 페이지 제목이나 특정 요소가 있는지 확인 (검증)
# assert "프로젝트" in driver.page_source

# 3. 업무 선택 및 진입
kanban_pg.select_task()

time.sleep(10)
driver.quit()
# 4T-2672
