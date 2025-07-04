from dash import Dash, dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc
import base64
import json
import dash_leaflet as dl
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import ipywidgets as widgets
from IPython.display import display
import time
import pickle
import os
import geopandas as gpd
import ws3.forest, ws3.core
import csv
from functools import partial, wraps
import distance
import operator
import shutil
from IPython.display import display
import libcbm
import zipfile
import os
import pickle
import os
from shapely.geometry import Polygon
import geopandas as gpd

from util import compile_events, cbm_report, compile_scenario_maxstock, plot_scenario_maxstock, run_cbm_emissionstock, run_scenario, plugin_c_curves, plugin_c_curves, cbm_report_both, compare_ws3_cbm, compare_ws3_cbm_both, track_system_stock, track_system_emission, compile_scenario_minemission, plot_scenario_minemission, kpi_age, kpi_species, cmp_c_ss, cmp_c_se, results_scenarios, bootstrap_ogi, compare_kpi_age, epsilon_computer, tradeoff_biodiversity_cs, tradeoff_hv_cs, tradeoff_hv_biodiversity, inventory_processing, curve_points_generator, fm_bootstrapper, carbon_curve_points

###########################################################################
########functions to create various graph objects###########################

from plotly.subplots import make_subplots
import plotly.graph_objs as go

def buildScenarioBarGraph(harvested_area_x,harvested_area_y,
                  harvested_vol_x, harvested_vol_y,
                  grow_stock_x, grow_stock_y):
    scenarioBarGraph = make_subplots(rows=1, cols=3,horizontal_spacing=0.1)

    scenarioBarGraph.add_trace(go.Bar(x=harvested_area_x, y=harvested_area_y, name = "Harvested area (ha)"),
                  row=1, col=1)
    scenarioBarGraph.update_xaxes(title_text="Harvested area (ha)", row=1, col=1)

    scenarioBarGraph.add_trace(go.Bar(x=harvested_vol_x, y=harvested_vol_y, name = "Harvested volume (m3)"),
                  row=1, col=2)
    scenarioBarGraph.update_xaxes(title_text="Harvested volume (m3)", row=1, col=2)

    scenarioBarGraph.add_trace(go.Bar(x=grow_stock_x, y=grow_stock_y, name = "Growing Stock (m3)"),
                  row=1, col=3)
    scenarioBarGraph.update_xaxes(title_text="Growing Stock (m3)", row=1, col=3)

    # scenarioBarGraph.update_layout(height=400, width=1800, title_text="Scenarios")
    return scenarioBarGraph


def buildStackedBarGraph(period_x, forest_area_stack1, forest_area_stack2):
    stackedBarChart = go.Figure(data=[
        go.Bar(name='Primary forest', x=period_x, y=forest_area_stack1),
        go.Bar(name='Secondary forest', x=period_x, y=forest_area_stack2)
    ])
    stackedBarChart.update_layout(barmode='stack')
    stackedBarChart.update_xaxes(title_text="Period")
    stackedBarChart.update_yaxes(title_text="Forest area (ha)")
    return stackedBarChart

def drawTradeOffCurve(_X, _Y, xLabel,yLabel):
    tradeOffFig = go.Figure()
    tradeOffFig.add_trace(go.Scatter(x=_X, y=_Y, mode='lines+markers', name='Pareto Front'))
    tradeOffFig.update_xaxes(title_text=xLabel)
    tradeOffFig.update_yaxes(title_text=yLabel)
    tradeOffFig['data'][0]['showlegend'] = True
    tradeOffFig.update_layout(height=400, width=1800, title_text="Tradeoff Curve")
    return tradeOffFig

def multipanelLineGraph(dataFrame1, xLabel, yLabel, title):
    carbonStockEmissionFig = go.Figure()
    carbonStockEmissionFig.update_xaxes(title_text=xLabel)
    carbonStockEmissionFig.update_yaxes(title_text=yLabel)
    carbonStockEmissionFig.update_layout(title_text=title)


    for i in range(1, len(dataFrame1.columns)):
        col_name = dataFrame1.columns[i]
        carbonStockEmissionFig.add_trace(go.Scatter(x=dataFrame1.index, y=dataFrame1[col_name], mode='lines', name=col_name))
    return carbonStockEmissionFig

