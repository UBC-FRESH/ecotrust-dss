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

    scenarioBarGraph.update_layout(height=400, width=1800, title_text="Scenarios")
    return scenarioBarGraph


def buildStackedBarGraph(period_x, forest_area_stack1, forest_area_stack2):
    stackedBarChart = go.Figure(data=[
        go.Bar(name='Primary forest', x=period_x, y=forest_area_stack1),
        go.Bar(name='Secondary forest', x=period_x, y=forest_area_stack2)
    ])
    stackedBarChart.update_layout(barmode='stack')
    stackedBarChart.update_xaxes(title_text="Period")
    stackedBarChart.update_yaxes(title_text="Forest area")
    return stackedBarChart

def drawTradeOffCurve(_X, _Y, xLabel,yLabel):
    tradeOffFig = go.Figure()
    tradeOffFig.add_trace(go.Scatter(x=_X, y=_Y, mode='lines+markers', name='Pareto Front'))
    tradeOffFig.update_xaxes(title_text=xLabel)
    tradeOffFig.update_yaxes(title_text=yLabel)
    tradeOffFig['data'][0]['showlegend'] = True
    tradeOffFig.update_layout(height=400, width=1800, title_text="Tradeoff Curve")
    return tradeOffFig



############################################################################
######Parameters that will be passed to the backend ########################
print("start")
base_year_val = 0
horizon_val = 0
period_length_val = 0
max_age_val = 0
num_of_steps_val = 0
max_harvest_val = 0
scenario_val = "Scenario 1"
objective_val = "Objective 1"
json_object_val = None
###########
# Initialize the input parameters
base_yearr = 2020
horizonn = 10
period_lengthh = 10
max_agee = 1000
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
bd1_values = []
cs1_values = []
hv2_values = []
cs2_values = []
hv3_values = []
bd3_values = []
# df_plot_12 = []
# cbm_output_1 = []
# cbm_output_2 = []
# df_plot_34 = []
# cbm_output_3 = []
# cbm_output_4 = []
T_df_plot_12 = []
T_cbm_output_1 = []
T_cbm_output_2 = []
T_df_plot_34 = []
T_cbm_output_3 = []
T_cbm_output_4 = []
###################
yld = pd.read_csv('./data/yld.csv')
yld['AU'] = yld['AU'].astype(int)
canf = pd.read_csv('data/canfi_species_revised.csv')
canf = canf[['name','canfi_species']].set_index('name')
##################
#shapefile_path = './data/shp_files/tsa01.shp/stands.shp'
shapefile_path = './data/shp_files/tsa17_test.shp/stands selection.shp'
stands_org = gpd.read_file(shapefile_path, engine = 'fiona', use_arrow = True)
stands_org = stands_org.to_crs(epsg=3005)
abridgedStands = stands_org   #.head(10) #only first 10 stands for testing purpose
print(abridgedStands)
print("got stands")
currentSelectedAreaCood = []

############################################################################
############################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = Dash(__name__, external_stylesheets=external_stylesheets, serve_locally=True, requests_pathname_prefix="/container11-port8002/")
server = app.server

