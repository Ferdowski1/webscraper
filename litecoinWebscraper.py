from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# Set up Selenium
options = Options()
options.add_argument("--headless") 
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start browser
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

URL = "https://finance.yahoo.com/quote/LTC-USD/history/?frequency=1wk&period1=1410912000&period2=1743810390"
COLUMNS = [
  "Week", "Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"
]

# Load the page
driver.get(URL)
time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
table = soup.find("table", class_="yf-1jecxey")

week = 1
all_data = []
for tr in table.find("tbody").find_all("tr"):
  row_data = []
  row_data.append(week)
  week += 1
  for td in tr.find_all("td"):
    row_data.append(td.text)

  all_data.append(row_data)
  
driver.quit()

df = pd.DataFrame(all_data, columns=COLUMNS)
df.to_csv("litecoin_weekly.csv", index=False, encoding="utf-8")