"""
dash_elements.py
This source code is part of temp-monitoring program.
It contains the code to draw all the graphics are represented 
in the dashboard.
"""

import datetime as dt

import pandas as pd
import plotly.graph_objects as go 
import plotly.express as px 

from dash_folder.dash_elements_functions import GapDeleter, NaNFinder


class dash_elements:
    """
    This class receives the values selected by the user in the Dash GUI, which are
    used to create the subsets of data which will be displayed graphically
    in Dash.
    There is a method for every type of graphic it will be shown on the dashboard.

    Args: 
        pd.Dataframe : filtered dataframe with selected data entries.
        list : two-element corresponding to min and max temp limits.
        bool : capability of show the temperature limits.
        str : 'D'/'H' change the bins parameters for the graph object.
    """
    def __init__(self, filtered_df, limit_selection=[5,20], 
                 show_limits=False, bins_interval="D"):
        self.selected_min = limit_selection[0]
        self.selected_max = limit_selection[1]
        self.show_limits = show_limits
        self.bins_interval = bins_interval
        self.filtered_df = filtered_df
        self.temperature_graph = self.get_temperature_graph() 
        self.regnumber_graph = self.get_regnumber_graph()
        self.temp_gauges = self.get_gauge_temp()
        self.pie_graph = self.get_graf_pie()
        self.gap_stats = self.get_gap_stats()
        self.avg_std_graph = self.get_graf_med_std()


    def get_temperature_graph(self):
        """
        Taking the atributes defined in the class, creates the different figures
        that will be displayed in Dash and returns each of them.

        Return: 
            figure : figure that includes all line plots with temperature (predicted/real/new created)
        """
        gap_finder = GapDeleter(self.filtered_df)
        graph_list = gap_finder.get_new_list()
        self.filtered_df["new_predicted"] = graph_list
        fig1 = px.line(self.filtered_df, 
                        x="date", 
                        y=["temp1", "predicted_temp", "new_predicted"],
                        )
        fig2 = px.scatter(self.filtered_df, 
                        x="date",
                        y="temp1",
                        )
        fig2.update_traces(mode="markers", marker_size=4)
        all_figs = go.Figure(data= fig1.data + fig2.data, layout=fig1.layout)
        if self.show_limits is True:
            all_figs.add_hline(y=self.selected_max, 
                                line_width=1, 
                                line_color="orange", 
                                name="max",
                                )
            all_figs.add_hline(y=self.selected_min, 
                                line_width=1, 
                                line_color="orange", 
                                name="min",
                                )
        all_figs.update_layout(autosize=False, 
                                height=300, 
                                width=600, 
                                xaxis_tickformat="%d-%m",
                                legend=dict(orientation="h",
                                            itemwidth=40,
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="left",
                                            x=0.01),
                                xaxis_title="",
                                yaxis_title="Temperature",
                                legend_title="",
                                margin=dict(l=0, r=0, t=0, b=0,),                       
                                font=dict(size=10,
                                        color="black")
                                )             
        all_figs.update_xaxes(ticklabelmode="period", 
                            tickfont_size=10, 
                            tickmode="linear", 
                            tickangle=90, 
                            showticklabels=True, 
                            showgrid=True
                            )
        return all_figs


    def get_regnumber_graph(self):
        """
        Taking the atributes defined in the class, and the format selected,
        creates the graph with the number of entries.

        Returns:
            figure : figure with bars for the bins selected.
        """
        # Counts the number of entries of the filtered dataframe.
        resampled = self.filtered_df.resample(self.bins_interval, 
                                        on="date", )["temp1"].count()
        # Checks if the interval button has been selected to H(hour) or D(day)
        if self.bins_interval == "H":
            tick_lab_mode="period"
            tick_format="%d-%b %H:%M"
            tick_mode="array"

        else:
            tick_lab_mode="instant"
            tick_format="%d-%b" 
            tick_mode="linear"


        fig_bar = px.bar(x=resampled.index, 
                        y=resampled
                        )
        fig_bar.update_traces(textfont_size=10, 
                            textposition="outside", 
                            cliponaxis=False
                            )
        fig_bar.update_layout(autosize=False, 
                            height=200, 
                            width=600, 
                            margin=dict(l=0, r=0, t=0, b=3)
                            )
        fig_bar.update_xaxes(title=None,
                            ticklabelmode=tick_lab_mode,
                            tickformat=tick_format, 
                            tickfont_size=10,  
                            tickmode=tick_mode, 
                            tickangle=-60, 
                            showticklabels=True,
                            tickson="boundaries",
                            showgrid=True
                            )
        fig_bar.update_yaxes(title=None, 
                            tickfont_size=10
                            )
        return fig_bar


    def get_gauge_temp(self):
        """
        Taking the atributes defined in the class, creates the different figures
        that will display minimum, maximum and average temperature for the 
        selected period in Dash.

        Returns:
            list : list with figures.
        """
        # Obtains the maximum, minumum and average from the filtered dataframe.
        min_temp = self.filtered_df["temp1"].min()
        mean_temp = self.filtered_df["temp1"].mean()
        max_temp = self.filtered_df["temp1"].max()

        return [min_temp, mean_temp, max_temp]


    def get_graf_pie(self):
        """
        Taking the atributes defined in the class, creates the different figures
        that will display the proportion of actual temperatures versus synthesised data.

        Returns: 
            figure : figure with the pie and values.
        """
        # Counts the number of entries with real temperature data and entries
        # where the data is predicted.
        regs_temp1 = self.filtered_df['temp1'].count()
        regs_predict = self.filtered_df['predicted_temp'].count()

        # Sum of real and predicted entries.
        regs_total = regs_temp1 + regs_predict

        # Generates the pie chart with the right values and formats it.
        fig_pie = px.pie(values=[regs_temp1/regs_total, (regs_predict/regs_total)], 
                        names = ["Registered", "Gaps"]
                        )
        fig_pie.update_traces(textposition="inside", 
                            textinfo="percent+label", 
                            showlegend=False, 
                            textfont={"color": "white", 
                                    "size": 12}
                            )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=0, b=40),
                            autosize=False,
                            width=200,
                            height=200
                            )
        return fig_pie


    def get_gap_stats(self):
        """
        Taking the atributes defined in the class, creates the different figures
        that will display how much of the time series is represented by real
        data and how much by gaps in the data

        Returns:
            list : list with figures with gap information. 
        """
        # Generates a list with all the entries that have gaps in the temperature data.
        new_list = NaNFinder(self.filtered_df).get_grouped_index()
        block_duration = []
        output_frmt = "%Y-%m-%d %H:%M:%S"

        # Iterates through each entry of the list to extract the duration of each block of 
        # real data
        for i in range(0,len(new_list)):
            dif = dt.datetime.strptime(str(new_list[i][-1]), output_frmt) - dt.datetime.strptime(str(new_list[i][0]), output_frmt)
            dif = dif.total_seconds()
            block_duration.append(dif)
        
        # Sums the total duration of the blcoks.
        total_duration = int(sum(block_duration))

        # Ensures correct time format is displayed
        t_min = int(total_duration/60)
        t_hour, t_min = divmod(t_min,60)
        avg_duration = int(total_duration/len(new_list))
        m_min, m_sec = divmod(avg_duration,60)   
        avg_duration = f"{m_min}m:{m_sec}s"
        total_duration = f"{t_hour}h:{t_min}m"

        return [avg_duration, total_duration]


    def get_graf_med_std(self):
        """
        Taking the atributes defined in the class, creates the different figures
        that will display the average duration and standard deviatio of the gaps
        in the data.

        Returns: 
            figure : figure with gaps information.
        """
        # Calculates the interval between entries and converts to correct format.
        self.filtered_df["diff"] = self.filtered_df["date"].diff()
        self.filtered_df["diff"] = pd.to_timedelta(self.filtered_df["diff"])/pd.Timedelta("60s")

        # Calculates the average duration and standard deviation.
        avg_duration = round((self.filtered_df["diff"].mean()),1)
        std_dev = round((self.filtered_df["diff"].std()),1)

        # Created the graph to display the average duration and standard deviation.
        fig_mean_std = go.Figure(data=[go.Bar(x=["Average interval (min)", 
                                                "Standar deviation (min)"], 
                                            y=[avg_duration, std_dev], 
                                            text=[avg_duration, std_dev])
                                        ], 
                                layout = {"xaxis": {"visible": True,
                                                    "showticklabels": True
                                                    },
                                        "yaxis": {"title": "y-label",
                                                "visible": False,
                                                "showticklabels": False
                                                },
                                        },
                                )
        fig_mean_std.update_traces(textangle=0, 
                                    textposition="inside", 
                                    cliponaxis=False, 
                                    textfont={"color": "white", 
                                            "size": 75}
                                    )
        fig_mean_std.update_xaxes(showgrid=False, 
                                tickfont_size=14
                                )
        fig_mean_std.update_yaxes(showgrid=False)
        fig_mean_std.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    autosize=False,
                                    width=620,
                                    height=150,
                                    xaxis=dict(color="white"))
        
        return fig_mean_std
