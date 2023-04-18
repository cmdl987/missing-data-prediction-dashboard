"""
prediction_maker.py
This source code is part of temp-monitoring program.
It contains the code to calculate and select the best hyperparameters for
every model that would be created for every vehicle plate.
All the hyperparameters, as the results, are saved inside '/prophet_folder'.
"""

import warnings
import json
import itertools
from pathlib import Path
from datetime import datetime

import pandas as pd
from prophet import Prophet
from matplotlib import pyplot as plt
from sklearn.metrics import r2_score
from prophet.diagnostics import cross_validation, performance_metrics
from prophet.serialize import model_to_json
from prophet.utilities import regressor_coefficients
import numpy as np
from configparser import ConfigParser

warnings.simplefilter('ignore')
parser = ConfigParser()
parser.read("config.ini")
my_path = Path.cwd()

class ProphetModel:
  """
  Receives a dataset and prepares the data before sending it to the Prophet
  algorithm to create the best model for every vehicle plate.
  
  Args:
    pd.Dataframe : dataframe where to run the model from.  
  """
  def __init__(self, main_df):
    self.main_df = self.rename_features(main_df)
    self.p_best_params = str(my_path)+parser.get("path_folder", "best_params")
    self.p_regrs_coef_path = str(my_path)+parser.get("path_folder", "regressors_coef")
    self.p_model_file = str(my_path)+parser.get("path_folder", "model_file")
    self.p_figures_folder = str(my_path)+parser.get("path_folder", "saved_figures")
    self.perf_metrics = str(my_path)+parser.get("path_folder", "perf_metrics")
    self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    

  def rename_features(self, main_df):
    """
    Renames the columns according to Prophet nomenclature.
    
    Args:
      pd.Dataframe: dataframe with columns without appropiate format for Prophet.

    Returns:
      pd.Dataframe : dataframe with columns renamed properly.
    """
    main_df.rename(columns={"temp1" : "y", "date": "ds"}, inplace=True)
    
    return main_df
  

  def run_model(self):
    """
    Detects if a model has been saved for each vehicle.
    If a model doesn't exits for a vehicle, it is generated with the best
    comnination of hyperpareters and saved.
    """
    # Iterates for every vehicle plate in the dataset. 
    for veh_plate in self.main_df["vehicle_plate"].unique():
      if Path((self.p_model_file).format(veh_plate)).exists():
        print(f"Model for vehicle plate {veh_plate} already exists.")
        continue
      
      else:
        df_veh_plate = self.main_df[self.main_df["vehicle_plate"] == veh_plate]
        df_veh_plate.dropna(subset=["y", "temp2"], inplace=True)
        duration_plate_days = (df_veh_plate["ds"].iloc[-1] - df_veh_plate["ds"].iloc[0])
        
        # Dictionary of the values of the hyperparametrs to be used in the model.
        param_grid = {"changepoint_prior_scale": [0.001, 0.01, 0.1],
                      "changepoint_range": [0.75, 0.8, 0.85],
                      "daily_seasonality": [True, False],
                      "weekly_seasonality": [True, False],
                      }

        # Generates all possible combinations of hyperparameters.
        all_params = [dict(zip(param_grid.keys(), v)) for v in\
                           itertools.product(*param_grid.values())]
      
        rmses = []  
        # Loop that runs through all the combinations of hyperparameters for each vehicle.
        df_full_metrics = pd.DataFrame()
        for params in all_params:
          model = Prophet(**params)
          
          # Adds regressors to the model.
          model.add_regressor("temp2")
          # model.add_regressor('ignition')
          # model.add_regressor('interval_time')
          # model.add_regressor('door1_status')
          # model.add_regressor('temp2_status')
          
          # Trains the model with the selected hyperparameters by vehcile. 
          model.fit(df_veh_plate)  
          
          # Cross validation. Parameters are scaled to the number of
          # entries in the dataframe.
          df_cv = cross_validation(model, 
                                  initial = duration_plate_days*0.3, 
                                  period=duration_plate_days*0.1, 
                                  horizon=duration_plate_days*0.1, 
                                  parallel="processes")

          df_perf = performance_metrics(df_cv, rolling_window=1).round(
                                                                    decimals=3)              
          df_full_metrics = pd.concat([df_full_metrics, df_perf], 
                                      ignore_index=True)  # nuevo

          # Creates a list that holds the rmse for each combination of hyperparemeters
          # of the model.
          rmses.append(df_perf["rmse"].values[0])

        # Saves the metrics of each parameter in a .csv
        tuning_results = pd.DataFrame(all_params)
        tuning_results = pd.concat([tuning_results, df_full_metrics], axis=1, 
                                  ignore_index=True)
        tuning_results.insert(0, "timestamp", self.timestamp)
        columns = ["timestamp", "changepoint_prior_scale", "changepoint_range",
                  "daily_seasonality", "weekly_seasonality", "horizon","mse", 
                  "rmse", "mae", "mape", "mdape", "smape", "coverage"]
        tuning_results.columns = columns
        tuning_results.to_csv(self.perf_metrics.format(veh_plate), 
                              mode="a",)

        # Displays the results of the RMSE of all the combination of 
        # hyperparameters in the terminal.
        print("="*70)
        print(tuning_results[["changepoint_prior_scale", "changepoint_range",
                  "daily_seasonality", "weekly_seasonality", "rmse"]])

        # Selects the combination of hyperparameters with the lowest RMSE score and
        # returns it to the terminal.
        best_params = all_params[np.argmin(rmses)]
        print("\nBest parameters for {vplate}:\n{params}".format(vplate=veh_plate,
                                                            params=best_params))
        print("="*70)

        # Saves the correlation coefficients of each regressor to a .txt
        reg_coef = regressor_coefficients(model)
        with open (self.p_regrs_coef_path.format(veh_plate), "w") as reg_txt:
          reg_txt.write(str(reg_coef))

        # Saves the best combination of hyperparameters in a .json
        with open((self.p_best_params).format(veh_plate), "w") as param_file:
          param_file.write(json.dumps(best_params))
        
        # Generates a new model using the best combination of hyperparameters.
        model = Prophet(changepoint_prior_scale=best_params["changepoint_prior_scale"], 
                        changepoint_range=best_params["changepoint_range"], 
                        daily_seasonality=best_params["daily_seasonality"], 
                        weekly_seasonality=best_params["weekly_seasonality"],
                        )

        # Trains the model on the corresponding vehicle dataframe, creating predictions
        # and plotting the results.
        model.fit(df_veh_plate)

        # Saves the current model in a .json file. Each vehicle has its own file
        # which will be used in prediction_maker to precit the missing temperature data.
        with open((self.p_model_file).format(veh_plate), "w") as model_file:
          model_file.write(model_to_json(model))

        # Makes future predictions.
        future_periods = model.make_future_dataframe(periods=int(len(df_veh_plate)*0.2), 
                                                    freq="0.3min")
        forecast = model.predict(future_periods)
        forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

        # Combines the results of these predictions to the corresponding
        # vehicle dataframe.
        metric2 = pd.merge(forecast, self.main_df[["y", "ds"]], on="ds")
        metric2 = metric2[metric2["y"].notna()]
        r_sq_score = r2_score(metric2.y, metric2.yhat)
        
        # Plots the results of the model, including the predictions.
        fig = model.plot(forecast, uncertainty=False)
        fig.subplots_adjust(bottom=0.22, top=0.95)
        plt.xticks(rotation=90)
        plt.xlabel("Date")
        plt.ylabel("Temperature")
        plt.title(f"Fit & Prediction. Prophet. {veh_plate}. R2 = " + str("%.2f" % r_sq_score))
        plt.legend(["Real temp", "Predicted"])

        # save the figure in 'saved_figures' folder.
        plt.savefig(self.p_figures_folder.format(veh_plate))