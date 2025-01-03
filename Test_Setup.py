# from selenium import webdriver

# # Initialize the Chrome WebDriver
# driver = webdriver.Chrome()

# # Open a webpage
# driver.get("https://www.google.com")

# print("Title of the page is:", driver.title)

# # Close the browser
# driver.quit()



from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Open a webpage
driver.get("https://www.google.com")

print("Title of the page is:", driver.title)

# Close the browser
driver.quit()

