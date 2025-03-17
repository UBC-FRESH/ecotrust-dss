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
from IPython.display import display
import time
import pickle
import os
import ws3.forest, ws3.core
import csv
from functools import partial, wraps
import distance
import operator
import shutil
from IPython.display import display
import libcbm
from util import compile_events, cbm_report, compile_scenario_maxstock, plot_scenario_maxstock, run_cbm_emissionstock, run_scenario, plugin_c_curves, plugin_c_curves, cbm_report_both, compare_ws3_cbm, compare_ws3_cbm_both, track_system_stock, track_system_emission, compile_scenario_minemission, plot_scenario_minemission, kpi_age, kpi_species, cmp_c_ss, cmp_c_se, results_scenarios, bootstrap_ogi, compare_kpi_age, epsilon_computer, tradeoff_biodiversity_cs, tradeoff_hv_cs, tradeoff_hv_biodiversity, inventory_processing, curve_points_generator, fm_bootstrapper, carbon_curve_points
############################################################################
######Parameters that will be passed to the backend ########################
base_year = 2020
horizon = 10
period_length = 10
max_age = 1000
n_steps = 100
tvy_name = 'totvol'
max_harvest = 1.0
case_study = 'ecotrust'
scenario_names = ['lowest carbon stock', 'business as usual', '40% of highest carbon stock', '60% of highest carbon stock', '20% of highest carbon stock', 'highest carbon stock']
obj_mode = 'max_hv'
hwp_pool_effect_value = 0
release_immediately_value = 0
displacement_effect = 0
clt_percentage = 0
credibility = 0
budget_input = 10000000

base_year_val = 2020
horizon_val = 0
period_length_val = 0
max_age_val = 0
num_of_steps_val = 0
max_harvest_val = 0
scenario_val = "Scenario 1"
objective_val = "Objective 1"
json_object_val = None

yld = pd.read_csv('./data/yld.csv')
yld['AU'] = yld['AU'].astype(int)

canf = pd.read_csv('data/canfi_species_revised.csv')
canf = canf[['name','canfi_species']].set_index('name')
shapefile_path = 'data/shp_files/tsa01.shp'
stands_org = gpd.read_file(shapefile_path, engine = 'pyogrio', use_arrow = True)
stands_org = stands_org.to_crs(epsg=4326)
abridgedStands = stands_org.head(10)#only first 10 stands for testing purpose
currentSelectedAreaCood = []
#check num of rows in abrighedStadns, or print (first row data) 

############################################################################
############################################################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, serve_locally=True, requests_pathname_prefix="/container11-port8002/")
server = app.server

