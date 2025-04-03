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

URL = "https://www.premierleague.com/clubs"
COLUMNS = [
  "name", "number", "nation", "appearances", "goals", "assists", "shots", "big_chances_created",
  "clean_sheets", "saves", "goals_conceded", "player_image", "nation_flag", "team", "position"
]

# Load the page
driver.get(URL)

# Wait for JavaScript to load
time.sleep(5)

# Get the HTML after rendering
html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

clubs = soup.find("div", class_="clubIndex col-12")
clubs_ul = clubs.find("ul")
clubs_list = clubs_ul.find_all("li", class_="club-card-wrapper")

all_players = []

for club in clubs_list:
  a_tag = club.find("a")
  club_url = a_tag.get("href")
  club_url = club_url.replace("/clubs", "").replace("overview", "squad?se=719")
  squad_url = URL + club_url
  squad_url_parts = squad_url.split("/")
  team = squad_url_parts[-2].replace("-", " ")

  driver.get(squad_url)
  time.sleep(5)

  # Get squad page HTML
  squad_html = driver.page_source
  squad_soup = BeautifulSoup(squad_html, "html.parser")
  squad_list = squad_soup.find("ul", class_="squadListContainer squad-list")

  position_containers = squad_list.find_all("div", class_="squad-list__position-container")

  for index, div in enumerate(position_containers):
    ul = div.find("ul")
    li_elements = ul.find_all("li", class_="stats-card")

    for li in li_elements:
      player_data = ["0"] * 15
      text = li.get_text(separator=" ", strip=True)
      text_split = text.split(" ")
      
      if index == 0: # Goalies
        player_data[8] = text_split[4]  # clean sheets
        player_data[9] = text_split[6]  # saves
        player_data[10] = text_split[9] # goals conceeded
      
      else:
        if index == 1:
          player_data[8] = text_split[8] # clean sheets

        elif index == 2:
          player_data[7] = text_split[9] # big chances created
        
        else:
          player_data[6] = text_split[7] # shots

        player_data[4] = text_split[3]   # goals
        player_data[5] = text_split[5]   # assists

      name = text_split[-7] if text_split[-8].isdigit() else text_split[-8] + " " + text_split[-7]
      player_data[0] = name             # name
      player_data[1] = text_split[-6]   # number 
      player_data[2] = text_split[-3]   # nation
      player_data[3] = text_split[1]    # appearances
      player_data[14] = text_split[-5]  # position
      player_data[13] = team            # team

      player_img = li.find("img", class_="statCardImg statCardPlayer").get("src")
      player_data[11] = player_img      # player image

      nation_flag = li.find("img", class_="stats-card__flag-icon").get("src")
      player_data[12] = nation_flag

      all_players.append(player_data)

driver.quit()

df = pd.DataFrame(all_players, columns=COLUMNS)
df.to_csv("all_players_data.csv", index=False, encoding="utf-8")
