"""
app.py
This source code is part of temp-monitoring program.
It contains the dash layout structure to generate the dashboard and
all this elements as a new tab in a browser.
"""


import webbrowser
import sys
from pathlib import Path
from threading import Timer

import dash
from dash import dcc, Output, Input, html
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_loading_spinners as dls

sys.path.append(str(Path.cwd()))
from data.dataloader import MainDataset
from dash_folder.dash_elements import dash_elements


# Calling an instance of the MainDataset class to retrieve main_dataset.
object = MainDataset()
main_dataset = object.main_dataset
main_dataset = main_dataset.sort_values(["vehicle_plate", "date"])

FONT_AWESOME = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
external_stylesheets = [dbc.themes.SUPERHERO, FONT_AWESOME]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport",
                            "content": "width=device-width, initial-scale=1.0"}]
                )

app.layout = dbc.Container([
                        dbc.Row([
                            dbc.Col(html.H1("Temperature monitoring",
                                            id = "Title", 
                                            style={"text-align":"center", 
                                                    "marginBottom": "20px"}),
                                            width=12),
                                ]),

                        dbc.Row([
                                dbc.Col([
                                html.Div([
                                    dbc.Row([
                                        dbc.Col([html.H6(id="texto_select_veh_plate",
                                            children=["Select vehicle plate"])],
                                                width=4),

                                        dbc.Col([html.H6(id="texto_select_dates",
                                                    style={"margin-left": "15px"},
                                                    children=["Select dates"])],
                                                    align="end", 
                                                    width=6),

                                        dbc.Col([html.H6(id="empty_1")],
                                                align="end", 
                                                width=1,
                                                ),
                                            ]),

                                    dbc.Row([
                                            dbc.Col([
                                            dcc.Dropdown(id="veh_plate_dropdown", 
                                                        multi=False, 
                                                        value="0001AAA",   
                                                        options=[{"label":x, "value":x}
                                                        for x in sorted(main_dataset["vehicle_plate"].unique())
                                                                ],
                                                        ),
                                                    ], width=3),

                                            dbc.Col([
                                            dcc.DatePickerRange(id="calendar",               
                                                                month_format="MMM, YY",
                                                                display_format="Do, MMM, YY",
                                                                start_date_placeholder_text="start date",
                                                                end_date_placeholder_text="end date",
                                                                minimum_nights=0,
                                                                day_size=32,
                                                                first_day_of_week = 0,
                                                                style = {"color": "black"},
                                                                ),
                                                    ], width=6),

                                            dbc.Col([
                                                dbc.Button(
                                                        id="csv-button",
                                                        children=[html.I(className = "fa fa-download mr-1"), "Download"],
                                                        n_clicks=0, 
                                                        style={"font-size": "12px", 
                                                                "width": "130px", 
                                                                "margin-bottom": "10px",  
                                                                "height": "37px", 
                                                                "verticalAlign": "top"},
                                                            ),
                                                dcc.Download(id="download-dataframe-csv"),
                                                    ], width=2, className="mr-6"),
                                            ]),

                                    dbc.Row([
                                        html.H5("Temperature Prediction", 
                                                id="titulo grafico", 
                                                style={"color": "white", 
                                                        "fontSize": 16, 
                                                        "text-align": "left"},                           
                                                ),
                                            ]),
                                            
                                    dbc.Row([
                                        dbc.Col([ 
                                            dls.Fade(
                                                dcc.Graph(id="temperature_graphics"),
                                                color="#FFFFFF",
                                                speed_multiplier=1,
                                                width=20,
                                                thickness=5),
                                                ]),
                                            ]),
                                    ], className="divBorder"),

                                html.Div([
                                    dbc.Row([
                                        dbc.Col([html.H5("Select limit temperatures", 
                                                        id="text_select_temp_limits", 
                                                        style={"color": "white", 
                                                                "fontSize": 16, 
                                                                "text-align": "left"},  
                                                        )
                                                ], 
                                                width=6),

                                        dbc.Col([html.H6("Show limit temperatures:", 
                                                        id="text_show_temp_limits",
                                                        style={"color": "white", 
                                                                "fontSize": 12, 
                                                                "text-align": "right"}                                 
                                                        )
                                                ], 
                                                width=4),

                                        dbc.Col([dcc.RadioItems([{"label": "Yes", 
                                                                "value": True},
                                                                {"label": "No", 
                                                                "value": False},
                                                                ],
                                                                False,
                                                                id="radio_show_t_crit",
                                                                labelStyle={"display": "inline-block",
                                                                        "margin-right": "7px",
                                                                        "font-weight": 300,
                                                                        "font-size" : "11px"
                                                                        },
                                                                style={"display": "inline-block",
                                                                        "margin-left": "0px",
                                                                        "marginBottom": "10px"},
                                                                inputStyle={"margin-right": "5px"}),
                                                ],
                                                style={"display": "inline-block",
                                                        "verticalAlign": "middle"}, 
                                                width=2),
                                        ], 
                                        align="center"),
                                    
                                    dbc.Row([
                                            dcc.RangeSlider(-10, 40, value=[0,30],
                                            allowCross=False, 
                                            id="temp_range_slider",
                                            tooltip={"placement": "bottom", 
                                                    "always_visible": True}
                                                            ),
                                            html.Div(id="output-container-range-slider")
                                            ]),
                                        ], 
                                        className="divBorder"),

                                html.Div([
                                    dbc.Row([
                                        dbc.Col([html.H6("Total entries", 
                                                        id="texto_total_entries",
                                                        style={"color": "white", 
                                                                "fontSize": 16, 
                                                                "text-align": "left"},
                                                        ),
                                                ],
                                                width=6),
                                        
                                        dbc.Col([html.H6("Show number of entries by:", 
                                                        id="text_show_reg_entries",
                                                        style={"color": "white", 
                                                        "fontSize": 12, 
                                                        "text-align": "right"},
                                                        )
                                                ], 
                                                width=4),

                                        dbc.Col([dcc.RadioItems([{"label":"Hour", "value":"H"},
                                                                {"label":"Day", "value":"D"}],"D", 
                                                id="hour-day_radio_item",  
                                                inline=False, 
                                                labelStyle={"display": "block",
                                                        "margin-right": "7px",
                                                        "font-weight": 300,
                                                        "font-size": "11px",
                                                        }, 
                                                style={"display": "inline-block",
                                                        "margin-left": "0px",
                                                        "marginBottom": "10px"
                                                        },
                                                inputStyle={"margin-right": "5px"
                                                        }),
                                                ],
                                                style={"display": "inline-block", 
                                                        "verticalAlign": "middle"}, 
                                                width=2),
                                        ], 
                                        align="center"),

                                    dbc.Row([  
                                        dbc.Col([
                                            dls.Fade(
                                                dcc.Graph(id="regnumber_graphics"),
                                                color="#FFFFFF",
                                                speed_multiplier=1,
                                                width=20,
                                                thickness=5)
                                                ]),
                                            ]),
                                        ],
                                    className="divBorder"),
                                    ], 
                                    width=6),

                            dbc.Col([    
                                dbc.Row([html.H2(id="title_temperature", 
                                                children=["Temperatures"],
                                                style={"marginBottom": "1em"})
                                        ], class_name="text-center"),

                                dbc.Row([
                                    dbc.Col([                                       
                                        daq.Gauge(id="gauge_min",
                                            showCurrentValue=True,
                                            units="ºC",
                                            value=-2,
                                            label="Temp. Min.",
                                            scale={"start": -20, 
                                                    "interval": 10, 
                                                    "labelInterval": 1},
                                            max=40,
                                            min=-20,
                                            color={"gradient": True,
                                                   "ranges": {"blue": [-20,0],
                                                            "yellow": [0,20],
                                                            "red": [20,40]}
                                                  },
                                            size=140
                                                )
                                        ], 
                                        width=4),

                                    dbc.Col([
                                        daq.Gauge(id="gauge_media",
                                                showCurrentValue=True,
                                                units="ºC",
                                                value=15,
                                                label="Temp. Media",
                                                scale={"start": -20, 
                                                    "interval": 10, 
                                                    "labelInterval": 1},
                                                max=40,
                                                min=-20,
                                                color={"gradient": True,
                                                        "ranges": {"blue": [-20,0],
                                                                "yellow": [0,20],
                                                                "red": [20,40]
                                                                },
                                                        },
                                                size=140
                                                ),
                                        ], 
                                        width=4),

                                    dbc.Col([
                                        daq.Gauge(id="gauge_max",
                                                showCurrentValue=True,
                                                units="ºC",
                                                value=35,
                                                label="Temp. Max.",
                                                scale={"start": -20, 
                                                        "interval": 10, 
                                                        "labelInterval": 1},
                                                max=40,
                                                min=-20,
                                                color={"gradient": True,
                                                        "ranges": {
                                                                "blue": [-20,0],
                                                                "yellow": [0,20],
                                                                "red": [20,40],
                                                                },
                                                        },
                                                size=140
                                                ),
                                        ], 
                                        width=4),
                                    ]),

                                dbc.Row([
                                    html.H2("Gaps", 
                                            id="Title_Gap",
                                            style={"color": "white",
                                                    "height": "10%"
                                                    },
                                            className="text-center"),
                                        ]),

                                dbc.Row([
                                    dbc.Col([
                                        dls.Fade(
                                                dcc.Graph(id="missing_data_pct_graph"),
                                                color="#FFFFFF",
                                                speed_multiplier=1,
                                                width=20,
                                                thickness=5,
                                                ),
                                        ], 
                                        width=4, 
                                        style={"display": "inline-block"}),  
                                                
                                    dbc.Col([
                                        dbc.Row([
                                            html.Div(id="mean_interval", 
                                                    style={"color": "white", 
                                                            "fontSize": 45,
                                                            "marginTop": "1em",
                                                            },   
                                                    className="text-center"),
                                                ]),
                                        dbc.Row([   
                                            html.Div("Gap average duration in minutes", 
                                                    id="texto_int_medio",
                                                    style={"color": "white", 
                                                            "fontSize": 14,
                                                            },
                                                    className="text-center"),
                                                ]),
                                        ], 
                                        width=4),

                                    dbc.Col([
                                        dbc.Row([
                                            html.Div(id="gap_total_time", 
                                                    style={"color": "white", 
                                                            "fontSize": 45,
                                                            "marginTop": "1em",
                                                            }, 
                                                    className="text-center"
                                                    ),
                                            html.Div("Gap duration in hours", 
                                                    id="text_gap_total_time", 
                                                    style={"color": "white", 
                                                            "fontSize": 14,
                                                            },
                                                    className="text-center"),
                                            ]), 
                                        ], 
                                        width=4),
                                    ]),

                                dbc.Row([
                                    html.H2("Time interval", 
                                            id="title_intervals", 
                                            style={"color": "white", 
                                                "height": "20%", 
                                                "marginTop": "1em", 
                                                "marginBotom": "1em"
                                                },
                                            className="text-center")
                                        ]),

                                dbc.Row([
                                    dbc.Col([
                                        dls.Fade(
                                                dcc.Graph(id="avg_stdev_graph",
                                                        style={"padding": 20,
                                                                "marginTop": "1em"
                                                                }),
                                                color="#FFFFFF",
                                                speed_multiplier=1,
                                                width=20,
                                                thickness=5)
                                            ]),
                                        ]),
                                ], 
                                width=6),
                            ]),
                        ])

