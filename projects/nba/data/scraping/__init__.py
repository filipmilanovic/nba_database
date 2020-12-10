from bs4 import BeautifulSoup
from selenium import webdriver  # used for interacting with webpages

#  Set options for headless web driver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
