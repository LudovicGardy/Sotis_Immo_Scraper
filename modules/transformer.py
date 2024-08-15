import pandas as pd


class Transformer:
    """
    The Transformer class is responsible for transforming property data,
    merging it with city data, and preparing it for database insertion.
    """

    def __init__(self):
        print("Init transformer...")

    def get_longitudes_latitudes(self):
        """
        Processes property data and merges it with city data to obtain longitudes and latitudes.
        The method also cleans and prepares the data for further processing or database insertion.
        """

        # Creating a clean copy of the properties_info_df to avoid modifications on the original view.
        # Dropping duplicates based on specified columns.
        self.properties_info_df_clean = self.properties_info_df.drop_duplicates(
            subset=["type_local", "valeur_fonciere", "code_postal", "surface"]
        ).copy()

        # Ensuring the postal codes are in string format for both dataframes.
        self.properties_info_df_clean["code_postal"] = self.properties_info_df_clean[
            "code_postal"
        ].astype(str)
        self.cities_df["code_postal"] = self.cities_df["code_postal"].astype(str)

        # Padding postal codes with leading zeros in the cities dataframe for consistency.
        self.cities_df["code_postal"] = self.cities_df["code_postal"].apply(
            lambda x: x.zfill(5)
        )

        # Merging the cleaned property dataframe with the cities dataframe on postal codes.
        # 'inner' join ensures that only matching records are merged.
        self.merged_table = pd.merge(
            self.properties_info_df_clean,
            self.cities_df[["code_postal", "latitude", "longitude"]],
            on="code_postal",
            how="inner",
        )

        # Converting the merged dataframe into a list of dictionaries.
        # This format is typically more convenient for database operations.
        self.properties_list_of_dicts = self.merged_table.to_dict(orient="records")

        # Optional: Uncomment the following line if you need to replace NaN values with None.
        # This can be useful for database insertions where NaN is not a valid value.
        # self.properties_list_of_dicts = [
        #     {k: (None if pd.isna(v) else v) for k, v in property_dict.items()}
        #     for property_dict in self.properties_list_of_dicts
        # ]
