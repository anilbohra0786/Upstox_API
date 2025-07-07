import os
import time
import pandas as pd
from pathlib import Path
from dependency.upstox_V3 import UpstoxAPI

# Define paths
basepath = Path(os.getcwd()).parent
apikey_filepath = f"{basepath}/Codes/dependency/accounts.csv"
token_path = f"{basepath}/token/access_token.csv"

# Load credentials from CSV
apikeydf = pd.read_csv(apikey_filepath)

# Extract values
API_KEY = apikeydf['api_key'].iloc[0]
API_SECRET = apikeydf['api_secret'].iloc[0]
REDIRECT_URI = apikeydf['redirect_uri'].iloc[0]
mobile_No = str(apikeydf['mobile_number'].iloc[0])
PIN = str(apikeydf['pin'].iloc[0])
OTP_key = str(apikeydf['totp_secret'].iloc[0])

# Create instance and get token
upstox_api = UpstoxAPI()
token_data = upstox_api.get_access_automate(API_KEY, REDIRECT_URI, mobile_No, PIN, OTP_key, API_SECRET)

# Save access_token
if token_data:
    print(f"Saving Access Token...{token_data}")
    if "user_id" in token_data and "access_token" in token_data:
        df = pd.DataFrame([{
            "client_id": token_data["user_id"],
            "access_token": token_data["access_token"],
            "api_key": API_KEY
        }])
        df.to_csv(token_path, index=False)
        print("✅ Access token saved successfully!")
    else:
        print("❌ Invalid token data received.")
else:
    print("❌ Token generation failed!")
