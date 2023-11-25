from dotenv import dotenv_values
import os
import sys

sys.path.append('../')
env_variables = dotenv_values('.env')

### CONFIGURATION ###
def user_config():

    user_config_dict = {
        "date_to_reach": "2023-11-23", # "yyyy-mm-dd"
        "start_department": 1 # from 1 to 95
    }

    return user_config_dict

def scraper_config():

    scraper_config_dict = {
        "path_to_chromedriver": r'drivers/chromedriver_mac_arm64/chromedriver',
        "html_element_of_interest": 'sideListItem', #'article.sideListItem'
        "nextpage_button_class_name": "goForward",
        "cookies_button_name": "didomi-notice-agree-button",
        "max_pages": 2
    }

    return scraper_config_dict

def data_URL():
    '''
    Set the URLs to the data sources.
    '''

    data_dict = {
        'source': '{source_url}/{departement}/{local_types}?page={page_num}&mode=liste&tri=publication-desc'.format(source_url=env_variables["SOURCE_URL"], local_types=env_variables["LOCAL_TYPES"], departement="departement", page_num="page_num"),      
        'villes': f'{env_variables["AWS_S3_URL"]}/villes.xls'
    }

    return data_dict