@app.callback(           
        Output("calendar", "min_date_allowed"),
        Output("calendar", "max_date_allowed"),
        Output("calendar", "start_date"),
        Output("calendar", "end_date"),
        Input("veh_plate_dropdown", "value"))
def min_max_date_by_plate(vehicle_plate):
    """
    The vehicle chosen in the drop_down menu is stored in the callback and 
    the maximum and minimum dates are detected and used as start and end points
    for the calendar.
    """
    df_plate_sel = main_dataset[main_dataset["vehicle_plate"] == vehicle_plate]
    start_date = df_plate_sel["date"].min().date()
    end_date = df_plate_sel["date"].max().date()

    return [start_date, end_date, start_date, end_date]  


@app.callback(
    [Output("temperature_graphics", "figure")],  
        [Input("veh_plate_dropdown", "value"),
        Input("temp_range_slider", "value"),
        Input("calendar", "start_date"),
        Input("calendar", "end_date"),
        Input("radio_show_t_crit", "value")])
def get_temperature_graph(vehicle_plate, limit_selection, start_date, end_date, show_limits):
    """
    The vehicle, temperature limits, whether the limits are shown, start and end 
    dates are chosen on the dashboard and stored in the callback. 
    The graph is updated with these data. 
    """
    end_date = end_date + " 23:59:59"
    mask = (
        (main_dataset["vehicle_plate"] == vehicle_plate)
         & (main_dataset["date"] > start_date)
         & (main_dataset["date"] <= end_date)
        )
    # Applies the date and vehicle filter
    global filtered_data
    filtered_data = main_dataset.loc[mask, :]

    # Creates instance from dash_elements class
    elements = dash_elements(**{"filtered_df": filtered_data, 
                                "limit_selection": limit_selection,
                                "show_limits": show_limits,
                                })

    # Generates variables from class objects
    temp_graph = elements.temperature_graph
    return [temp_graph]


