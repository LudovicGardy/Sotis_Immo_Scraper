import json
import sys

sys.path.append('../')
from modules.config import data_URL, user_config, scraper_config, load_configurations
from modules.scraper import Scraper

# Appending the parent directory to the system path for importing local modules
env_variables = load_configurations()

# Extraire les paramètres
date_to_reach = user_config().get('date_to_reach')
start_department = user_config().get('start_department')

print("Starting main.py...") # DEBUG: send to log later
print(f"date_to_reach: {date_to_reach}") # DEBUG: send to log later
print(f"start_department: {start_department}") # DEBUG: send to log later
print("") # DEBUG: send to log later

path_to_chromedriver = scraper_config().get('path_to_chromedriver')
html_element_of_interest = scraper_config().get('html_element_of_interest')
nextpage_button_class_name = scraper_config().get('nextpage_button_class_name')
cookies_button_name = scraper_config().get('cookies_button_name')
max_pages = scraper_config().get('max_pages')

url = data_URL()['source']
villes = data_URL()['villes']
CD = Scraper(date_to_reach, start_department, cookies_button_name, villes, env_variables, write_xls=False, show_chrome_gui=False)
CD.scrap_over_departments(url, path_to_chromedriver, html_element_of_interest, nextpage_button_class_name, max_pages, verbose=True)

