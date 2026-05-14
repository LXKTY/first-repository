"""
Teamer 문서뷰 동시 편집 제한 테스트
- 두 계정이 동시에 같은 문서에 접근하여 편집 후 저장 버튼을 동시에 클릭
- pip install playwright 설치 후 실행
- playwright install chromium

흐름:
  1) 로그인 페이지 진입 → 로그인
  2) LEE_TEST 프로젝트 클릭 (새 창 전환)
  3) 사이드바 '문서뷰 확인' 메뉴 진입
  4) 대상 게시물 URL 직접 진입
  5) 두 세션이 동시에 '내용' 필드에 랜덤 데이터 입력
  6) 두 세션이 동시에 저장 버튼 클릭
"""

import asyncio
import random
import string
from playwright.async_api import async_playwright, BrowserContext, Page

# =============================================
# 설정값 — 실제 사용 시 환경변수로 관리 권장
# =============================================
BASE_URL = "http://222.239.248.185:8010"
LOGIN_URL = f"{BASE_URL}/#/login"
TARGET_URL = f"{BASE_URL}/#/project/116/workitem/9205/list/detail/1651309"

ACCOUNT_A = {
    "id": "sjlee",
    "pw": "vway123!",
    "label": "세션 A (sjlee)"
}

ACCOUNT_B = {
    "id": "sjlee_company",
    "pw": "132435ab!",
    "label": "세션 B (sjlee_company)"
}


async def login_and_open(context: BrowserContext, account: dict, result: dict):
    """로그인 → LEE_TEST 진입 → 문서뷰 확인 메뉴 → 대상 문서 진입"""
    page = await context.new_page()
    label = account["label"]

    try:
        # 1. 로그인 페이지 이동
        print(f"[{label}] 로그인 페이지 이동 중...")
        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")

        # 2. 로그인 (Login_Page.py 셀렉터 기준)
        await page.wait_for_selector("input[name='username']", timeout=15000)
        await page.fill("input[name='username']", account["id"])
        await page.fill("input[name='password']", account["pw"])
        await page.click('xpath=//*[@id="app"]/div/div[6]/div/form/button')
        print(f"[{label}] 로그인 버튼 클릭 — 대기 중...")
        await page.wait_for_timeout(5000)

        # 3. LEE_TEST 프로젝트 클릭 (새 창 전환 대비)
        lee_test_locator = page.locator(
            "xpath=//*[@id='app']//div[contains(@class, 'project-item-column')]//span[text()='LEE_TEST']"
        ).first
        await lee_test_locator.wait_for(state="visible", timeout=15000)

        # 새 창이 열리는 경우/같은 탭에서 이동하는 경우 모두 대응
        work_page: Page = page
        try:
            async with context.expect_page(timeout=5000) as new_page_info:
                await lee_test_locator.click()
            work_page = await new_page_info.value
            await work_page.wait_for_load_state("networkidle")
            print(f"[{label}] 새 창 전환 완료")
        except Exception:
            # 새 창이 안 열리면 기존 페이지 그대로 사용
            await page.wait_for_load_state("networkidle")
            print(f"[{label}] 동일 탭에서 프로젝트 진입")

        await work_page.wait_for_timeout(2000)

        # 4. '문서뷰 확인' 사이드바 메뉴 클릭 (data-tooltip-text 또는 텍스트 기반)
        doc_menu = work_page.locator(
            "xpath=//*[contains(@data-tooltip-text, '문서뷰 확인')] | //span[contains(text(), '문서뷰 확인')]"
        ).first
        await doc_menu.wait_for(state="visible", timeout=15000)
        try:
            await doc_menu.scroll_into_view_if_needed()
        except Exception:
            pass
        await doc_menu.click()
        print(f"[{label}] '문서뷰 확인' 메뉴 진입 완료")
        await work_page.wait_for_timeout(2000)

        # 5. 대상 게시물 URL 직접 이동
        await work_page.goto(TARGET_URL)
        await work_page.wait_for_load_state("networkidle")
        await work_page.wait_for_timeout(2000)
        print(f"[{label}] 대상 문서 진입 완료: {work_page.url}")

        result["page"] = work_page
        result["success"] = True

    except Exception as e:
        print(f"[{label}] 오류 발생: {e}")
        try:
            await page.screenshot(path=f"login_error_{label.replace(' ', '_')}.png")
        except Exception:
            pass
        result["success"] = False
        result["error"] = str(e)


def random_content(label: str) -> str:
    """세션 식별 가능한 랜덤 내용 생성"""
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"[{label}] 동시편집테스트-{suffix}"


