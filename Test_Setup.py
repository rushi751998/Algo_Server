from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from server.loginmgmt.session_manger import SessionManager
from server.Utils.Path import Path

Path.load()
SessionManager.load_credentials()

chatId = SessionManager.User_Config['chatId']
bot_id = SessionManager.User_Config['emergency_bot']


# Initialize the Chrome WebDriver
driver = webdriver.Chrome()



options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# For Linux
driver = webdriver.Chrome(options=options)

# # For Windows
driver.get("https://www.google.com")





# # Close the browser



import requests



# The message you want to send
MESSAGE = str(driver.title)


# Telegram API URL
url = f"https://api.telegram.org/bot{bot_id}/sendMessage"

# Data to send
payload = {
    "chat_id": chatId,
    "text": MESSAGE
}

# Send the message
response = requests.post(url, data=payload)

# Print the response (optional)
print(response.json())

driver.quit()