app.layout =html.Div( [ html.Div([
    html.Div(children=[
        dbc.Row(
            [
                dbc.Col(html.Div("Base Year")),
                dbc.Col(dcc.Input(
                    id="base_year_id", type="number", placeholder="Base Year",
                    min=1900, max=2999, step=1, style={"min-width": "100%"}
                )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Horizon")),
                dbc.Col(dcc.Input(
                    id="horizon_id", type="number", placeholder="Horizon",
                    min=1900, max=2999, step=1, style={"min-width": "100%"}
                )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Period Length")),
                dbc.Col(dcc.Input(
                    id="period_length_id", type="number", placeholder="Period Length",
                    min=1, max=100, step=1, style={"min-width": "100%"}
                )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Max Age")),
                dbc.Col(dcc.Input(
                    id="max_age_id", type="number", placeholder="Max Age",
                    min=1, max=1000, step=1, style={"min-width": "100%"}
                )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Number of Steps")),
                dbc.Col(dcc.Input(
                    id="num_of_steps_id", type="number", placeholder="Number of Steps",
                    min=1, max=10000, step=1, style={"min-width": "100%"}
                )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Max Harvest")),
                dbc.Col(dcc.Input(
                    id="max_harvest_id", type="number", placeholder="Max Harvest",
                    min=0, max=100, step=1, style={"min-width": "100%"}
                )
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Scenarios")),
                dbc.Col(dcc.Dropdown( ['Scenario 1', 'Scenario 2', 'Scenario 3','Scenario 4', 'Scenario 5', 'Scenario 6'], 'Scenario 1', clearable=False, id = "scenarios_id", )),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Objective")),
                dbc.Col(dcc.Dropdown(['Objective 1', 'Objective 2', 'Objective 3','Objective 4'], 'Objective 1',clearable=False, id = "objective_id", )),
            ]
        ),
        dbc.Row(
            [
                dbc.Col( dcc.Upload(html.Button('Upload Area of Interest', id = "upload_area_button_id", style = {'width' : '100%'}), id='upload-data'), width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Button('Analyse',id = "analyse_button_id", style = {'width' : '100%'}),width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Label( 'Waiting', id="wait_label_id", style={'width': '100%'}),width={"size": 6, "offset": 3}, style={"margin-top": "10px"}),
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
              Input('tabs-graphs', 'value'))
def render_content(tab):

    #######################scenario bar graphs#############################################
    #first dummy data set for first set of bar graphs
    barGraphX = [1,2,3,4,5,6,7,8,9,10]
    barGraphY = [600,550,600,500,600,550,600,500,600,500]
    scenarioBarGraph = make_subplots(rows=1, cols=3,horizontal_spacing=0.1)
    scenarioBarGraph.add_trace(go.Bar(x=barGraphX, y=barGraphY, name = "Harvested area (ha)"),
                  row=1, col=1)
    scenarioBarGraph.update_xaxes(title_text="Harvested area (ha)", row=1, col=1)
    scenarioBarGraph.add_trace(go.Bar(x=barGraphX, y=barGraphY, name = "Harvested volume (m3)"),
                  row=1, col=2)
    scenarioBarGraph.update_xaxes(title_text="Harvested volume (m3)", row=1, col=2)
    scenarioBarGraph.add_trace(go.Bar(x=barGraphX, y=barGraphY, name = "Growing Stock (m3)"),
                  row=1, col=3)
    scenarioBarGraph.update_xaxes(title_text="Growing Stock (m3)", row=1, col=3)
    scenarioBarGraph.update_layout(height=400, width=1800, title_text="Scenarios")
    #######################stacked bar graphs#############################################
    stackedBarGraphY1 = [20000,19000,18000,17000,16000,15000,14000,13000,12000,11000]
    stackedBarGraphY2 = [1000,2000,3000,4000,5000,6000,7000,8000,9000,10000]

    stackedBarChart = go.Figure(data=[
        go.Bar(name='Primary forest', x=barGraphX, y=stackedBarGraphY1),
        go.Bar(name='Secondary forest', x=barGraphX, y=stackedBarGraphY2)
    ])
    stackedBarChart.update_layout(barmode='stack')
    stackedBarChart.update_xaxes(title_text="Period")
    stackedBarChart.update_yaxes(title_text="Forest area")
    #######################line graphs#############################################


    if tab == 'scn-1-graph':
        return html.Div([
            html.H3('Scenarios'),
            dcc.Graph( figure= scenarioBarGraph),
            html.H3('Area primary secondary forest'),
            dcc.Graph(figure=stackedBarChart)
        ])
    elif tab == 'scn-2-graph':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs-dcc',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [5, 10, 6],
                        'type': 'bar'
                    }]
                }
            )
        ])




resCounterIndex = 0
@app.callback(Output('wait_label_id','children' ), [],
              [
                  State('base_year_id', 'value'),
                  State('horizon_id', 'value'),
                  State('period_length_id', 'value'),
                  State('max_age_id', 'value'),
                  State('num_of_steps_id', 'value'),
                  State('max_harvest_id', 'value'),
                  State('scenarios_id', 'value'),
                  State('objective_id', 'value'),
                  Input("analyse_button_id", "n_clicks"),
              ])
# resCounterIndex = 0

# @app.callback(
#     Output('wait_label_id', 'children'),
#     [Input("analyse_button_id", "n_clicks")],  # Input must be in a list
#     [
#         State('base_year_id', 'value'),
#         State('horizon_id', 'value'),
#         State('period_length_id', 'value'),
#         State('max_age_id', 'value'),
#         State('num_of_steps_id', 'value'),
#         State('max_harvest_id', 'value'),
#         State('scenarios_id', 'value'),  # Ensure this ID exists in the layout
#         State('objective_id', 'value'),
#         State('hwp_pool_effect_id', 'value'),
#         State('release_immediately_id', 'value'),
#         State('displacement_effect_id', 'value'),
#         State('clt_percentage_id', 'value'),
#         State('credibility_id', 'value'),
#         State('budget_input_id', 'value')
#     ]
# )

def mycallback(base_year, horizon, period_length, max_Age, num_of_steps, max_harvest, scenario, objective, n_clicks):#

    print(base_year)
    print(horizon)
    print(period_length)
    print(max_Age)
    print(num_of_steps)
    print(max_harvest)
    print(scenario)
    print(objective)
    print(n_clicks)
    msgShow = "none selected"
    #global currentSelectedAreaCood
    numOfPointsInPoly = len(currentSelectedAreaCood)
    print(currentSelectedAreaCood)
    print("after area selection")
    print(numOfPointsInPoly)
    if(numOfPointsInPoly > 2):
        print("got poly")
        selPoly = Polygon(currentSelectedAreaCood)
        gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[selPoly])
        sjoin_results = gpd.sjoin(abridgedStands, gdf, how='left', predicate='within')
   # if canf is global and you want to manipulate, edit, 
   #glbal canf 
   #canf = something...
        stands = inventory_processing(sjoin_results, canf)
        #print(stands.head(10))
        print("step1")
        print(sjoin_results)
        afterDropping = sjoin_results.dropna()
        numOfHits = afterDropping.shape[0]
        print(numOfHits)
    #start calling backend here, backend generates data that need to be plotted it gives 
    #back that data, store it here locally. that will be used by tabs for plotting.
        curve_points_table = curve_points_generator(stands, yld, canf)
        fm = fm_bootstrapper(base_year, horizon, period_length, max_age, stands, curve_points_table, tvy_name)
        c_curves_p, c_curves_f = carbon_curve_points(fm)
        plugin_c_curves(fm, c_curves_p, c_curves_f)
        bootstrap_ogi(fm)
        epsilon, cs_max = epsilon_computer(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=10, solver=ws3.opt.SOLVER_PULP)
        print('curves are done.')
        for scenario_name in scenario_names:
            print(f"Running for {case_study}_{obj_mode}_{scenario_name}...")
            results_scenarios(fm, 
                              clt_percentage, 
                              credibility, 
                              budget_input, 
                              n_steps, 
                              max_harvest, 
                              scenario_name, 
                              displacement_effect, 
                              hwp_pool_effect_value, 
                              release_immediately_value, 
                              case_study, 
                              obj_mode, 
                              epsilon,
                              cs_max,
                              pickle_output_base=False, 
                              pickle_output_alter=False)
        bd_values, cs_values = tradeoff_biodiversity_cs(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        epsilon, cs_max = epsilon_computer(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        hv_values, cs_values = tradeoff_hv_cs(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, epsilon, cs_max, n=4, solver=ws3.opt.SOLVER_PULP)
        hv_values, bd_values = tradeoff_hv_biodiversity(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        msgShow = "selected " + str(numOfHits)

    #global resCounterIndex
    #resCounterIndex= resCounterIndex + 1
    return msgShow#"Done " + str(resCounterIndex)

@callback(Output("geojsonComp", "data"),
          Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decodedeStuff = base64.b64decode(content_string).decode()
        json_object  = json.loads(decodedeStuff)

        if isinstance(json_object, dict):
            if 'features' in json_object:
                featData = json_object['features']
                for elem in featData:
                    geometryData = elem["geometry"]
                    if (geometryData["type"] == "Polygon"):
                        global currentSelectedAreaCood
                        listOfCoods = geometryData["coordinates"]
                        currentSelectedAreaCood = listOfCoods[0]
                        print("got curve coods")
                        print(currentSelectedAreaCood)
        return json_object

if __name__ == '__main__':
    app.run(debug=True)
