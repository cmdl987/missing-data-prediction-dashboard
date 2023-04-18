"""
dash_elements_functions.py
This source code is part of temp-monitoring program.
It contains different methods used to improve the results of the 
graphics represented in the dashboard.
"""

import pandas as pd
import more_itertools as mit
    

class GapDeleter:
    """
    Where the temperature registered is plotted, lines corresponding to real temperature
    and those which has been predicted don't connect each other, existing a gap between 
    these points.
    
    This class allows to connect these points.

    Args:
        pd.Dataframe : dataset with all registered data.
    """
    def __init__(self, df):
        self.gap_list = self.set_list(df)
        
    
    def set_list(self, df):
        """
        Taking the dataframe called by the class, extracts each entry that has 
        a prediction of missing data which will be displayed graphically.
        The method iterates for every row and detect if the previous and the 
        following row in 'predicted_temp' exists, copying the value to connect 
        the graph-line.
        
        Returns:
            list : list with modified values need to draw the graph.
        """
        new_list = []
        new_list.append(df["predicted_temp"].iloc[0])
        for i in range(0, len(df)):
            if 0 < i < (len(df)-1):
                if pd.isna(df["predicted_temp"].iloc[i]):
                    if pd.isna(df["predicted_temp"].iloc[i-1]) is False:
                        new_list.append(df["temp1"].iloc[i])
                    else:
                        if pd.isna(df["predicted_temp"].iloc[i+1]) is False:
                            new_list.append(df["temp1"].iloc[i])
                        else:
                            new_list.append(df["predicted_temp"].iloc[i])
                else:
                    new_list.append(df["predicted_temp"].iloc[i])
                    
        new_list.append(df["predicted_temp"].iloc[-1])        
        
        return new_list


    def get_new_list(self):
        """
        Returns the list with data modified in set_list method.
        """
        return self.gap_list


class NaNFinder:
    """
    This class find for missing data inside the dataset.

    Args:
        pd.Dataframe : dataframe with all entries needed.
    """

    def __init__(self, fichero):
        self.grouped_list = self.set_grouped_list(fichero)
        
        
    @staticmethod
    def set_grouped_list(df):
        """
        Taking the dataframe called by the class, extracts blocks of contiguous
        dates where temp register is empty and 'data_flag' value is True, 
        and creates a list for each block. 

        Args: 
            pd.Dataframe : dataframe with all the entries.

        Returns:
            list : list with arrays.
        """
        df_sort = df.reset_index().sort_values(by="date")

        # Filters gaps in temp1 and synthesised dates from upsampler.
        mask1 = df_sort["temp1"].isna()        
        mask2 = df_sort["date_flag"] == True   
        df_new = df_sort[mask1 & mask2]   
        
        # Obtains a list with indexes 
        array_index = df_new.index.tolist()  

        # Groups continguous indices in lists.
        grouped_indexes = [list(group) for group in mit.consecutive_groups(array_index)]
        
        # Substitutes indices with their corresponding date.
        for outer_ndx, out in enumerate(grouped_indexes):
            for inner_ndx, inner in enumerate(out):
                grouped_indexes[outer_ndx][inner_ndx] = df_sort._get_value(inner, 'date')

        return grouped_indexes
    

    def get_grouped_index(self):
        """
        Returns the grouped list with contiguous index.
        """
        return self.grouped_list