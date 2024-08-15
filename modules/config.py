from dotenv import load_dotenv, find_dotenv
import os


def load_configurations():
    """
    Only load the variables from the .env file if it exists.
    If the .env file does not exist, load all the system environment variables.
    """
    dotenv_path = find_dotenv(".env")

    if dotenv_path:
        # The .env file exists, load only its variables
        load_dotenv(dotenv_path)
        # Return the variables loaded from the .env
        return {
            key: os.environ[key]
            for key in os.environ
            if key in open(dotenv_path).read()
        }
    else:
        # The .env file does not exist, return all the system environment variables
        return dict(os.environ)


def user_config():
    user_config_dict = {
        "date_to_reach": "2023-11-01",  # "yyyy-mm-dd"
        "start_department": 1,  # from 1 to 95
    }

    return user_config_dict


def scraper_config():
    scraper_config_dict = {
        "path_to_chromedriver": r"drivers/chromedriver_mac_arm64/chromedriver",
        "html_element_of_interest": "sideListItem",  #'article.sideListItem'
        "nextpage_button_class_name": "goForward",
        "cookies_button_name": "didomi-notice-agree-button",
        "max_pages": 100,  # max 100
    }

    return scraper_config_dict


def data_URL():
    """
    Set the URLs to the data sources.
    """

    env_variables = load_configurations()

    data_dict = {
        "source": "{source_url}/{departement}/{local_types}?page={page_num}&mode=liste&tri=publication-desc".format(
            source_url=env_variables["SOURCE_URL"],
            local_types=env_variables["LOCAL_TYPES"],
            departement="departement",
            page_num="page_num",
        ),
        "villes": f'{env_variables["AWS_S3_URL"]}/villes.xls',
    }

    return data_dict
