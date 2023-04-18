"""
prediction_maker.py
This source code is part of temp-monitoring program.
It contains the code to open the models for every vehicle and launch the predictions.
It also merge this new prediction results into the main_dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path

from prophet.serialize import model_from_json
from configparser import ConfigParser

parser = ConfigParser()
parser.read("config.ini")
my_path = Path.cwd()


class PredictTempForNaN:
  """
  Class that receives, per vehicle, the nested list of dates where temperature data is missing
  and the dataset with all the entries. The class makes predictions of missing temeperature
  data for corrresponding dates using the saved model for this vehicle. The end result is a dataframe
  for each vehicle that includes the dates that had missing values and the corresponding 
  temperature prediction.

  Args: 
    pd.Dataframe : dataframe with data filtered per vehicle plate.
    string : vehicle plate that will be used to load the saved prophet model.
  """
  def __init__(self, df, vehicle_plate):
    # self.config = Config()
    self.df = df
    self.vehicle_plate = vehicle_plate
    self.model = self.prophet_model_loader()
    self.predict_result = self.get_prediction()

  
  def prophet_model_loader(self):
    """
    Opens the corresponding prophet model for the selected vehicle plate. The path is allocated in the 
    'self.config' instance variable.
    
    Returns:
      prophet.model.object : 
    """
    absolute_path = str(my_path)+parser.get("path_folder", "model_file")
    with open(absolute_path.format(self.vehicle_plate), 'r') as fin:
      model = model_from_json(fin.read())

    return model


  def get_prediction(self):
    """
    Passes a dataframe with the entries is going to be predicted. Returns the predictions made by the model for the missing temperature 
    data for the vehicle.

    Returns:
      pd.Dataframe : dataframe with the predicted temp.
    """
    # Prepares the dataframe
    df_dates = self.df.loc[:,"ds"].to_frame(name="ds")

    # Makes a prediction
    forecast = self.model.predict(df_dates)

    # Substract columns 'ds' and 'yhat' for the predicted dataframe
    predict_result = forecast[['ds','yhat']]

    # Create a new attribute with the vehicle plate and prepare the dataframe to be returned.
    predict_result['vehicle_plate'] = self.vehicle_plate
    predict_result.rename(columns = {'ds': 'date', 
                                    'yhat': 'predicted_temp'}, 
                          inplace=True
                          )
    predict_result["predicted_temp"] = predict_result["predicted_temp"].round(1)
    predict_result["date"] = predict_result['date'].astype('datetime64[s]')

    return predict_result


class MergePredictions:
  """
  Class that takes the predictions for all the vehicles (concatenated in one file)
  and merges them into the main dataset. Ensures that all the predictions are in one
  column (named predicted_temp). Renames columns to ensure coherent naming. The final
  database only includes the relevant columns.
  
  Args:
    pd.Dataframe : dataframe with predictions made previously.
    pd.Dataframe : main_dataset with temp data and empy temp entries.
  """
  def __init__(self, predictions, main_df):
    self.prediction = predictions
    self.df = self.rename_columns(main_df)


  def rename_columns(self, df):
    """
    Takes the dataframe and renames the columns created after the predictions,
    to then merge them to the main dataset.

    Args:
      pd.Dataframe : dataframe with all predicted values and temp values.

    Returns: 
      pd.Dataframe : dataframe with columns renamed, ready to analyze and plot.
    """
    df.rename(columns = {'ds': 'date'}, inplace=True)
    self.prediction["date"] = pd.to_datetime(self.prediction["date"]).dt.tz_localize(None)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    merged_df = pd.merge(self.prediction, df,  how='outer', left_on=['date', 'vehicle_plate'], right_on=['date', 'vehicle_plate'])
    merged_df['temp1'] = merged_df['y']
    merged_df["predicted_temp"] = np.nan
    merged_df["predicted_temp"].fillna(merged_df["predicted_temp_x"], inplace=True)
    merged_df["predicted_temp"].fillna(merged_df["predicted_temp_y"], inplace=True)
    merged_df.rename(columns={"ignition_y": "ignition",
                          "temp2_y":"temp2", 
                          "interval_time_y":"interval_time",
                          "hour_y":"hour", 
                          "day_of_week_y":"day_of_week",
                          "predicted_temp2_x":"predicted_temp2",
                          "vehicle_id_y":"vehicle_id", 
                          }, 
                      inplace=True)
    merged_df = merged_df[["date", "vehicle_plate", "vehicle_id", 
                          "date_flag", "temp1", "temp2", "ignition", 
                          "interval_time", "hour", "day_of_week",
                          "predicted_temp", "predicted_temp2"]
                          ]
    
    return merged_df