async def edit_content(page: Page, label: str, result: dict):
    """문서 '내용' 필드(TinyMCE iframe)에 랜덤 데이터 입력"""
    try:
        # 편집 모드 진입 버튼이 있다면 먼저 클릭 ('수정' 또는 '편집')
        for sel in [
            "xpath=//*[@id='app']//button[contains(., '수정')]",
            "xpath=//*[@id='app']//button[contains(., '편집')]",
        ]:
            btn = page.locator(sel).first
            try:
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click()
                    print(f"[{label}] 편집 모드 진입")
                    await page.wait_for_timeout(1500)
                    break
            except Exception:
                pass

        # TinyMCE iframe 진입 (Kanban_Page.py와 동일 패턴)
        editor_frame = page.frame_locator("iframe").first
        editor_body = editor_frame.locator("#tinymce")
        await editor_body.wait_for(state="visible", timeout=10000)

        # 기존 내용 전체 선택 후 삭제
        await editor_body.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Delete")

        # 랜덤 내용 타이핑
        content = random_content(label)
        await page.keyboard.type(content, delay=30)
        print(f"[{label}] 내용 입력 완료: {content}")

        result["typed_content"] = content
        result["edit_success"] = True

    except Exception as e:
        print(f"[{label}] 내용 입력 오류: {e}")
        try:
            await page.screenshot(path=f"edit_error_{label.replace(' ', '_')}.png")
        except Exception:
            pass
        result["edit_success"] = False
        result["edit_error"] = str(e)


async def click_save(page: Page, label: str, result: dict):
    """저장 버튼 클릭 및 결과 캡처"""
    try:
        # Kanban_Page.py와 동일한 패턴: app 내부 '저장' 텍스트 버튼
        save_button = page.locator(
            "xpath=//*[@id='app']//button[contains(., '저장')]"
        ).first

        await save_button.wait_for(state="visible", timeout=10000)
        try:
            await save_button.scroll_into_view_if_needed()
        except Exception:
            pass

        await save_button.click()
        print(f"[{label}] 저장 버튼 클릭 완료")

        # 결과 메시지 확인 (성공/실패/충돌 메시지)
        await page.wait_for_timeout(2000)
        result["after_save_url"] = page.url
        result["save_clicked"] = True

        # 스크린샷 저장
        await page.screenshot(path=f"result_{label.replace(' ', '_')}.png")
        print(f"[{label}] 저장 후 스크린샷 저장 완료")

    except Exception as e:
        print(f"[{label}] 저장 버튼 오류: {e}")
        try:
            await page.screenshot(path=f"error_{label.replace(' ', '_')}.png")
        except Exception:
            pass
        result["save_clicked"] = False
        result["error"] = str(e)


async def main():
    result_a = {}
    result_b = {}

    async with async_playwright() as pw:

        # 두 개의 독립적인 브라우저 컨텍스트 생성 (세션 분리)
        browser_a = await pw.chromium.launch(headless=False, slow_mo=300)
        browser_b = await pw.chromium.launch(headless=False, slow_mo=300)

        context_a = await browser_a.new_context()
        context_b = await browser_b.new_context()

        # ── STEP 1: 두 세션 동시 로그인 및 문서 진입 ──────────────────
        print("\n=== STEP 1: 동시 로그인 및 문서 진입 ===")
        await asyncio.gather(
            login_and_open(context_a, ACCOUNT_A, result_a),
            login_and_open(context_b, ACCOUNT_B, result_b),
        )

        if not result_a.get("success") or not result_b.get("success"):
            print("\n❌ 로그인/문서 진입 실패로 테스트 중단")
            await asyncio.sleep(3)
            await browser_a.close()
            await browser_b.close()
            return

        page_a = result_a["page"]
        page_b = result_b["page"]

        # ── STEP 2: 두 세션 동시 '내용' 필드 랜덤 입력 ─────────────────
        print("\n=== STEP 2: 동시 내용 입력 ===")
        await asyncio.gather(
            edit_content(page_a, ACCOUNT_A["label"], result_a),
            edit_content(page_b, ACCOUNT_B["label"], result_b),
        )

        # ── STEP 3: 동시 저장 버튼 클릭 ──────────────────────────────
        print("\n=== STEP 3: 동시 저장 버튼 클릭 ===")
        await asyncio.gather(
            click_save(page_a, ACCOUNT_A["label"], result_a),
            click_save(page_b, ACCOUNT_B["label"], result_b),
        )

        # ── STEP 4: 결과 출력 ──────────────────────────────────────
        print("\n=== 테스트 결과 ===")
        print(f"[{ACCOUNT_A['label']}] 입력 내용: {result_a.get('typed_content')}")
        print(f"[{ACCOUNT_B['label']}] 입력 내용: {result_b.get('typed_content')}")
        print(f"[{ACCOUNT_A['label']}] 저장 클릭 여부: {result_a.get('save_clicked')}")
        print(f"[{ACCOUNT_B['label']}] 저장 클릭 여부: {result_b.get('save_clicked')}")

        if result_a.get("error"):
            print(f"[{ACCOUNT_A['label']}] 오류: {result_a['error']}")
        if result_b.get("error"):
            print(f"[{ACCOUNT_B['label']}] 오류: {result_b['error']}")

        print("\n스크린샷이 현재 폴더에 저장되었습니다.")

        # 브라우저 종료 전 결과 확인용 대기
        await asyncio.sleep(5)

        await browser_a.close()
        await browser_b.close()


if __name__ == "__main__":
    asyncio.run(main())
