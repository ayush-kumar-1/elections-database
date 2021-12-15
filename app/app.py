#Imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.figure_factory as ff

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib
import plotly.express as px
import requests 
import json
import plotly.graph_objects as go

#Declare Dash App
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Election Statistics"

server = app.server
app.config.suppress_callback_exceptions = True

# ------ API functions ------
def get_results_by_county(sheet_number=2, year = 2016, month = 11, result_column="total_votes"): 
    """
    Uses api endpoint to get the total votes aggregated to the county level. 
    Parameters (all optional): 
    ------------------------------------------------
    year (default 2016) - the year of the election
    month (default 11) - the month of th election
    sheet_number (default 2) - the contest number of the election
    result_column (default total_votes) Options [election_day, provisional, absentee_by_mail, advance_in_person, total_votes]   
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"sheet_number": sheet_number, "year": year, "month": month, "result_column": result_column}
    response = requests.get(invoke_url + "/get_results", params=params)
    df = pd.read_json(response.text)
    
    return df

def get_turnout_by_county(year=2016, month=11, race=None, gender=None, age_grp=None): 
    """
    Uses api endpoint to the turnout by demographic with optional filtering by a single gender, 
    single race, and/or single age group. 
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"year": year, "month": month}
    if race: 
        params["race"] = race 
    if gender: 
        params["gender"] = gender
    if age_grp: 
        params["age_grp"] = age_grp

    response = requests.get(invoke_url + "/get_turnout", params=params)
    return pd.read_json(response.text)

def get_distribution(county_name="Fulton", year=2016, month=11, axis="age_grp", metric="voted"):
    """
    Uses api endpoint to get the distribution of the metric by the axis. 
    """
    invoke_url = "https://qp4b96543m.execute-api.us-east-2.amazonaws.com/active"
    params = {"county_name": county_name, "year": year, "month": month, "axis": axis, "metric": metric}
    response = requests.get(invoke_url + "/get_distribution", params=params)
    return pd.read_json(response.text)


# ------ Get data from API ------
results = get_results_by_county()
counties = results['county_name']

result_opt = ['election_day', 'provisional', 'absentee_by_mail', 'advance_in_person', 'total_votes'] 

#Get Contest - Sheet translation Data
sheets = pd.read_excel('detail.xls.xlsx')
sheets = sheets.drop([0, 1,2,3])
sheets = sheets.rename(columns = {'Unnamed: 0':'sheet','Unnamed: 1':'contest'})
contests = sheets['contest'].tolist()

#List of available years
years = ['2016']



# ------ Countywide Election Results ------
def county_results(county, contest, year, value):
	#convert contest name to sheet number
	con = sheets[sheets['contest'] == contest]
	con = con.iloc[0]['sheet']
	
	#get results by county
	countyResults = get_results_by_county(con,year,11,value)
	
	#get list of candidates
	cand = list(countyResults.columns)
	cand.pop(0)
	
	#column_list = list(results)
	county_results = countyResults[(countyResults['county_name'] == county)]
	county_results = county_results.T
	county_results.reset_index(inplace=True)
	#county_results = county_results.rename(columns = {'index':'Candidate'})
	#county_results = county_results.rename(columns = {0:'votes'})
	county_results.columns.values[0] = 'Candidate'
	county_results.columns.values[1] = "votes"
	county_results = county_results.drop([0])
	fig = px.histogram(county_results, x="Candidate", y="votes",title="Countywide Results")
	fig.update_layout(autosize=True,width=300,height=250,margin=dict(
			l=65,
			r=50,
			b=0,
			t=30
		),paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)')
	return fig

# ------ Age histogram ------
def age_histogram(county):
	df = get_distribution(county)
	fig = px.histogram(df, x="age_grp", y="voted")
	fig.update_layout(autosize=True,width=350,height=230,margin=dict(
        l=50,
        r=50,
        b=0,
        t=10
    ),)
	return fig

# ------ Gender Histogram ------
def gender_histogram(county):
	df = get_distribution(county, 2016, 11, "gender", metric="voted")
	fig = px.histogram(df, x="gender", y="voted")
	fig.update_layout(autosize=True,width=350,height=190,margin=dict(
        l=50,
        r=50,
        b=0,
        t=10
    ),)
	return fig

# ------ Race Histogram ------
def race_histogram(county):
	df = get_distribution(county, 2016, 11, "race", metric="voted")
	fig = px.histogram(df, x="race", y="voted")
	fig.update_layout(autosize=True,width=350,height=230,margin=dict(
        l=50,
        r=50,
        b=10,
        t=10
    ),)
	return fig

# HTML Div containing charts for age, gender, and race; and county selector dropdown menu
def graphs():
	return html.Div(id = "graph-section", children = [
			html.Div(id = "county-select", children = [ 
                html.B("Select County"),
                    dcc.Dropdown(id = "county_drop_select",
                        options=[{"label": i, "value": i} for i in counties], value=counties[0])]),
            dcc.Graph(id = "age_histogram"),
            dcc.Graph(id = "gender_histogram"),
            dcc.Graph(id = "race_histogram")])