def netEmissionGraph(dataFrame1, xLabel, yLabel, title):
    netEmissionFig = go.Figure()
    netEmissionFig.update_xaxes(title_text=xLabel)
    netEmissionFig.update_yaxes(title_text=yLabel)
    netEmissionFig.update_layout(title_text=title)

    netEmissionFig.add_trace(go.Scatter(x=dataFrame1['Year'], y=dataFrame1['Net emission'], mode='lines', name='Net emission'))
    print("++++++++++++++++++")
    baseLineDf = pd.DataFrame({'dummy': [0] * dataFrame1.shape[0]})
    netEmissionFig.add_trace(go.Scatter(x=dataFrame1['Year'], y=baseLineDf['dummy'], mode='lines', showlegend = False, line = dict(color='red', width=2, dash='dash')))
    return netEmissionFig

def clear_output_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # remove directory
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f"Folder {folder_path} does not exist.")


############################################################################
######Parameters that will be passed to the backend ########################
print("start")
# base_year_val = 0
horizon = 0
json_object_val = None
###########
# Initialize the input parameters
base_yearr = 2020
period_lengthh = 10
max_agee = 1000
n_steps = 100
tvy_name = 'totvol'
max_harvest = 1.0
case_study = 'ecotrust'
scenario_names = ['lowest carbon stock', 'business as usual', '40% of highest carbon stock', '60% of highest carbon stock', '20% of highest carbon stock', 'highest carbon stock']
# scenario_names = ['lowest carbon stock']
obj_mode = 'max_hv'
hwp_pool_effect_value = 0
release_immediately_value = 0
displacement_effect = 0
clt_percentage = 0
credibility = 0
budget_input = 10000000
bd1_values = []
cs1_values = []
hv2_values = []
cs2_values = []
hv3_values = []
bd3_values = []
T_df_plot_12 = []
T_cbm_output_1 = []
T_cbm_output_2 = []
T_df_plot_34 = []
T_cbm_output_3 = []
T_cbm_output_4 = []
T_forest_type_base = []
T_forest_type_alt = []
T_emission_difference = []
resultsReady = False
###################
yld = pd.read_csv('./data/ecotrust-dss-bc-data/yld.csv')
yld['AU'] = yld['AU'].astype(int)

downloadPath = './outputs/csv/ecotrust/'
canf = pd.read_csv('./data/ecotrust-dss-bc-data/canfi_species.csv')
canf = canf[['name','canfi_species']].set_index('name')
clear_output_folder('./outputs')
##################
shapefile_path = './data/ecotrust-dss-bc-data/merged_stands.gpkg'
# shapefile_path = './data/shp_files/tsa45.shp/stands.shp'
stands_org = gpd.read_file(shapefile_path, layer="merged_stands")
# stands_org = gpd.read_file(shapefile_path, engine = 'fiona', use_arrow = True)
stands_org = stands_org.to_crs(epsg=4326)
abridgedStands = stands_org  #.head(10) #only first 10 stands for testing purpose
currentSelectedAreaCood = []
print('loading done')
############################################################################
############################################################################


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = Dash(__name__, external_stylesheets=external_stylesheets, serve_locally=True, requests_pathname_prefix="/container11-port8002/")

import uuid
import os

@app.callback(
    Output('session-id', 'data'),
    Input('horizon_id', 'value'),  # or any trigger on app start
    prevent_initial_call=True
)
def assign_session(_):
    session_id = str(uuid.uuid4())
    os.makedirs(f'./sessions/{session_id}', exist_ok=True)
    return session_id

server = app.server

