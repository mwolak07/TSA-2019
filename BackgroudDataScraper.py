from google_images_download import google_images_download
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Starting chromdriver in headless mode with selenium
options = Options()
options.headless = True
driver = webdriver.Chrome("chromedriver.exe", options=options)

# Creating arguments dictionary for high school interior image search
arguments = {"chromedriver": driver, "keywords": "high school interior"}
# Initializing google images search
response = google_images_download.googleimagesdownload()
# Searching for high school interior pictures according to arguments, storing paths to images in path variable
paths = response.download(arguments)
print(paths)

# Creating arguments dictionary for store interior image search
arguments = {"chromedriver": driver, "keywords": "store interior"}
# Initializing google images search
response = google_images_download.googleimagesdownload()
# Searching for store interior pictures according to arguments, storing paths to images in path variable
paths = response.download(arguments)
print(paths)
