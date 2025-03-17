from dash import Dash, dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc
import base64
import json
import dash_leaflet as dl
import geopandas as gpd
############################################################################
######Parameters that will be passed to the backend ########################
base_year_val = 0
horizon_val = 0
period_length_val = 0
max_age_val = 0
num_of_steps_val = 0
max_harvest_val = 0
scenario_val = "Scenario 1"
objective_val = "Objective 1"

#shapefile_path = './data/shp_files/tsa01.shp'
#stands_org = gpd.read_file(shapefile_path, engine = 'pyogrio', use_arrow = True)
#stands_org = stands_org.to_crs(epsg=4326)
#abridgedStands = stands_org.head(10)

############################################################################
############################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, serve_locally=True, requests_pathname_prefix="/container11-port8002/")
#app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Tab One', value='tab-1-example-graph'),
        dcc.Tab(label='Tab Two', value='tab-2-example-graph'),
        dcc.Tab(label='Tab Three', value='tab-3-example-graph'),
        dcc.Tab(label='Tab Four', value='tab-4-example-graph'),
        dcc.Tab(label='Tab Five', value='tab-5-example-graph'),
        dcc.Tab(label='Tab Six', value='tab-6-example-graph'),
    ]),
    html.Div(id='tabs-content-example-graph')
], style={'padding': 10, 'flex': 1, 'border':'2px gray solid', 'height': '40vh'})

])

############################################################################
############################################################################

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
    print(base_year)
    print(horizon)
    print(period_length)
    print(max_Age)
    print(num_of_steps)
    print(max_harvest)
    print(scenario)
    print(objective)
    print(n_clicks)
    return "Done"

@callback(Output("geojsonComp", "data"),
          Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        content_type, content_string = list_of_contents.split(',')
        decodedeStuff = base64.b64decode(content_string).decode()
        json_object  = json.loads(decodedeStuff)
        return json_object
'''        print(list_of_contents)
        print(decodedeStuff)
    children = [
    '       parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children'''

if __name__ == '__main__':
    app.run(debug=True)