app.layout =html.Div( [ html.Div([
    html.Div(children=[

        dbc.Row(
            [
                dbc.Col(html.Label( 'Define the planning horizon', id="instruction_label_id", style={'width': '100%'}),width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Horizon")),
                dbc.Col(dcc.Input(
                    id="horizon_id", type="number", placeholder="Horizon",
                    min=0, max=20, step=1, value=10, style={"min-width": "100%"}
                )
                ),
            ]
        ),

        dbc.Row(
            [
                dbc.Col( dcc.Upload(html.Button('Upload Area of Interest', id = "upload_area_button_id", style = {'width' : '100%'}), id='upload-data'), width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        ),
        dcc.Store(id='session-id', storage_type='session'), ###########
        dcc.Store(id='results-ready', storage_type='session'), ######
        dcc.Store(id='aoi-coordinates', storage_type='session'), #####
        dcc.Store(id='analysis_status_store', data='idle'), ######
        html.Div(id='analysis_status_msg', style={'textAlign': 'center', 'marginTop': '10px'}), #########

        dbc.Row(
            [
                dbc.Col(html.Button('Analyse',id = "analyse_button_id", style = {'width' : '100%'}),width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Button('Download results',id = "download_button_id", style = {'width' : '100%'}),width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Label( 'Waiting', id="wait_label_id", style={'width': '100%'}),width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        ),
        # dbc.Alert(
        #     id="alert_analysis",
        #     children="",
        #     color="info",
        #     is_open=False,
        #     dismissable=False,
        # ),
        # dcc.Store(id="analysis_status", data="idle"),  # to store status like "waiting" or "done"

        dbc.Row(
            [
                dbc.Col(dcc.Download(id="dcc_download"),width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        )
    ], style={'margin': 10, 'min-width': '400px', 'padding': 10, 'flex': 1, 'border':'2px gray solid'}),
    html.Div(children=[
        dl.Map(center=[49, -120], zoom=6, children=[
            dl.TileLayer(),
            dl.GeoJSON(id = 'geojsonComp', options={"style": {"color": "red"}}),
            dl.FeatureGroup([dl.EditControl(id="edit_control", draw={'circle': 'false'})
                 ]),
        ], style={'margin': 10,'min-width': '400px', 'width': '70vw', 'height': '50vh', "display": "inline-block", 'border':'2px gray solid'}, id="map"),
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flexDirection': 'row','border':'2px gray solid'}),

html.Div(children=[
    html.Label('Results and Plots'),
    dcc.Tabs(id="tabs-graphs", value='scn-1-graph', children=[
        dcc.Tab(label='Scenario One', value='scn-1-graph'),
        dcc.Tab(label='Scenario Two', value='scn-2-graph'),
        dcc.Tab(label='Scenario Three', value='scn-3-graph'),
        dcc.Tab(label='Scenario Four', value='scn-4-graph'),
        dcc.Tab(label='Scenario Five', value='scn-5-graph'),
        dcc.Tab(label='Scenario Six', value='scn-6-graph'),
########################################################################
        dcc.Tab(label='Tradeoff One', value='tdoff-1-graph'),
        dcc.Tab(label='Tradeoff Two', value='tdoff-2-graph'),
        dcc.Tab(label='Tradeoff Three', value='tdoff-3-graph'),

    ]),
    html.Div(id='tabs-content-example-graph')
], style={'padding': 10, 'flex': 1, 'border':'2px gray solid', 'height': '40vh'})

])





############################################################################
############################################################################


@callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-graphs', 'value'),
         State('session-id', 'data')  # <- get session_id from dcc.Store
         )
def render_content(tab, session_id):
    # if resultsReady == False:
    #     return html.Div([html.H3('Results are not ready yet')])

    # if not resultsReady:
    #     return html.Div([html.H3('Results are not ready yet')])

    session_path = os.path.join("sessions", session_id)
    session_file = os.path.join(session_path, "results.pkl")

    if not os.path.exists(session_file):
        return html.Div("No results found for your session.")

    with open(session_file, "rb") as f:
        data = pickle.load(f)

    T_df_plot_12 = data['T_df_plot_12']
    T_cbm_output_1 = data['T_cbm_output_1']
    T_cbm_output_2 = data['T_cbm_output_2']
    T_df_plot_34 = data['T_df_plot_34']
    T_cbm_output_3 = data['T_cbm_output_3']
    T_cbm_output_4 = data['T_cbm_output_4']
    T_forest_type_base = data['T_forest_type_base']
    T_forest_type_alt = data['T_forest_type_alt']
    T_emission_difference = data['T_emission_difference']
    bd1_values = data['bd1_values']
    cs1_values = data['cs1_values']
    hv2_values = data['hv2_values']
    cs2_values = data['cs2_values']
    hv3_values = data['hv3_values']
    bd3_values = data['bd3_values']        

    print("showing results now")

    if tab == 'scn-1-graph':
        return html.Div([
            html.H3('Alternative scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_12[0]['period'].tolist(), T_df_plot_12[0]['oha'].tolist(), T_df_plot_12[0]['period'].tolist(), T_df_plot_12[0]['ohv'].tolist(),T_df_plot_12[0]['period'].tolist(), T_df_plot_12[0]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_alt[0]['period'].tolist(), T_forest_type_alt[0]['primary forest'].tolist(), T_forest_type_alt[0]['secondary forest'].tolist())),
            html.H3('Business as usual scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_34[0]['period'].tolist(), T_df_plot_34[0]['oha'].tolist(), T_df_plot_34[0]['period'].tolist(), T_df_plot_34[0]['ohv'].tolist(),T_df_plot_34[0]['period'].tolist(), T_df_plot_34[0]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_base[0]['period'].tolist(), T_forest_type_base[0]['primary forest'].tolist(), T_forest_type_base[0]['secondary forest'].tolist())),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_1[0], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (alternative scenario)')), width = 2),
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_3[0], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (base scenario)')), width = 2)
            ]),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_2[0], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (alternative scenario)')), width = 2),
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_4[0], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (base scenario)')), width = 2)
            ]),
            html.H3('Net emission difference', style={'fontSize': '32px'}),
            dcc.Graph( figure= netEmissionGraph(T_emission_difference[0], 'Year', 'Net carbon emission difference (Ton)', 'Net emission difference between base and alternative scenarios')),
        ])
    elif tab == 'scn-2-graph':
        return html.Div([
            html.H3('Alternative scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_12[1]['period'].tolist(), T_df_plot_12[1]['oha'].tolist(), T_df_plot_12[1]['period'].tolist(), T_df_plot_12[1]['ohv'].tolist(),T_df_plot_12[1]['period'].tolist(), T_df_plot_12[1]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_alt[1]['period'].tolist(), T_forest_type_alt[1]['primary forest'].tolist(), T_forest_type_alt[1]['secondary forest'].tolist())),
            html.H3('Business as usual scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_34[1]['period'].tolist(), T_df_plot_34[1]['oha'].tolist(), T_df_plot_34[1]['period'].tolist(), T_df_plot_34[1]['ohv'].tolist(),T_df_plot_34[1]['period'].tolist(), T_df_plot_34[1]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_base[1]['period'].tolist(), T_forest_type_base[1]['primary forest'].tolist(), T_forest_type_base[1]['secondary forest'].tolist())),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_1[1], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_3[1], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (base scenario)')))
            ]),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_2[1], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_4[1], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (base scenario)')))
            ]),
            html.H3('Net emission difference', style={'fontSize': '32px'}),
            dcc.Graph( figure= netEmissionGraph(T_emission_difference[1], 'Year', 'Net carbon emission difference (Ton)', 'Net emission difference between base and alternative scenarios')),
        ])
    elif tab == 'scn-3-graph':
        return html.Div([
            html.H3('Alternative scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_12[2]['period'].tolist(), T_df_plot_12[2]['oha'].tolist(), T_df_plot_12[2]['period'].tolist(), T_df_plot_12[2]['ohv'].tolist(),T_df_plot_12[2]['period'].tolist(), T_df_plot_12[2]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_alt[2]['period'].tolist(), T_forest_type_alt[2]['primary forest'].tolist(), T_forest_type_alt[2]['secondary forest'].tolist())),
            html.H3('Business as usual scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_34[2]['period'].tolist(), T_df_plot_34[2]['oha'].tolist(), T_df_plot_34[2]['period'].tolist(), T_df_plot_34[2]['ohv'].tolist(),T_df_plot_34[2]['period'].tolist(), T_df_plot_34[2]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_base[2]['period'].tolist(), T_forest_type_base[2]['primary forest'].tolist(), T_forest_type_base[2]['secondary forest'].tolist())),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_1[2], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_3[2], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (base scenario)')))
            ]),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_2[2], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_4[2], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (base scenario)')))
            ]),
            html.H3('Net emission difference', style={'fontSize': '32px'}),
            dcc.Graph( figure= netEmissionGraph(T_emission_difference[2], 'Year', 'Net carbon emission difference (Ton)', 'Net emission difference between base and alternative scenarios')),
        ])
    elif tab == 'scn-4-graph':
        return html.Div([
            html.H3('Alternative scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_12[3]['period'].tolist(), T_df_plot_12[3]['oha'].tolist(), T_df_plot_12[3]['period'].tolist(), T_df_plot_12[3]['ohv'].tolist(),T_df_plot_12[3]['period'].tolist(), T_df_plot_12[3]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_alt[3]['period'].tolist(), T_forest_type_alt[3]['primary forest'].tolist(), T_forest_type_alt[3]['secondary forest'].tolist())),
            html.H3('Business as usual scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_34[3]['period'].tolist(), T_df_plot_34[3]['oha'].tolist(), T_df_plot_34[3]['period'].tolist(), T_df_plot_34[3]['ohv'].tolist(),T_df_plot_34[3]['period'].tolist(), T_df_plot_34[3]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_base[3]['period'].tolist(), T_forest_type_base[3]['primary forest'].tolist(), T_forest_type_base[3]['secondary forest'].tolist())),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_1[3], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_3[3], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (base scenario)')))
            ]),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_2[3], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_4[3], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (base scenario)')))
            ]),
            html.H3('Net emission difference', style={'fontSize': '32px'}),
            dcc.Graph( figure= netEmissionGraph(T_emission_difference[3], 'Year', 'Net carbon emission difference (Ton)', 'Net emission difference between base and alternative scenarios')),
        ])
    elif tab == 'scn-5-graph':
        return html.Div([
            html.H3('Alternative scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_12[4]['period'].tolist(), T_df_plot_12[4]['oha'].tolist(), T_df_plot_12[4]['period'].tolist(), T_df_plot_12[4]['ohv'].tolist(),T_df_plot_12[4]['period'].tolist(), T_df_plot_12[4]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_alt[4]['period'].tolist(), T_forest_type_alt[4]['primary forest'].tolist(), T_forest_type_alt[4]['secondary forest'].tolist())),
            html.H3('Business as usual scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_34[4]['period'].tolist(), T_df_plot_34[4]['oha'].tolist(), T_df_plot_34[4]['period'].tolist(), T_df_plot_34[4]['ohv'].tolist(),T_df_plot_34[4]['period'].tolist(), T_df_plot_34[4]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_base[4]['period'].tolist(), T_forest_type_base[4]['primary forest'].tolist(), T_forest_type_base[4]['secondary forest'].tolist())),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_1[4], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_3[4], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (base scenario)')))
            ]),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_2[4], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_4[4], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (base scenario)')))
            ]),
            html.H3('Net emission difference', style={'fontSize': '32px'}),
            dcc.Graph( figure= netEmissionGraph(T_emission_difference[4], 'Year', 'Net carbon emission difference (Ton)', 'Net emission difference between base and alternative scenarios')),
        ])
    elif tab == 'scn-6-graph':
        return html.Div([
            html.H3('Alternative scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_12[5]['period'].tolist(), T_df_plot_12[5]['oha'].tolist(), T_df_plot_12[5]['period'].tolist(), T_df_plot_12[5]['ohv'].tolist(),T_df_plot_12[5]['period'].tolist(), T_df_plot_12[5]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_alt[5]['period'].tolist(), T_forest_type_alt[5]['primary forest'].tolist(), T_forest_type_alt[5]['secondary forest'].tolist())),
            html.H3('Business as usual scenario', style={'fontSize': '32px'}),
            dcc.Graph( figure= buildScenarioBarGraph(T_df_plot_34[5]['period'].tolist(), T_df_plot_34[5]['oha'].tolist(), T_df_plot_34[5]['period'].tolist(), T_df_plot_34[5]['ohv'].tolist(),T_df_plot_34[5]['period'].tolist(), T_df_plot_34[5]['ogs'].tolist()) ),
            html.H3('Area primary secondary forest', style={'fontSize': '24px'}),
            dcc.Graph(figure=buildStackedBarGraph(T_forest_type_base[5]['period'].tolist(), T_forest_type_base[5]['primary forest'].tolist(), T_forest_type_base[5]['secondary forest'].tolist())),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_1[5], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure = multipanelLineGraph(T_cbm_output_3[5], 'Year', 'Carbon stocks (Ton)', 'Carbon stocks over years (base scenario)')))
            ]),
            dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_2[5], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (alternative scenario)'))),
                dbc.Col(dcc.Graph(figure=multipanelLineGraph(T_cbm_output_4[5], 'Year', 'Carbon emission (Ton)', 'Carbon emission over years (base scenario)')))
            ]),
            html.H3('Net emission difference', style={'fontSize': '32px'}),
            dcc.Graph( figure= netEmissionGraph(T_emission_difference[5], 'Year', 'Net carbon emission difference (Ton)', 'Net emission difference between base and alternative scenarios')),
        ])

    elif tab == 'tdoff-1-graph':
        return html.Div([
            html.H3('Biodiversity & Carbon stock Tradeoff Curve', style={'fontSize': '24px'}),
            dcc.Graph(figure=drawTradeOffCurve(cs1_values, bd1_values, "Carbon Stock","Biodiversity"))
            # dcc.Graph(figure=drawTradeOffCurve(tradeoff_x, tradeoff_y, "Carbon Stock","Biodiversity"))
        ])
    elif tab == 'tdoff-2-graph':
        return html.Div([
            html.H3('Biodiversity & Harvest Volume Tradeoff Curve', style={'fontSize': '24px'}),
            dcc.Graph(figure=drawTradeOffCurve(cs2_values, hv2_values, "Biodiversity", "Harvested Volume"))
            # dcc.Graph(figure=drawTradeOffCurve(tradeoff_x, tradeoff_y, "Biodiversity", "Harvested Volume"))
        ])
    elif tab == 'tdoff-3-graph':
        return html.Div([
            html.H3('Carbon Stock & Harvest Volume Tradeoff Curve', style={'fontSize': '24px'}),
            dcc.Graph(figure=drawTradeOffCurve(bd3_values, hv3_values, "Carbon Stock", "Harvested Volume"))
            # dcc.Graph(figure=drawTradeOffCurve(tradeoff_x, tradeoff_y, "Carbon Stock", "Harvested Volume"))
        ])

