from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from datetime import datetime
import time
import tqdm
import pandas as pd
import os
import re
import pymssql
import logging
import numpy as np

import sys
sys.path.append('../')
from modules.transformer import Transformer
from modules.sender import Sender

calendar_match = {
    'janvier': '01',
    'février': '02',
    'mars': '03',
    'avril': '04',
    'mai': '05',
    'juin': '06',
    'juillet': '07',
    'août': '08',
    'septembre': '09',
    'octobre': '10',
    'novembre': '11',
    'décembre': '12'
}

class Scraper(Transformer, Sender):
    def __init__(self, date_to_reach, start_department, cookies_button_name, villes, env_variables, write_xls, show_chrome_gui=True):
        Transformer.__init__(self)
        Sender.__init__(self, env_variables)

        # self.results_dict = {"type_local": [], "valeur_fonciere": [], "value_per_sqm": [], "code_postal": [], "city": [], "district": []}
        self.properties_list_of_dicts = []
        self.dataframes_list = []
        self.write_xls = write_xls

        # Certains codes postaux sont répétés dans le fichier Excel, il faut donc les regrouper
        self.cities_df = pd.read_excel(villes)
        self.cities_df['latitude'] = pd.to_numeric(self.cities_df['latitude'], errors='coerce')
        self.cities_df['longitude'] = pd.to_numeric(self.cities_df['longitude'], errors='coerce')
        self.cities_df = self.cities_df.groupby('code_postal')[['latitude', 'longitude']].mean().reset_index()

        self.cookies_button_name = cookies_button_name
        self.show_chrome_gui = show_chrome_gui

        self.date_to_reach = datetime.strptime(date_to_reach, '%Y-%m-%d')
        self.start_department = start_department

        self.count_exceptions = 0
        self.break_loop = False

        try:
            self.create_SQL_table()
        except Exception as e:
            print('Did not create table (might already exist). See error log:\n')
            print(e)
    
    def import_chromedriver(self, path_to_chromedriver):
        if not self.show_chrome_gui:
            # Création d'une instance de ChromeOptions
            chrome_options = webdriver.ChromeOptions()
            # Add options to the chromedriver
            chrome_options.add_argument('--headless') # Don't show the GUI
            chrome_options.add_argument('--disable-gpu') # Don't show the GUI
            # chrome_options.add_argument('--disable-application-cache') # Disable the application cache
            self.driver = webdriver.Chrome(options=chrome_options) #(executable_path=path_to_chromedriver, options=options) 
        else:
            self.driver = webdriver.Chrome()

    def scrap_over_departments(self, url, path_to_chromedriver, html_element_of_interest, nextpage_button_class_name, max_pages, verbose=False):
        self.base_url = url

        departments = [str(i).zfill(2) for i in range(self.start_department,96)]#,3)]
        #departments = [str(i).zfill(2) + "000" for i in range(1,3 )]#96)]

        if not os.path.exists('dpt'):
            os.makedirs('dpt')

        for dep_num in tqdm.tqdm(departments):
            if int(dep_num) == 3:
                break

            print(f'\nProcessing department {dep_num}...')
            print('----------------------------------')
            self.dep_num = dep_num
            self.browse_current_department_pages(path_to_chromedriver, url, html_element_of_interest, nextpage_button_class_name, max_pages, verbose)

            self.properties_info_df = pd.DataFrame(self.properties_list_of_dicts)

            self.get_longitudes_latitudes()
            # self.dataframes_list.append(self.properties_info_df)

            # self.properties_info_df.to_csv(f'dpt/{dep}.csv', sep="`", index=False, encoding='utf-8')
            if self.write_xls:
                self.properties_info_df.to_excel(f'dpt/{dep_num}.xlsx', index=False)
            else:
                # self.send_to_db(self.properties_info_df)
                self.send_to_db(self.merged_table)
                print(f'|-----| Department {dep_num} sent to db.')
                # break

            # Réinitialiser la liste pour le prochain département
            self.properties_list_of_dicts = []

            time.sleep(2)
            #count_rows += 1

    def browse_current_department_pages(self, path_to_chromedriver, url, html_element_of_interest, nextpage_button_class_name, max_pages, verbose):
        '''
        Attributes
        ----------
        path_to_chromedriver : str
            Path to chromedriver
        url : str
            Url to scrape
        html_element_of_interest : str
            Class name of the element to get the text from
            class_name = 'resultsListContainer'
        nextpage_button_class_name : str
            Class name of the button to click on
            class_name = "goForward"
        ref_keyword : str
            Keyword to split the lines: 
            - Appartement
            - Maison
            - Terrain
        max_pages : int
            Number of pages to scrape
            max_pages = 10
        '''

        self.import_chromedriver(path_to_chromedriver)
        
        if self.show_chrome_gui:
            url = self.base_url.replace("departement", str(self.dep_num)).replace("page_num", str(1))
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 2) 
            # element = self.driver.find_element(By.ID, self.cookies_button_name)
            # element.click()
            bouton_accepter = wait.until(EC.visibility_of_element_located((By.ID, self.cookies_button_name)))
            bouton_accepter.click()

        # for page_num in tqdm.tqdm(range(1,max_pages+1)):
        for page_num in range(1,max_pages+1):
            print(f'Processing page {page_num}...')

            self.count_exceptions = 0
            
            ### Go to next page without GUI
            if not self.show_chrome_gui:
                url = self.base_url.replace("departement", str(self.dep_num)).replace("page_num", str(page_num))
                self.driver.get(url)

            if self.break_loop:
                self.count_exceptions = 0
                self.break_loop = False
                break

            # Is the element that should be cateched by extract_current_page_properties is present ?
            try:
                wait = WebDriverWait(self.driver, 30)  # Attendre jusqu'à 30 secondes
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, html_element_of_interest)))
                if verbose: print(f"Élément trouvé : {html_element_of_interest}")
            except TimeoutException:
                print(f"Élément non trouvé dans le temps imparti : {html_element_of_interest}")
                continue  # Passe à la page suivante si l'élément n'est pas trouvé

            # Get the element from the page
            self.extract_current_page_properties(html_element_of_interest, page_num, self.dep_num, verbose)

            ### Go to next page with GUI
            if self.show_chrome_gui:
                try:
                    element = self.driver.find_element(By.CLASS_NAME, nextpage_button_class_name)
                    element.click()
                except:
                    print(f"Process finished before page {max_pages}. Last page was: {page_num}")

            time.sleep(0.5)

        # If loop ends by reaching the last page, reset the count_exceptions
        self.count_exceptions = 0
        self.break_loop = False

        if self.show_chrome_gui:
            self.driver.close()

    def extract_current_page_properties(self, html_element_of_interest, page_num, dep_num, verbose=False):
        '''
        Attributes
        ----------
        class_name : str
            Class name of the element to get the text from
            class_name = 'resultsListContainer'
        '''

        # Trouver tous les articles de biens immobiliers sur la page
        properties = self.driver.find_elements(By.CSS_SELECTOR, f'article.{html_element_of_interest}')

        for idx, prop in enumerate(properties):
            # Utiliser l'attribut data-id comme clé unique pour chaque bien
            data_id = prop.get_attribute('data-id')
            ignore_prop = False
            
            # Initialiser un dictionnaire pour le bien courant
            prop_info = {}
            
            # Extraire les différentes informations
            try:
                title_element = prop.find_element(By.CSS_SELECTOR, 'h3.ad-overview-details__title')
            except:
                title_element = None
            try:
                title_text = title_element.text
            except:
                title_text = None
            try:
                price_element = prop.find_element(By.CSS_SELECTOR, 'span.ad-price__the-price')
            except:
                price_element = None
            try:
                price_per_sqm_element = prop.find_element(By.CSS_SELECTOR, 'span.ad-price__price-per-square-meter')
            except:
                price_per_sqm_element = None
            try:
                publication_date_element = prop.find_element(By.CSS_SELECTOR, 'div.photoPublicationDate')
            except:
                publication_date_element = None
            try:
                modification_date_element = prop.find_element(By.CSS_SELECTOR, 'div.photoModificationDate')
            except:
                modification_date_element = None
            try:
                reference_element = prop.find_element(By.CSS_SELECTOR, 'div.reference')
            except:
                reference_element = None
            try:
                description_element = prop.find_element(By.CSS_SELECTOR, 'div.ad-overview__description')
            except:
                description_element = None
            
            # Utilisation de regex pour extraire les données spécifiques du texte
            match = re.search(r'(\w+) (\d+) pièces (\d+) m²', title_text)
            # if match:
            try:
                prop_info['type_local'] = str(match.group(1))
            except:
                prop_info['type_local'] = None
            try:
                prop_info['nombre_pieces'] = int(match.group(2))
            except:
                prop_info['nombre_pieces'] = None
            try:
                prop_info['surface'] = int(match.group(3))
            except:
                prop_info['surface'] = None
            
            # Code postal et ville
            address_text = title_element.find_element(By.CSS_SELECTOR, 'span.ad-overview-details__address-title').text
            address_match = re.search(r'(\d{5})\s+(.+?)(?:\s+\((.+)\))?$', address_text)
            # if address_match:
            try:
                prop_info['code_postal'] = str(address_match.group(1))
            except:
                prop_info['code_postal'] = None
            try:
                prop_info['code_departement'] = str(self.dep_num)
            except:
                prop_info['code_departement'] = None
            try:
                prop_info['ville'] = str(address_match.group(2))
            except:
                prop_info['ville'] = None
            try:
                prop_info['quartier'] = str(address_match.group(3)) if address_match.group(3) else None
            except:
                prop_info['quartier'] = None
            
            # Prix au mètre carré
            try:
                prop_info['valeur_sqm'] = str(price_per_sqm_element.text.replace('€/m²', '').replace('\xa0', '').replace(' ', ''))
            except:
                prop_info['valeur_sqm'] = None
            # prop_info['prix_m2'] = int(price_per_sqm_text)

            # Prix
            try:
                # Extraire uniquement les chiffres de la chaîne de texte
                digits = ''.join(filter(str.isdigit, price_element.text))
                prop_info['valeur_fonciere'] = int(digits) if digits else None
            except:
                prop_info['valeur_fonciere'] = None

            # Dates
            try:
                prop_info['date_publication'] = str(publication_date_element.get_attribute('title').replace('1er', '1'))
            except:
                prop_info['date_publication'] = None
            try:
                prop_info['date_modification'] = str(modification_date_element.get_attribute('title').replace('1er', '1'))
            except:
                prop_info['date_modification'] = None

            # Dates reformat to yyyymmdd
            try:
                yyyy = prop_info['date_publication'].split(' ')[2]
                mm = calendar_match[prop_info['date_publication'].split(' ')[1].lower()]
                dd = prop_info['date_publication'].split(' ')[0]
                dd = f"{int(dd):02d}"
                prop_info['date_publication_yyyymmdd'] = str(f"{yyyy}-{mm}-{dd}")
            except:
                prop_info['date_publication_yyyymmdd'] = None
            try:
                yyyy = prop_info['date_modification'].split(' ')[2]
                mm = calendar_match[prop_info['date_modification'].split(' ')[1].lower()]
                dd = prop_info['date_modification'].split(' ')[0]
                dd = f"{int(dd):02d}"
                prop_info['date_modification_yyyymmdd'] = str(f"{yyyy}-{mm}-{dd}")
            except:
                prop_info['date_modification_yyyymmdd'] = None

            if prop_info['date_modification_yyyymmdd'] != None:
                current_date = datetime.strptime(prop_info['date_modification_yyyymmdd'], '%Y-%m-%d')
                if current_date < self.date_to_reach:
                    # stop process
                    if verbose: print(f'[dep: {dep_num} | page-idx: {page_num}-{idx}]: {current_date} < {self.date_to_reach}')
                    self.count_exceptions += 1
                    ignore_prop = True
                    if self.count_exceptions > 5:
                        self.break_loop = True
                        break

            # Référence
            try:
                prop_info['reference'] = str(reference_element.text.replace('Référence : ', '').strip())
            except:
                prop_info['reference'] = None
            
            # Description
            try:
                prop_info['description'] = str(description_element.text.replace('<br>', '\n').strip())
            except:
                prop_info['description'] = None
            
            try: 
                prop_info['agence'] = str(data_id)
            except:
                prop_info['agence'] = None

            # if verbose:
            #     print(prop_info)

            # Ajouter les informations du bien au dictionnaire principal
            try:
                # self.properties_info[data_id] = prop_info
                if prop_info['valeur_fonciere'] != None and prop_info['type_local'] != None and prop_info['code_postal'] and not ignore_prop:
                    self.properties_list_of_dicts.append(prop_info)

            except Exception as e:
                logging.error(f"Error occurred: {e}")
                print(e) # Temporary, debugging purposes
                print("") # Temporary, debugging purposes
                # raise(e) 