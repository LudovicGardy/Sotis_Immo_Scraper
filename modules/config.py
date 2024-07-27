from dotenv import load_dotenv, find_dotenv
import os
import sys

def load_configurations():
    """
    Charge uniquement les variables du fichier .env si celui-ci est présent.
    Si le fichier .env n'existe pas, charge toutes les variables d'environnement du système.
    """
    dotenv_path = find_dotenv('.env')

    if dotenv_path:
        # Le fichier .env existe, charger uniquement ses variables
        load_dotenv(dotenv_path)
        # Retourne les variables chargées depuis le .env
        return {key: os.environ[key] for key in os.environ if key in open(dotenv_path).read()}
    else:
        # Le fichier .env n'existe pas, retourne toutes les variables d'environnement du système
        return dict(os.environ)

### CONFIGURATION ###
def user_config():

    user_config_dict = {
        "date_to_reach": "2023-11-01", # "yyyy-mm-dd"
        "start_department": 1 # from 1 to 95
    }

    return user_config_dict

def scraper_config():

    scraper_config_dict = {
        "path_to_chromedriver": r'drivers/chromedriver_mac_arm64/chromedriver',
        "html_element_of_interest": 'sideListItem', #'article.sideListItem'
        "nextpage_button_class_name": "goForward",
        "cookies_button_name": "didomi-notice-agree-button",
        "max_pages": 100 # max 100
    }

    return scraper_config_dict

def data_URL():
    '''
    Set the URLs to the data sources.
    '''

    env_variables = load_configurations()

    data_dict = {
        'source': '{source_url}/{departement}/{local_types}?page={page_num}&mode=liste&tri=publication-desc'.format(source_url=env_variables["SOURCE_URL"], local_types=env_variables["LOCAL_TYPES"], departement="departement", page_num="page_num"),      
        'villes': f'{env_variables["AWS_S3_URL"]}/villes.xls'
    }

    return data_dict