@app.callback(Output('dcc_download','data'), [],
              [
                  Input("download_button_id", "n_clicks"),
              ],prevent_initial_call=True)
def mycallback2( n_clicks):#
    with zipfile.ZipFile('report123.zip', 'w') as myzip:
     for f in os.listdir(downloadPath):
         filename = downloadPath +  os.fsdecode(f)
         myzip.write(filename, f)
    return dcc.send_file('report123.zip')


# resCounterIndex = 0




@app.callback(
    Output("analysis_status_store", "data"),
    Output("wait_label_id", "children"),
    Output("results-ready", "data"),
    Input("analyse_button_id", "n_clicks"),
    State("horizon_id", "value"),
    State("session-id", "data"),
    State("aoi-coordinates", "data"),
    prevent_initial_call=True
)
def run_analysis(n_clicks, horizon, session_id, currentSelectedAreaCood):
    if not currentSelectedAreaCood or len(currentSelectedAreaCood) < 3:
        return "error", "No AOI uploaded or AOI too small.", False

    try:


        if len(currentSelectedAreaCood) <= 2:
            raise ValueError("Not enough polygon points in AOI.")

        selPoly = Polygon(currentSelectedAreaCood)
        gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[selPoly])
        sjoin_results = gpd.sjoin(abridgedStands, gdf, how='left', predicate='within')
        afterDropping = sjoin_results.dropna().to_crs(3005)
        clear_output_folder('./outputs')
        stands = inventory_processing(afterDropping, canf)

        curve_points_table = curve_points_generator(stands, yld, canf)
        fm = fm_bootstrapper(base_yearr, horizon, period_lengthh, max_agee, stands, curve_points_table, tvy_name)
        c_curves_p, c_curves_f = carbon_curve_points(fm)
        plugin_c_curves(fm, c_curves_p, c_curves_f)
        bootstrap_ogi(fm)

        epsilon, cs_max = epsilon_computer(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=10, solver=ws3.opt.SOLVER_PULP)

        # Result containers
        T_df_plot_12, T_cbm_output_1, T_cbm_output_2 = [], [], []
        T_df_plot_34, T_cbm_output_3, T_cbm_output_4 = [], [], []
        T_forest_type_base, T_forest_type_alt, T_emission_difference = [], [], []

        for scenario_name in scenario_names:
            df_plot_12, cbm_output_1, cbm_output_2, forest_type_alt, df_plot_34, cbm_output_3, cbm_output_4, forest_type_base, emission_difference = results_scenarios(
                fm, clt_percentage, credibility, budget_input, n_steps, max_harvest, scenario_name,
                displacement_effect, hwp_pool_effect_value, release_immediately_value, case_study,
                obj_mode, epsilon, cs_max, pickle_output_base=False, pickle_output_alter=False
            )
            T_df_plot_12.append(df_plot_12)
            T_cbm_output_1.append(cbm_output_1)
            T_cbm_output_2.append(cbm_output_2)
            T_forest_type_alt.append(forest_type_alt)
            T_df_plot_34.append(df_plot_34)
            T_cbm_output_3.append(cbm_output_3)
            T_cbm_output_4.append(cbm_output_4)
            T_forest_type_base.append(forest_type_base)
            T_emission_difference.append(emission_difference)

        bd1_values, cs1_values = tradeoff_biodiversity_cs(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        epsilon, cs_max = epsilon_computer(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        hv2_values, cs2_values = tradeoff_hv_cs(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, epsilon, cs_max, n=4, solver=ws3.opt.SOLVER_PULP)
        hv3_values, bd3_values = tradeoff_hv_biodiversity(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)


        import os
        session_path = f"./sessions/{session_id}"
        # os.makedirs(session_path, exist_ok=True)
        
        # Debug result contents
        print("Dumping results to:", session_path)
        print("Data keys:", {
            'T_df_plot_12': len(T_df_plot_12),
            'T_cbm_output_1': len(T_cbm_output_1),
            'T_cbm_output_2': len(T_cbm_output_2),
            # ... add more if needed
        })
        # Save all data to session folder
        with open(f"{session_path}/results.pkl", "wb") as f:
            pickle.dump({
                'T_df_plot_12': T_df_plot_12,
                'T_cbm_output_1': T_cbm_output_1,
                'T_cbm_output_2': T_cbm_output_2,
                'T_df_plot_34': T_df_plot_34,
                'T_cbm_output_3': T_cbm_output_3,
                'T_cbm_output_4': T_cbm_output_4,
                'T_forest_type_base': T_forest_type_base,
                'T_forest_type_alt': T_forest_type_alt,
                'T_emission_difference': T_emission_difference,
                'bd1_values': bd1_values,
                'cs1_values': cs1_values,
                'hv2_values': hv2_values,
                'cs2_values': cs2_values,
                'hv3_values': hv3_values,
                'bd3_values': bd3_values,
            }, f)



        msg = "Analysis complete. Switch tabs to view results."
        return "done", msg, True

    except Exception as e:
        return "error", f"Error: {str(e)}", False


# Callback for showing status messages (in progress, done, etc.)
@app.callback(
    Output("analysis_status_msg", "children"),
    Input("analysis_status_store", "data")
)
def update_status_message(status):
    if status == "in_progress":
        return html.Div("Analysis is in progress...", style={"color": "orange"})
    elif status == "done":
        return html.Div("Analysis is done. Look at the results below.", style={"color": "green"})
    elif status == "error":
        return html.Div("An error occurred during analysis.", style={"color": "red"})
    elif status == "reset":
        return ""
    else:
        return ""



@app.callback(
    Output("geojsonComp", "data"),
    Output("aoi-coordinates", "data"),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('session-id', 'data'),
    prevent_initial_call=True
)
def update_output(contents, filename, session_id):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode()
        geojson_data = json.loads(decoded)

        if isinstance(geojson_data, dict) and 'features' in geojson_data:
            for feature in geojson_data['features']:
                geometry = feature["geometry"]
                if geometry["type"] == "Polygon":
                    coords = geometry["coordinates"][0]

                    # Save to disk
                    os.makedirs(f"./sessions/{session_id}", exist_ok=True)
                    with open(f"./sessions/{session_id}/aoi.json", "w") as f:
                        json.dump(coords, f)

                    # Return for storage in memory too
                    return geojson_data, coords
    return dash.no_update, dash.no_update




if __name__ == '__main__':
    app.run(debug=True)
