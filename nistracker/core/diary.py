import asyncio
from datetime import datetime
from seleniumrequests import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class DiaryDriver(Chrome):
    def __init__(self):
        self.ready = False  # Shows if loginpage is opened
        self.login_result_dict = dict()

        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')  # Disable automation control
        options.add_argument('--no-sandbox')  # Bypass OS security model
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')  # Set a custom user-agent
        options.add_argument("--headless")

        super().__init__(service=Service(ChromeDriverManager().install()), options=options)

    async def open_loginpage(self):
        self.base_url = "https://crashed-nis.vercel.app/"
        await asyncio.to_thread(self.get, url=self.base_url + "login/")
    
    # Returns the login status in format (Logged in: boolean, message: string)
    async def login(self, pin: str, password: str, timeout=8):
        self.find_element("id", ":R6brqla:-form-item").send_keys(pin)
        self.find_element("id", ":Rabrqla:-form-item").send_keys(password)
        self.find_element(
            by="css selector",
            value=".inline-flex.items-center.justify-center"
        ).click()

        start_time = datetime.now()
        while True:
            if self.current_url.startswith(self.base_url + "dash"):
                return (True, "Logged in successfully")
            
            if len(self.find_elements("id", ":Rabrqla:-form-item-message")) > 0:
                return (False, f"Error: {self.find_element("id", ":Rabrqla:-form-item-message").text}")

            if (datetime.now() - start_time).total_seconds() > timeout:
                return (False, "Waiting limit exceeded. Try again")

            await asyncio.sleep(0.1)

    # Ensure you logged in successfully
    async def get_diary(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }
        response = await asyncio.to_thread(self.request, "GET", "https://crashed-nis.vercel.app/api/journal", headers=headers)
        return response.json()
    
    async def get_subject_mark(self, diary, quarter, eng_name):
        subject_id = None
        for subject in diary[quarter]["subjects"]:
            if subject["name"]["en"] == eng_name:
                subject_id = subject["id"]
        
        if subject_id is None:
            return None

        url = f"https://crashed-nis.vercel.app/api/journal/{subject_id}?quarter={quarter}"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }
        response = await asyncio.to_thread(self.request, "GET", url, headers=headers)
        return response.json()

    def __del__(self):
        self.quit()
