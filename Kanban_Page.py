from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random
import time

class KanbanPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        
        # --- [Locators] XPATH 경로는 원본 그대로 유지 ---
        self.project_lee_test = (By.XPATH, "//*[@id='app']//div[contains(@class, 'project-item-column')]//span[text()='LEE_TEST']")
        self.kanban_task = (By.XPATH, '//*[@id="/project_menu"]/div/li/ul/div[1]/div/li/ul/div[12]/div')
        self.add_button = (By.XPATH, '//*[@id="workitem-kanban-toolbar"]/button[1]/span')
        self.title_input_field = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[1]/div/div[2]/div/div[1]/form/div[1]/div/div[1]/input')
        self.second_field = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[1]/div/div[2]/div/div[1]/form/div[2]/div/div/input')
        self.calendar_xpath = "//td[contains(@class, 'available')]"
        self.content_input_field = (By.XPATH, '//*[@id="tinymce"]')
        self.save_btn_xpath = (By.XPATH, '//*[@id="app"]//button[contains(., "저장")]')
        
        

    def select_project(self):
        """1. 'LEE_TEST' 프로젝트 선택 및 진입"""
        print("🚀 프로젝트 진입 시도 중...")
        element = self.wait.until(EC.element_to_be_clickable(self.project_lee_test))
        element.click()
        print("✅ 'LEE_TEST' 프로젝트 진입 성공")

    def select_task(self):
        """2. 새 창 전환 및 '칸반뷰 테스트' 업무 선택"""
        try:
            # [창 전환] 새 창이 열릴 때까지 대기 후 제어권 이동
            all_windows = self.driver.window_handles
            if len(all_windows) > 1:
                self.driver.switch_to.window(all_windows[-1])
                print(f"✅ 새 창 전환 완료: {self.driver.title}")
            
            time.sleep(2) # 페이지 안정화 대기

            # [업무 탐색] 툴팁 또는 텍스트 기반으로 정밀 탐색
            xpath_task = (By.XPATH, "//*[contains(@data-tooltip-text, '칸반뷰 테스트')] | //span[contains(text(), '칸반뷰 테스트')]")
            task_element = self.wait.until(EC.presence_of_element_located(xpath_task))
            
            # 스크롤 및 클릭 (JS 실행으로 안전하게 접근)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", task_element)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", task_element)
            print("✅ '칸반뷰 테스트' 업무 진입 성공")

        except Exception as e:
            print(f"❌ 업무 진입 중 에러 발생: {e}")
            self.driver.save_screenshot("task_entry_error.png")
            raise

    def create_kanban_post(self, title=None, content=None):
        try:
            print("\n🚀 [최종 공정] 칸반 게시물 생성을 시작합니다.")

            # 1. '추가' 버튼 클릭 (물리 클릭 시도, 안 되면 JS)
            add_btn = self.wait.until(EC.element_to_be_clickable(self.add_button))
            try:
                add_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", add_btn)
            time.sleep(1)

            # 2. 제목 입력
            if title is None:
                title = "최종_자동화_" + time.strftime("%y%m%d_%H%M")
            title_input = self.wait.until(EC.visibility_of_element_located(self.title_input_field))
            title_input.clear()
            title_input.send_keys(title)
            title_input.send_keys(Keys.ENTER)
            print(f"✅ 제목 입력 완료: {title}")

            # 3. 날짜 랜덤 선택 (기존 로직 유지하되 물리 클릭 시도)
            date_field = self.wait.until(EC.element_to_be_clickable(self.second_field))
            date_field.click()
            time.sleep(1)
            
            available_days = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "available")))
            if available_days:
                target_day = random.choice(available_days)
                # 날짜는 작아서 클릭이 빗나갈 수 있으니 JS 클릭이 안전합니다.
                self.driver.execute_script("arguments[0].click();", target_day)
                print(f"✅ 날짜 선택 완료")

            # 4. 본문 입력 (눈에 보이는 정공법!)
            if content is None:
                content = "마지막 통합 테스트 본문입니다."
                
            editor_iframe = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            self.driver.switch_to.frame(editor_iframe)
            
            editor_body = self.wait.until(EC.element_to_be_clickable((By.ID, "tinymce")))
            
            # [수정] JS 주입 대신 직접 타이핑
            editor_body.click()
            editor_body.send_keys(Keys.CONTROL + 'a')
            editor_body.send_keys(Keys.BACKSPACE)
            editor_body.send_keys(content) # 글자가 써지는 게 보입니다!
            print("✅ 본문 타이핑 완료")
            
            self.driver.switch_to.default_content()
            
            # 5. 저장 버튼 클릭 (들여쓰기 수정 및 물리 클릭)
            print("💾 저장 버튼 클릭 시도...")
            # xpath 변수가 튜플인지 확인하세요. (By.XPATH, "...") 형태여야 합니다.
            save_btn = self.wait.until(EC.element_to_be_clickable(self.save_btn_xpath))
            
            # 중앙으로 스크롤해서 보여주기
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
            time.sleep(1)

            # 진짜 마우스 클릭!
            save_btn.click()
            save_btn.click()
            print("🎉 게시물 저장 완료!")
            
            time.sleep(2)
            return title

        except Exception as e:
            self.driver.switch_to.default_content()
            print(f"❌ 공정 중 에러 발생: {e}")
            self.driver.save_screenshot("final_error.png")
            raise