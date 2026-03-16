from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains    
import time

class KanbanPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        
        # [전략] 절대 경로(Full XPATH)보다는 텍스트나 고유 속성을 활용하는 것이 화면 크기 변화에 강합니다.
        self.project_lee_test = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[2]/div[4]/div/div[2]/div/div/div/div/div/div[2]/span')
        # 칸반뷰 테스트 업무 (텍스트 기반으로 찾으면 스크롤 시에도 더 정확합니다)
        self.kanban_task = (By.XPATH, '//*[@id="/project_menu"]/div/li/ul/div[1]/div/li/ul/div[12]/div')
        
    def select_project(self):
        # 'LEE_TEST' 프로젝트 선택
        element = self.wait.until(EC.element_to_be_clickable(self.project_lee_test))
        element.click()
        print("✅ 'LEE_TEST' 프로젝트 진입 성공")   
        
    def select_task(self):
        try:
            print("🔄 새로 열린 프로젝트 창으로 전환합니다...")
        
            # 1. [창 전환 로직] 현재 열린 모든 창의 핸들을 가져옵니다.
            all_windows = self.driver.window_handles
        
            # 2. 마지막에 열린 창(새 창)으로 드라이버 제어권을 옮깁니다.
            if len(all_windows) > 1:
                self.driver.switch_to.window(all_windows[-1])
                print(f"✅ 새 창으로 전환 완료: {self.driver.title}")
            else:
                print("⚠️ 새 창이 발견되지 않았습니다. 현재 창에서 계속 진행합니다.")

            # 3. 새 창이 로딩될 때까지 잠시 대기
            time.sleep(2) 
        
            # 4. 이제 사이드바에서 업무를 탐색합니다.
            xpath_task = (By.XPATH, "//*[contains(@data-tooltip-text, '칸반뷰 테스트')] | //span[contains(text(), '칸반뷰 테스트')]")
        
            # 요소 대기 및 스크롤
            task_element = self.wait.until(EC.presence_of_element_located(xpath_task))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", task_element)
        
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", task_element)
            print("✅ '칸반뷰 테스트' 업무 진입 성공")

        except Exception as e:
            print(f"❌ 업무 진입 중 에러 발생: {e}")
            self.driver.save_screenshot("window_switch_error.png")
            raise