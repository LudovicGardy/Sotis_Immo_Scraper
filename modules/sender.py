# Importations nécessaires
import logging
import os
import pandas as pd
import json
from google.cloud import bigquery
from google.oauth2 import service_account


class Sender:
    def __init__(self, env_variables):
        print('Init sender...')
        # Configuration pour BigQuery
        self.project_id = env_variables.get('BIGQUERY_PROJECT_ID')
        self.dataset_id = env_variables.get('BIGQUERY_DATASET_ID')
        self.table_id = env_variables.get('BIGQUERY_TABLE')

        # Configuration de l'authentification avec variables d'environnement
        credentials_dict = {
            "type": env_variables.get('TYPE'),
            "project_id": env_variables.get('PROJECT_ID'),
            "private_key_id": env_variables.get('PRIVATE_KEY_ID'),
            "private_key": env_variables.get('PRIVATE_KEY').replace("/breakline/", "\n"),
            "client_email": env_variables.get('CLIENT_EMAIL'),
            "client_id": env_variables.get('CLIENT_ID'),
            "auth_uri": env_variables.get('AUTH_URI'),
            "token_uri": env_variables.get('TOKEN_URI'),
            "auth_provider_x509_cert_url": env_variables.get('AUTH_PROVIDER_X509_CERT_URL'),
            "client_x509_cert_url": env_variables.get('CLIENT_X509_CERT_URL'),
            "universe_domain": env_variables.get('UNIVERSE_DOMAIN')
        }

        # Créer un fichier JSON temporaire pour stocker les credentials et les envoyer à BigQuery
        credentials_path = 'temp_credentials.json'
        with open(credentials_path, 'w') as credentials_file:
            json.dump(credentials_dict, credentials_file)

        # Utiliser le fichier JSON temporaire pour créer les credentials
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = bigquery.Client(credentials=credentials, project=self.project_id)

        # Supprimer le fichier temporaire après utilisation
        os.remove(credentials_path)

    def create_SQL_table(self):
        # Code pour créer une table dans BigQuery avec un schéma complet
        schema = [
            bigquery.SchemaField("type_local", "STRING"),
            bigquery.SchemaField("nombre_pieces", "INTEGER"),
            bigquery.SchemaField("surface", "INTEGER"),
            bigquery.SchemaField("code_postal", "STRING"),
            bigquery.SchemaField("code_departement", "STRING"),
            bigquery.SchemaField("ville", "STRING"),
            bigquery.SchemaField("quartier", "STRING"),
            bigquery.SchemaField("valeur_sqm", "STRING"),
            bigquery.SchemaField("valeur_fonciere", "INTEGER"),
            bigquery.SchemaField("date_publication", "STRING"),
            bigquery.SchemaField("date_modification", "STRING"),
            bigquery.SchemaField("date_publication_yyyymmdd", "STRING"),
            bigquery.SchemaField("date_modification_yyyymmdd", "STRING"),
            bigquery.SchemaField("reference", "STRING"),
            bigquery.SchemaField("description", "STRING"),
            bigquery.SchemaField("agence", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT")
        ]

        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
        table = bigquery.Table(table_ref, schema=schema)
        table = self.client.create_table(table, exists_ok=True)  # Crée la table si elle n'existe pas

        print(f"Table {table.table_id} created successfully.")

    def send_to_db(self, dataframe):
        '''
        Note : there is no simple way to check for duplicates in BigQuery.
        A request by line would be necessary and cost inefficient.
        Might be better to do the request at loading time.
        '''

        # Code pour envoyer des données à BigQuery
        table_id = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        job = self.client.load_table_from_dataframe(dataframe, table_id)
        job.result()  # Attend la fin du job
        print("Data sent to BigQuery successfully.")