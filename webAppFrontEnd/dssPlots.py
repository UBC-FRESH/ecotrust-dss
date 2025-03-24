############################################################################
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
