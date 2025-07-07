import time
import pyotp
import requests
import pandas as pd
from playwright.sync_api import sync_playwright
from urllib.parse import urlencode, urlparse, parse_qs 

class UpstoxAPI:
    BASE_URL_V2 = "https://api.upstox.com/v2"
    BASE_URL_V3 = "https://api.upstox.com/v3"
    
    # Define the required URLs
    login_url = "https://api.upstox.com/v2/login/authorization/dialog?"
    access_token_url = "https://api.upstox.com/v2/login/authorization/token"
    profile_logout = "https://api.upstox.com/v2/logout"

    def __init__(self, csv_path=None, row=None):
        if csv_path:
            self._load_credentials(csv_path)
        elif row is not None:
            self.api_key = str(row['api_key'])
            self.api_secret = str(row['api_secret'])
            self.redirect_uri = str(row['redirect_uri'])
            self.totp_secret = str(row['totp_secret'])
            self.mobile_number = str(row['mobile_number'])
            self.pin = str(row['pin'])
            self.client_id = str(row['client_id'])
        
        self.access_token = None
        self.refresh_token = None

    def _load_credentials(self, csv_path):
        """Load credentials from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            row = df.iloc[0]  # Assuming first row contains credentials
            self.api_key = str(row['api_key'])
            self.api_secret = str(row['api_secret'])
            self.redirect_uri = str(row['redirect_uri'])
            self.totp_secret = str(row['totp_secret'])
            self.mobile_number = str(row['mobile_number'])
            self.pin = str(row['pin'])
            self.client_id = str(row['client_id'])
        except Exception as e:
            print(f"Error loading credentials: {e}")

    # Get Access Token(call function 1)
    def get_login_url(self, API_KEY, REDIRECT_URI):
        params = {"response_type": "code", "client_id": API_KEY, "redirect_uri": REDIRECT_URI}
        login_url = f"{self.login_url}{urlencode(params)}"
        return login_url

    # Get Access Token(call function 2)
    def loging_web(self, login_url, REDIRECT_URI, mobile_No, PIN, OTP_key):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            with page.expect_request(f"*{REDIRECT_URI}?code*") as request:
                page.goto(login_url)
                page.locator("#mobileNum").fill(mobile_No)
                page.get_by_role("button", name="Get OTP").click()
                otp = pyotp.TOTP(OTP_key).now()
                page.locator("#otpNum").fill(otp)
                page.get_by_role("button", name="Continue").click()                
                page.get_by_label("Enter 6-digit PIN").fill(PIN)
                page.get_by_role("button", name="Continue").click()
                page.wait_for_load_state()
            
            url = request.value.url 
            parsed = urlparse(url)
            auth_code = parse_qs(parsed.query)['code'][0]

            context.close()
            browser.close()
            print(f"Authorization Code: {auth_code}")
            return auth_code

    # Get Access Token(call function 3)
    def get_access_token(self, auth_code, API_KEY, API_SECRET, REDIRECT_URI):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "client_id": API_KEY, 
            "client_secret": API_SECRET,
            "code": auth_code, 
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        }

        response = requests.post(self.access_token_url, headers=headers, data=urlencode(payload))
        return response.json() if response.status_code == 200 else response.json()['errors'][0]

    # Generate Authorization Code
    def get_access_automate(self, API_KEY, REDIRECT_URI, mobile_No, PIN, OTP_key, API_SECRET):
        params = {"response_type": "code", "client_id": API_KEY, "redirect_uri": REDIRECT_URI}
        login_url = f"{self.login_url}{urlencode(params)}"

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            with page.expect_request(f"*{REDIRECT_URI}?code*") as request:
                page.goto(login_url)
                page.locator("#mobileNum").fill(mobile_No)
                page.get_by_role("button", name="Get OTP").click()
                otp = pyotp.TOTP(OTP_key).now()
                page.locator("#otpNum").fill(otp)
                page.get_by_role("button", name="Continue").click() 
                page.get_by_label("Enter 6-digit PIN").fill(PIN)
                page.get_by_role("button", name="Continue").click()
                page.wait_for_load_state()
            
            url = request.value.url 
            parsed = urlparse(url)
            auth_code = parse_qs(parsed.query)['code'][0]

            context.close()
            browser.close()
            print(f"Authorization Code: {auth_code}")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "client_id": API_KEY, 
            "client_secret": API_SECRET, 
            "code": auth_code,
            "grant_type": "authorization_code", 
            "redirect_uri": REDIRECT_URI
        }

        response = requests.post(self.access_token_url, headers=headers, data=urlencode(payload))
        return response.json() if response.status_code == 200 else response.json()['errors'][0]

    # logout
    def logout_upstox(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        response = requests.delete(self.profile_logout, headers=headers)
        return response.json() if response.status_code == 200 else response.json()['errors'][0]