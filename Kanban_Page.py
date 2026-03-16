from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class KanbanPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        
        # [전략] 'LEE_TEST'라는 텍스트를 가진 span의 부모 div를 찾습니다.
        # 이 방식은 이미지나 글자 어디를 클릭해도 div 전체가 잡히므로 실패율이 낮습니다.
        
        self.project_lee_test = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[2]/div[4]/div/div[2]/div/div/div/div/div/div[2]/span')
        self.kanban_task = (By.XPATH, '//*[@id="/project_menu"]/div/li/ul/div[1]/div/li/ul/div[12]/div')
        
    def select_project(self):
        # 'LEE_TEST'라는 텍스트를 가진 span 요소를 찾음
        element = self.wait.until(EC.visibility_of_element_located(self.project_lee_test))
        element.click()  # 해당 요소 클릭
        print("✅ 'LEE_TEST' 프로젝트 진입 성공")   
        
    
        
    def select_task(self):
        try:
            # 1. 사이드바 메뉴가 뜰 때까지 잠시 대기
            time.sleep(2) 
            
            # 2. [스크롤 로직] 해당 요소가 보일 때까지 사이드바 내부를 스크롤함
            # presence_of_element_located는 눈에 안 보여도 DOM에 있으면 잡습니다.
            task_element = self.wait.until(EC.presence_of_element_located(self.kanban_task_path))
            
            # 3. 요소가 위치한 곳으로 부모 영역 스크롤 이동
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", task_element)
            print("📜 '칸반뷰 테스트' 위치로 스크롤 이동")
            time.sleep(1) # 이동 후 안정화 대기
            
            # 4. 강제 클릭
            self.driver.execute_script("arguments[0].click();", task_element)
            print("✅ '칸반뷰 테스트' 업무 진입 성공")
            
        except Exception as e:
            print(f"❌ 업무 진입 중 에러 발생: {e}")
            self.driver.save_screenshot("scroll_error.png")
            raise
        
        
        #0025