@app.callback(
    [Output("regnumber_graphics", "figure")],
        [Input("veh_plate_dropdown", "value"),
        Input("calendar", "start_date"),
        Input("calendar", "end_date"),
        Input("hour-day_radio_item", "value")],
                )
def get_regnumber_graph(vehicle_plate, start_date, end_date, graf_bins):
    """
    The vehicle, start and end dates, whether data are shown by day or by hour
    are chosen on the dashboard and stored in the callback. The graph is updated 
    with these data.
    """
    end_date = end_date + " 23:59:59"
    mask = (
        (main_dataset["vehicle_plate"] == vehicle_plate)
         & (main_dataset["date"] > start_date)
         & (main_dataset["date"] <= end_date)
        )
    # Applies the date and vehicle filter
    filtered_data = main_dataset.loc[mask, :]

    # Creates instance from dash_elements class
    elements = dash_elements(**{"filtered_df":filtered_data,
                                "bins_interval": graf_bins})

    # Generates variables from class objects
    regnumber_graph = elements.regnumber_graph

    return [regnumber_graph]


@app.callback(
    [Output("gauge_min", "value"),
    Output("gauge_media", "value"),
    Output("gauge_max", "value"),
    Output("missing_data_pct_graph", "figure"),
    Output("mean_interval", "children"),      
    Output("gap_total_time", "children"),  
    Output("avg_stdev_graph", "figure"),],
        [Input("veh_plate_dropdown", "value"),
        Input("calendar", "start_date"),
        Input("calendar", "end_date")]
                )
