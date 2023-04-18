"""
dataloader.py
This source code is part of temp-monitoring program.
It contains the code to check for the existence of the main dataset, loading all the 
data contained in the .json files into different datasets that will be merged in
one complete database with both, real and predicted data.
It also creates the prophet's model data for each vehicle. 
"""

from pathlib import Path

import pandas as pd
from configparser import ConfigParser

from data.preprocessing import CheckMainDataset, ProcessingData
from prophet_folder.modelo_main import ProphetModel
from prophet_folder.prediction_maker import PredictTempForNaN, MergePredictions

parser = ConfigParser()
parser.read("config.ini")
my_path = Path.cwd()

class MainDataset: 
    """
    Using the path defined in the config class, all the json files
    in the json_folder are merged into one dataframe called main_dataset.csv.
    """
    def __init__(self):
        self.pred_container = pd.DataFrame()
        self.main_dataset_path = self.get_main_dataset_path()
        self.main_dataset = self.set_main_dataset()
        self.run_prophet_models(self.main_dataset)
        self.get_predictions()
        self.main_dataset = self.merge_predictions()


    def get_main_dataset_path(self):
        """
        Checks if the main_dataset.csv exists in the pathspecified in 
        the config class. If it doesn't, the file is generated.

        Returns: 
            str : path of the new main_dataset.csv file
        """
        saved_path = parser.get("path_folder", "main_dataset")
        absolut_path = str(my_path)+saved_path
        main_dataset_path = str(CheckMainDataset(absolut_path))     
        
        return main_dataset_path


    def set_main_dataset(self):
        """
        All the json files in the folder specified in the config
        class are processed and merged into a single main_dataset.

        Returns:
            pd.Dataframe : merged dataframe with all data from every vehicle.
        """
        saved_path = parser.get("path_folder", "json_files")
        absolut_path = str(my_path)+saved_path
        for json_file in Path(absolut_path).iterdir():                    
            dataset = ProcessingData(json_file, self.main_dataset_path)
            dataset.merge_data_to_main_df()
        
        main_dataset = dataset.main_df

        return main_dataset


    @staticmethod
    def run_prophet_models(main_dataset):
        """
        Prepares the content of main_dataset to be passed to the Prophet algorithm, creating model files 
        for each vehicle if it doesn't exist.
        """
        objeto = ProphetModel(main_dataset)
        objeto.run_model()


    def get_predictions(self):
        """
        Iterates for every vehicle plate, creating a new filtered dataframe with all
        the NaN values to be passed to our trained model.
        Collect and concatenate all the predicted data for every vehicle plate into 
        the new dataframe. 
        Returns a modified instance variable 'self.pred_container' with the results 
        of all the predictions.
        """ 
        pred_container = pd.DataFrame(columns=['date','predicted_temp',
                                            'vehicle_plate'
                                                ])

        for v_plate in self.main_dataset["vehicle_plate"].unique():
            df_veh_plate = self.main_dataset[self.main_dataset["vehicle_plate"] == v_plate]
            mask1 = df_veh_plate["y"].isna()    
            df_to_predict = df_veh_plate[mask1]        
            prediction = PredictTempForNaN(df_to_predict, v_plate).predict_result
            pred_container = pd.concat([pred_container, prediction], 
                                        join='outer',
                                        ignore_index=True,
                                        )
                                    
        self.pred_container = pred_container


    def merge_predictions(self):
        """
        Merges all the predections with the orginal main-dataset.
        
        Returns:
            pd.dataframe : a dataframe with real and predicted data.
        """
        merged_df = MergePredictions(self.pred_container, self.main_dataset).df
        merged_df.rename(columns = {'y': 'temp1'}, inplace=True)
        merged_df.sort_values('date', inplace=True)
        merged_df["date"] = merged_df["date"].dt.floor("T")
        merged_df.to_csv(self.main_dataset_path, index=False)

        return merged_df