# ------ Statewide Election Results ------
def state_results(contest, year, value):
	#convert contest name to sheet number
	con = sheets[sheets['contest'] == contest]
	con = con.iloc[0]['sheet']
	
	#get results by county
	countyResults = get_results_by_county(con,year,11,value)
	
	#get list of candidates
	cand = list(countyResults.columns)
	cand.pop(0)
	
	#column_list = list(countyResults)
	#column_list.remove("county_name")
	state_wide = pd.DataFrame({'votes':countyResults[cand].sum(axis=0)})
	state_wide.reset_index(inplace=True)
	state_wide = state_wide.rename(columns = {'index':'Candidate'})
	fig = px.histogram(state_wide, x="Candidate", y="votes", title="Statewide Results",)
	fig.update_layout(autosize=True,width=300,height=250,margin=dict(
        l=50,
        r=50,
        b=0,
        t=30
    ),paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)')	
	return fig

candidate_order = []
# Georgia Choropleth Map 
def generate_map(contest, year, value):
	# -- Georgia Choropleth Map Data
	FIPS_df = pd.read_csv("https://raw.githubusercontent.com/fhossain75/georgia-election-map/main/data/georgiaFIPS.csv")
	
	#convert contest name to sheet number
	con = sheets[sheets['contest'] == contest]
	con = con.iloc[0]['sheet']
	
	#get results by county
	countyResults = get_results_by_county(con,year,11,value)
	
	#get list of candidates
	cand = list(countyResults.columns)
	cand.pop(0)
	
	candidate_order.extend(cand)

	countyResults['winner'] = countyResults[cand].idxmax(axis=1)
	countyResults.insert(0, "FIPS", FIPS_df["FIPS"])
	fips = countyResults['FIPS'].tolist()
	winners = countyResults['winner'].tolist()
	colorscale = ["#DE0100", "#1405BD", "#FFFF00"]
	fig = ff.create_choropleth(
		fips = fips, values = winners, scope = ['Georgia'], colorscale = colorscale, 
		round_legend_values = True,
		plot_bgcolor = 'rgb(229,229,229)',
		paper_bgcolor = 'rgb(229,229,229)',
		legend_title = 'Majority Vote by County',
		county_outline = {'color': 'rgb(255,255,255)', 'width': 0.5},
		exponent_format = True
    )
	fig.layout.template = None
	fig.update_layout(autosize = True, width = 1000, height = 500)
	return fig

# HTML Div containing charts for age, gender, and race; and county selector dropdown menu
#def map_graphs():
#	return html.Div(id = "map-section", children=[
#						html.Div(id="state-wide"),
#						html.Div(id="county-wide"),
#                        dcc.Graph(id='state-map'),
#                    ], )


# ------ State Map Data control card: Contest, Year, Value dropdowns 
def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Contest"),
            dcc.Dropdown(
                id="contest_select",
                options=[{"label": i, "value": i} for i in contests],
                value=contests[0],
            ),
            html.Br(),
            html.P("Select Year"),
            dcc.Dropdown(
                id="year_select",
                options=[{"label": i, "value": i} for i in years],
                value=years[0],
            ),
            html.Br(),
            html.P("Select Value"),
            dcc.Dropdown(
                id="value_select",
                options=[{"label": i, "value": i} for i in result_opt],
                value=result_opt[0],
            ),
            html.Br(),
            html.Br(),
            
        ],
    )



# ------ APPLICATION LAYOUT ------
app.layout = html.Div(
    id="app-container",
    children=[
        
        # Left column (GA Map, state and county results graphs)
        html.Div(
            id="left-column",
            className="eight columns",
            children=[
                html.Div(
                    id="map-graphs",
                    children=[
						html.Div(id="state-wide",children=dcc.Graph(id="state-graph"),),
						html.Div(id="county-wide",children=dcc.Graph(id='county-bar'),),
                        dcc.Graph(id='state-map'),
                    ], 
                ),
            ],            
        ),
		html.Div(
            id="banner2",
            className="four columns",
            children=[generate_control_card()]
            + [
                html.Div(
                    ["initial child"], id="election-control", style={"display": "none"}
                )
            ],
        ),
		# Right column (County select, age, gender, race graphs)
        html.Div(
            id="right-column",
            className="eight columns",
            children=[graphs()]
            + [
                html.Div(
                    ["initial child"], id="graphs", style={"display": "none"}
                )
            ],   
        ),
    ],
)


# County Select call back
@app.callback(
    [Output("county-bar", "figure"), Output("age_histogram", "figure"), Output("gender_histogram", "figure"), Output("race_histogram", "figure")],
    [Input('county_drop_select','value'),Input('contest_select','value'), Input('year_select','value'), Input('value_select','value')],
)

def update_charts(county_drop_select, contest_select, year_select, value_select):
	return county_results(county_drop_select,contest_select, year_select, value_select), age_histogram(county_drop_select), gender_histogram(county_drop_select), race_histogram(county_drop_select)

# Map Select call back
@app.callback(
    [Output("state-graph", "figure"), Output("state-map", "figure")],
    [Input('contest_select','value'), Input('year_select','value'), Input('value_select','value')],
)


def update_map(contest_select, year_select, value_select):
	
	return state_results(contest_select, year_select, value_select), generate_map(contest_select,year_select,value_select)

# ------ Run the server ------
if __name__ == "__main__":
    app.run_server(debug=True)

