"""
preprocessing.py
This source code is part of temp-monitoring program.
It contains the code to check and create a full database from the data 
stored in smaller datasets, adding extra features before merging them. 
"""

from pathlib import Path
from datetime import timedelta

import pandas as pd
from configparser import ConfigParser

parser = ConfigParser()
parser.read("config.ini")

class CheckMainDataset:
    """Checks if the main_dataset.csv exists in the /data
    folder. If it doesn't exist, it is created and the relevant
    columns are added.

    Args:
        str : path of the folder where the main dataset will be located.
        str (optional) : name of the file
    """
    
    def __init__(self, pathfolder, filename="main_dataset.csv"):
        self.pathfolder = Path(pathfolder)
        self.filename = filename
        self.columns = ['vehicle_id', 'vehicle_plate', 'date', 'driver', 
                        'longitude', 'out_speed', 'location', 'out_event_odo', 
                        'terminal_serial', 'ignition', 'temp1', 'temp2', 'temp3', 
                        'temp4', 'door1_status', 'door2_status', 't_longitude', 
                        'day_of_week', 'interval_time', 'hour', 'predicted_temp', 
                        'predicted_temp2']
        self.path_file = str(self.pathfolder) + "/" + str(self.filename)
        self.create_file()


    def create_file(self):
        """
        Checks if the main_dataset.csv exists in the folder it should
        be in. If it doesn't exist, it is created in the path declared into the instance 
        variable 'self.path_file'.
        """
        path = Path(self.path_file)
        if not path.is_file():
            main_df = pd.DataFrame(columns=self.columns)
            main_df.to_csv(self.path_file, index=False)        
            print("<main_dataset.csv> could not be found. A new file has been created.")    
        

    def __str__(self):
        return self.path_file


class ProcessingData:
    """This class is in charge of doing the data cleaning and feature engineering 
    from the main_dataset.
    
    Args:
        json_pathfile (str) : path where the .json is located.
        main_dataset_path (str) : path where the main_dataset will be saved. 
        limit_interval (float) : interval time that triggers uppsampler function. 
        default_interval (float) : interval time created between new entries out of limit interval.  
    """
    def __init__(self, json_pathfile, main_dataset_path):
        self.pathfile = json_pathfile
        self.main_df = pd.DataFrame()
        self.df = pd.read_json(json_pathfile)   
        self.main_dataset_path = main_dataset_path
        self.limit_interval = parser.getint("interval_time_config", "limit")  
        self.default_interval = parser.getint("interval_time_config", "default")
        self.df = self.feature_engineering(self.df)


    def feature_engineering(self, df):
        """
        Receives, renames and modifies a dataset, adding some attributes that 
        will be used later. It merges the actual dataframe with the previous value of
        instance variable 'self.df'. 
        
        Args:
            df (pd.Dataframe) : dataframe with database loaded.
        
        Returns:
            pd.Dataframe : dataframe modified with extra features and merged.
        """

        column_names = {"out_vehicle_id": "vehicle_id", 
                        "out_registration": "vehicle_plate",
                        "out_event_ts": "date", 
                        "out_driver": "driver", 
                        "out_longitude": "longitude",
                        "out_event_description": "location", 
                        "out_terminal_serial": "terminal_serial",
                        } 
        # Rename columns
        df.rename(columns=column_names, inplace=True)

        # Drop duplicates 
        df.drop_duplicates(subset="date", keep="last", inplace=True)  

        # Cast 'date' attribute into a datatime format.
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)

        # Generate extra attributes          
        df["day_of_week"] = df["date"].dt.day_name() 
        df["interval_time"] = df["date"].diff()
        df["hour"] = df["date"].dt.hour          
        df["ignition"] = df["ignition"].map({"t":1, "f":0})
        new_df = self.generate_df(df)
        df["interval_time"] = df["interval_time"].dt.total_seconds()

        # Merge the modified dataframe with the previous data.        
        df = new_df.merge(df, how="outer").sort_values(by="date").reset_index(drop=True)
          
        return df


    def merge_data_to_main_df(self):
        """
        Merge the resulting dataframe information to main_dataset.
        It modifies the instance variable 'self.main_df'.
        """
        main_df = pd.read_csv(self.main_dataset_path)
        main_df["date"] = pd.to_datetime(main_df["date"])               
        main_df["interval_time"] = pd.to_timedelta(main_df["interval_time"]).dt.total_seconds()      
        main_df = self.df.merge(main_df, how="outer").sort_values(by="date").reset_index(drop=True)       
        main_df.drop_duplicates(subset="date", keep="first", inplace=True) 
        main_df.reset_index(drop=True, inplace=True)
        main_df.to_csv(self.main_dataset_path, index=False)
        
        self.main_df = main_df
        
    @staticmethod
    def run_upsampler(df, limit_interval, default_interval):
        """
        Receives a dataframe, identifies time intervals between two consecutive
        entries that are greater than the selected limit and where these exist, 
        new time intervals are created so that all intervals between consecutive
        entries are at equal to under the selected limit. Returns a list with new
        dates and pre-established values for necessary attributes. The last element
        in the list is a True value for the real data, to differenciate between
        real and synthesised data.
        
        Args:
            df (pd.Dataframe) : dataset with data loaded.
            limit_interval (float) : limit in minutes to trigger uppsampler function. 
            default_interval (float) : interval time in minutes created between new 
                                    entries out of limit interval.
        
        Returns:
            list : nested list with new entries for the dataset.
        """

        list_new_dates = []
        # Iterates through the dataframe to obtain intervals.
        for i in range(0, len(df)-1):
            if df["interval_time"].iloc[i] > timedelta(minutes=limit_interval):
                start_date = df["date"].iloc[i]
                end_date = df["date"].iloc[i+1]
                interval = (end_date - start_date).total_seconds()/60

                # Generates a dataframe with time intervals based on the stipulated interval limit.
                range_dates = pd.date_range(start=start_date, 
                                            end=end_date, 
                                            periods=int(interval/default_interval), 
                                            inclusive="neither") 

                # Iterates through each new date generated, adding attributes
                # to a new list. New attributes can be added as necessary. 
                for new_date in range_dates:
                    list_new_dates.append([new_date,       
                                            df["vehicle_id"].iloc[i], df["vehicle_plate"].iloc[i],
                                            df["door1_status"].iloc[i], df["door2_status"].iloc[i],
                                            df["ignition"].iloc[i], True])      
        
        return list_new_dates  


    def generate_df(self, df):
        """Receives a dataframe with our data and generates a new one after 
        upsampling which will be merged togther. Returns a more complete
        dataframe.

        Args:
            df (pd.Dataframe) : dataframe with our database loaded.

        Returns:
            pd.Dataframe : dataframe with additional attributes.
        
        """

        columns = [
            "date", "vehicle_id", "vehicle_plate", "door1_status", 
            "door2_status", "ignition", "date_flag"
        ]
        new_df = pd.DataFrame(self.run_upsampler(df, self.limit_interval, 
                                                 self.default_interval), 
                                                 columns=columns)
        
        # Generates new attribute capable of being used as regressors 
        new_df["day_of_week"] = new_df["date"].dt.day_name()
        new_df["date"] = new_df['date'].astype('datetime64[s]')     

        return new_df