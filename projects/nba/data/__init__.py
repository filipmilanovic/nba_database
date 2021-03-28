from bs4 import BeautifulSoup
import requests as r
from selenium import webdriver  # used for interacting with webpages
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from statistics import mean

#  Set options for headless web driver
options = webdriver.ChromeOptions()
options.add_argument('--headless')

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' \
             '89.0.4389.90 Safari/537.36'