def dibujar_grafica(vehicle_plate, start_date, end_date):
    """
    The vehicle, start and end dates are chosen on the dashboard and stored 
    in the callback. This information is used to display graphs with 
    information on missing data. 
    It modifies a global variable.

    Returns: 
        list : list with graphics.
    """
    end_date = end_date + " 23:59:59"
    mask = (
        (main_dataset["vehicle_plate"] == vehicle_plate)
         & (main_dataset["date"] > start_date)
         & (main_dataset["date"] <= end_date)
        )
    # Applies the date and vehicle filter
    global filtered_data
    filtered_data = main_dataset.loc[mask, :]
    
    # Creates instance from dash_elements class
    elements = dash_elements(filtered_data)
    
    # Generates variables from class objects
    g_min, g_mean, g_max = elements.temp_gauges
    pie_graphic = elements.pie_graph
    mean_gap, total_gap = elements.gap_stats
    avg_stdev_graph = elements.avg_std_graph

    return [g_min, g_mean, g_max, pie_graphic, mean_gap, 
            total_gap, avg_stdev_graph]


@app.callback(
        Output("download-dataframe-csv", "data"),
        Input("csv-button", "n_clicks"),
        prevent_initial_call=True) 
def download_file(n_clicks):
    """
    If the download button is pressed the data pertaining to the selected
    vehicle and dates is selected for download.
    """
    return dcc.send_data_frame(filtered_data.to_csv, "dataframe.csv", index=False)


def open_browser():
    """
    Opens a web browser with the defined URL and port to display the dashboard.
    """
    webbrowser.open_new("http://127.0.0.1:8050/page1/")


def main():
	"""
    Function that executes the dash application from scratch.
	"""
	Timer(2, open_browser).start()
	app.run_server(debug=True, use_reloader=False)