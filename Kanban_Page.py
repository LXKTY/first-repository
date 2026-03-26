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
        self.project_lee_test = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[2]/div[4]/div/div[2]/div/div/div/div/div/div[2]/span')
        self.kanban_task = (By.XPATH, '//*[@id="/project_menu"]/div/li/ul/div[1]/div/li/ul/div[12]/div')
        self.add_button = (By.XPATH, '//*[@id="workitem-kanban-toolbar"]/button[1]/span')
        self.title_input_field = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[1]/div/div[2]/div/div[1]/form/div[1]/div/div[1]/input')
        self.second_field = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[1]/div/div[2]/div/div[1]/form/div[2]/div/div/input')
        self.calendar_xpath = "/html/body/div[5]/div[1]/div/div[2]/table[1]/tbody//td[contains(@class, 'available')]"
        self.content_input_field = (By.XPATH, '//*[@id="tinymce"]')

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

    def click_add_button(self):
        """3. 칸반 툴바에서 '추가' 버튼 클릭"""
        try:
            print("🔄 '추가' 버튼 클릭 시도...")
            add_btn = self.wait.until(EC.element_to_be_clickable(self.add_button))
            
            # 스크롤 후 클릭
            self.driver.execute_script("arguments[0].scrollIntoView(true);", add_btn)
            add_btn.click()
            print("✅ '추가' 버튼 클릭 성공")
            time.sleep(1) # 다이얼로그 애니메이션 대기
            
        except Exception as e:
            print(f"❌ '추가' 버튼 클릭 실패: {e}")
            raise

    def input_kanban_title(self, title_text=None):
        """4. 입력 폼에 제목 작성 및 엔터"""
        try:
            # 제목 미지정 시 타임스탬프 기반 자동 생성
            if title_text is None:
                title_text = "자동화_테스트_" + time.strftime("%y%m%d_%H%M")

            print(f"📝 제목 입력 중: {title_text}")
            title_input = self.wait.until(EC.visibility_of_element_located(self.title_input_field))
            
            title_input.clear()
            title_input.send_keys(title_text)
            title_input.send_keys(Keys.ENTER)
            
            print(f"✅ 제목 입력 완료: {title_text}")
            return title_text

        except Exception as e:
            print(f"❌ 제목 입력 실패: {e}")
            self.driver.save_screenshot("input_error.png")
            raise
        

    def click_random_available_date(self):
        """두 번째 필드를 클릭하여 달력을 호출하고, 'available' 날짜 중 하나를 랜덤하게 클릭합니다."""
        try:
            # 1. 두 번째 입력 필드(날짜 선택기) 클릭
            print("📅 두 번째 입력 필드 클릭 (달력 호출 중)...")
            date_field = self.wait.until(EC.element_to_be_clickable(self.second_field))
            date_field.click()
            time.sleep(1) # 달력 레이어가 팝업되는 시간 대기

            print("🔍 선택 가능한 날짜 탐색 중...")
            
            # 2. 대상 tbody 안의 'available' 클래스 날짜들 찾기
            # self.calendar_xpath에 이미 경로를 만들어두셨으므로 그대로 사용합니다.
            available_days = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.calendar_xpath)))
            
            if available_days:
                # 3. 리스트 중에서 랜덤으로 하나 선택
                target_day = random.choice(available_days)
                day_text = target_day.text
                print(f"🎲 랜덤 선택된 날짜: {day_text}일")
                
                # 4. 클릭 (안전하게 JS 클릭 사용)
                self.driver.execute_script("arguments[0].click();", target_day)
                print(f"✅ {day_text}일 클릭 완료")
                
            else:
                print("⚠️ 선택 가능한(available) 날짜가 없습니다.")

        except Exception as e:
            print(f"❌ 날짜 선택 프로세스 중 에러 발생: {e}")
            self.driver.save_screenshot("calendar_error.png")
            raise
        
    # Kanban_Page.py 내부
    def input_content(self, content_text=None):
        try:
            if content_text is None:
                content_text = "자동화 테스트 본문 기본값_" + time.strftime("%Y%m%d_%H%M")
            
            print(f"📝 본문 내용(TinyMCE) 입력 중: {content_text}")

            # 1. 에디터가 들어있는 iframe 요소를 찾습니다. 
            # 보통 iframe의 ID나 클래스를 이용하거나, 상위 요소를 통해 접근합니다.
            # 만약 iframe ID를 모르신다면 우선 아래처럼 시도해보세요.
            wait_iframe = WebDriverWait(self.driver, 10)
            editor_iframe = wait_iframe.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

            # 2. 제어권을 iframe 내부로 전환합니다.
            self.driver.switch_to.frame(editor_iframe)

            # 3. iframe 내부의 실제 입력 필드(body 태그 등)를 찾아서 입력합니다.
            # TinyMCE는 보통 body#tinymce 구조를 가집니다.
            editor_body = self.wait.until(EC.element_to_be_clickable((By.ID, "tinymce")))
            
            # 기존 내용 삭제 (Control+A 후 Backspace 방식이 iframe에서 더 잘 먹힙니다)
            editor_body.send_keys(Keys.CONTROL + 'a')
            editor_body.send_keys(Keys.BACKSPACE)
            
            # 텍스트 입력
            editor_body.send_keys(content_text)
            print("✅ 본문 입력 완료")

            # 4. **중요** 입력을 마친 후 다시 메인 창으로 제어권을 돌려줍니다.
            self.driver.switch_to.default_content()

        except Exception as e:
            # 에러 발생 시에도 메인 창으로 복귀 시도
            self.driver.switch_to.default_content()
            print(f"❌ 본문 입력 실패: {e}")
            self.driver.save_screenshot("content_input_error.png")
            raise
        
    
    def click_save_button(self):
        """5. 작성한 내용을 저장합니다 (강력한 클릭 로직 적용)"""
        try:
            # [필수] iframe에서 메인 컨텐츠로 확실히 복귀
            self.driver.switch_to.default_content()
            time.sleep(0.5) # 프레임 전환 후 아주 잠깐 대기

            print("💾 저장 버튼 클릭 시도 중...")
            
            # 저장 버튼 요소를 가져옵니다.
            save_btn_xpath = (By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[3]/section/div[1]/div[1]/div/div[2]/div/div[2]/button[1]/span')
            
            # 1단계: 버튼이 보이고 클릭 가능할 때까지 확실히 대기
            save_btn = self.wait.until(EC.element_to_be_clickable(save_btn_xpath))
            
            # 2단계: 화면 중앙으로 스크롤 (다른 요소에 가려지지 않게 함)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
            time.sleep(0.5)

            # 3단계: JavaScript를 이용한 직접 클릭 (가장 강력함)
            # 일반 .click()은 가려져 있으면 에러가 나거나 무시되지만, JS 클릭은 좌표 무관하게 이벤트를 발생시킵니다.
            self.driver.execute_script("arguments[0].click();", save_btn)
            
            print("✅ 저장 버튼에 JavaScript 클릭 신호를 보냈습니다.")
            
            # 저장 후 화면 변화를 확인하기 위해 잠시 대기
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ 저장 버튼 클릭 실패: {e}")
            self.driver.save_screenshot("save_button_critical_error.png")
            raise