app.layout =html.Div( [ html.Div([
    html.Div(children=[
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
    if tab == 'scn-1-graph':
        return html.Div([
            html.H3('Scenarios'),
            # dcc.Graph( figure= buildScenarioBarGraph(barGraphX, barGraphY, barGraphX, barGraphY,barGraphX, barGraphY) ),
            html.H3('Area primary secondary forest'),
            # dcc.Graph(figure=buildStackedBarGraph(barGraphX, stackedBarGraphY1, stackedBarGraphY2))
        ])
    elif tab == 'scn-2-graph':
        return html.Div([
            html.H3('Scenarios'),
            # dcc.Graph(figure=buildScenarioBarGraph(barGraphX, barGraphY, barGraphX, barGraphY, barGraphX, barGraphY)),
            html.H3('Area primary secondary forest'),
            # dcc.Graph(figure=buildStackedBarGraph(barGraphX, stackedBarGraphY1, stackedBarGraphY2))
        ])
    elif tab == 'tdoff-1-graph':
        return html.Div([
            html.H3('Tradeoff Curve'),
            dcc.Graph(figure=drawTradeOffCurve(cs1_values, bd1_values, "Carbon Stock","Biodiversity"))
            # dcc.Graph(figure=drawTradeOffCurve(tradeoff_x, tradeoff_y, "Carbon Stock","Biodiversity"))
        ])
    elif tab == 'tdoff-2-graph':
        return html.Div([
            html.H3('Tradeoff Curve'),
            dcc.Graph(figure=drawTradeOffCurve(cs2_values, hv2_values, "Biodiversity", "Harvested Volume"))
            # dcc.Graph(figure=drawTradeOffCurve(tradeoff_x, tradeoff_y, "Biodiversity", "Harvested Volume"))
        ])
    elif tab == 'tdoff-3-graph':
        return html.Div([
            html.H3('Tradeoff Curve'),
            dcc.Graph(figure=drawTradeOffCurve(bd3_values, hv3_values, "Carbon Stock", "Harvested Volume"))
            # dcc.Graph(figure=drawTradeOffCurve(tradeoff_x, tradeoff_y, "Carbon Stock", "Harvested Volume"))
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
def mycallback(base_year, horizon, period_length, max_Age, num_of_steps, max_harvest, scenario, objective, n_clicks):#
    #print(base_year)
    #print(horizon)
    #print(period_length)
    #print(max_Age)
    #print(num_of_steps)
    #print(max_harvest)
    #print(scenario)
    #print(objective)
    #print(n_clicks)

    msgShow = "none selected"
    global currentSelectedAreaCood
    global T_df_plot_12
    global T_cbm_output_1
    global T_cbm_output_2
    global T_df_plot_34
    global T_cbm_output_3
    global T_cbm_output_4
    numOfPointsInPoly = len(currentSelectedAreaCood)
    print(currentSelectedAreaCood)
    print(numOfPointsInPoly)
    print("its OK")

    if(numOfPointsInPoly > 2):
        selPoly = Polygon(currentSelectedAreaCood)
        gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[selPoly])
       # sjoin_results = gpd.sjoin(abridgedStands, gdf, how='left', predicate='within')
        afterDropping = abridgedStands  # sjoin_results.dropna()
        print("num of stands got is")
        print(afterDropping)
        stands = inventory_processing(afterDropping, canf)
        print(stands)
        print("stands got")
        curve_points_table = curve_points_generator(stands, yld, canf)
        print(curve_points_table)
        print("curve points table got")
        print(horizonn)
        fm = fm_bootstrapper(base_yearr, horizonn, period_lengthh, max_agee, stands, curve_points_table, tvy_name)
        print("fm is created")
        c_curves_p, c_curves_f = carbon_curve_points(fm)
        print("c and f points are received")
        plugin_c_curves(fm, c_curves_p, c_curves_f)
        bootstrap_ogi(fm)
        print("all curves are got")
        epsilon, cs_max = epsilon_computer(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=10, solver=ws3.opt.SOLVER_PULP)
        print("epsilon")
        print(epsilon)
        for scenario_name in scenario_names:
            print(f"Running for {case_study}_{obj_mode}_{scenario_name}...")
            df_plot_12, cbm_output_1, cbm_output_2, df_plot_34, cbm_output_3, cbm_output_4 = results_scenarios(fm, 
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
            T_df_plot_12.append(df_plot_12)
            T_cbm_output_1.append(cbm_output_1)
            T_cbm_output_2.append(cbm_output_2)
            T_df_plot_34.append(df_plot_34)
            T_cbm_output_3.append(cbm_output_3)
            T_cbm_output_4.append(cbm_output_4)          
        print("opt is done")
        print(T_df_plot_12)
        global bd1_values
        global cs1_values
        bd1_values, cs1_values = tradeoff_biodiversity_cs(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        print("tradeoff1 is done")
        epsilon, cs_max = epsilon_computer(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        global hv2_values
        global cs2_values
        hv2_values, cs2_values = tradeoff_hv_cs(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, epsilon, cs_max, n=4, solver=ws3.opt.SOLVER_PULP)
        print("tradeoff2 is done")
        global hv3_values
        global bd3_values
        hv3_values, bd3_values = tradeoff_hv_biodiversity(fm, clt_percentage, hwp_pool_effect_value, displacement_effect, release_immediately_value, n=4, solver=ws3.opt.SOLVER_PULP)
        print("tradeoff3 is done")
        numOfHits = afterDropping.shape[0]
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
