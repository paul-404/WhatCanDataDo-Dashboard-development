import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import requests
import plotly.graph_objects as go

from dash.dependencies import Input, Output

### Launch app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True # suppress callback errors
server = app.server
app.title="COVID-19 Live Analytics"

### Import Data from JHU CSSE & create country dataframe
# Import Data
df_cases_jhu = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
df_recovered_jhu = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
df_deaths_jhu = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")

# Country Dataframe: Create new dataframes with entries per country (sum over province) & rename columns to single words & drop Lat and Long columns
df_cases = df_cases_jhu.rename(columns={"Country/Region": "Country", "Province/State": "Province"}).groupby("Country").sum().reset_index().drop(["Lat", "Long"], axis=1)
df_recovered = df_recovered_jhu.rename(columns={"Country/Region": "Country", "Province/State": "Province"}).groupby("Country").sum().reset_index().drop(["Lat", "Long"], axis=1)
df_deaths = df_deaths_jhu.rename(columns={"Country/Region": "Country", "Province/State": "Province"}).groupby("Country").sum().reset_index().drop(["Lat", "Long"], axis=1)


### Call APIs for live counts world
live_all = requests.get("https://corona.lmao.ninja/all").json()

### Create Country Selection Lists
countries_top10 = ["US", "Italy", "Spain", "China", "Germany", "France", "Iran", "United Kingdom", "Switzerland", "Turkey"]
countries_top15 = ["US", "Italy", "Spain", "China", "Germany", "France", "Iran", "United Kingdom", "Switzerland", "Turkey", "Belgium", "Netherlands", "Austria", "Korea, South", "Canada"]
countries_top20 = ["US", "Italy", "Spain", "China", "Germany", "France", "Iran", "United Kingdom", "Switzerland", "Turkey", "Belgium", "Netherlands", "Austria", "Korea, South", "Canada", "Portugal", "Brazil", "Israel", "Norway", "Australia"]
countries_asia = ["China", "Korea, South", "Georgia", "Malaysia", "Philippines", "Japan", "Pakistan", "India", "Thailand", "Indonesia"]
countries_europe = ["Italy", "Spain", "Germany", "France",
"United Kingdom", "Switzerland", "Belgium", "Netherlands", "Austria", "Portugal"]
# Country selection depending on Measures:
countries_mask = ["China", "Korea, South", "Japan", "Singapore", "Taiwan*", "Czechia"]
countries_nomask = ["US", "Italy", "Spain", "Germany", "France", "United Kingdom"]
threshold = 100 # Minimum number of cases on first day for trend plots

### Create Dropdown options
dropdown_options = [{"label" : i, "value" : i} for i in df_cases["Country"].unique()]

### Create Map figure

#World Map
fig_world = go.Figure()
scale = df_cases["4/5/20"].max() # Use max cases in country on "4/5/20" as scaling factor
fig_world.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_cases['Country'],
        text = df_cases.iloc[:,-1],
        marker = dict(
            size = df_cases.iloc[:,-1]*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'red',
            opacity = 0.7,
            ),
        name='total confirmed'
        )
    )

df_recovered_size = df_recovered.iloc[:,-1] + df_deaths.iloc[:,-1] # Add Deaths to recovered size since deaths are displayed on top. This way at the end total confirmed size = total recovered size
fig_world.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_recovered['Country'],
        text = df_recovered.iloc[:,-1],
        marker = dict(
            size = df_recovered_size*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'green',
            opacity = 0.7,
            ),
        name='total recovered'
        )
    )

fig_world.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_deaths['Country'],
        text = df_deaths.iloc[:,-1],
        marker = dict(
            size = df_deaths.iloc[:,-1]*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'yellow',
            opacity = 0.7,
            ),
        name='total deceased'
        )
    )

fig_world.update_layout(
        title = 'World',
        showlegend = True,
        legend_orientation="h",
        legend=dict(x=0.25, y=0),
        height = 400,
        margin = {"r":0,"t":50,"l":0,"b":0},
        geo = dict(
            scope = 'world',
            landcolor = 'rgb(217, 217, 217)',
            showcountries = True,
            countrycolor = "white",
            coastlinecolor = "white",
            showframe = True,
            #lonaxis_range= [ -150, None ],
            #lataxis_range= [ -60, 90 ],
            projection_type = 'natural earth'
        )
    )

# Europe Map
fig_europe = go.Figure()

fig_europe.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_cases['Country'],
        text = df_cases.iloc[:,-1],
        marker = dict(
            size = df_cases.iloc[:,-1]*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'red',
            opacity = 0.7,
            ),
        name='total confirmed'
        )
    )

fig_europe.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_recovered['Country'],
        text = df_recovered.iloc[:,-1],
        marker = dict(
            size = df_recovered_size*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'green',
            opacity = 0.7,
            ),
        name='total recovered'
        )
    )

fig_europe.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_deaths['Country'],
        text = df_deaths.iloc[:,-1],
        marker = dict(
            size = df_deaths.iloc[:,-1]*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'yellow',
            opacity = 0.7,
            ),
        name='total deceased'
        )
    )

fig_europe.update_layout(
        title = 'Europe',
        showlegend = True,
        legend_orientation="h",
        legend=dict(x=0.25, y=0),
        height = 400,
        margin = {"r":0,"t":50,"l":0,"b":0},
        geo = dict(
            scope = 'europe',
            landcolor = 'rgb(217, 217, 217)',
            showcountries = True,
            countrycolor = "white",
            coastlinecolor = "white",
            showframe = True,
            #lonaxis_range= [ -150, None ],
            #lataxis_range= [ -60, 90 ],
            projection_type = 'natural earth'
        )
    )

# Asia Map
fig_asia = go.Figure()

fig_asia.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_cases['Country'],
        text = df_cases.iloc[:,-1],
        marker = dict(
            size = df_cases.iloc[:,-1]*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'red',
            opacity = 0.7,
            ),
        name='total confirmed'
        )
    )

fig_asia.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_recovered['Country'],
        text = df_recovered.iloc[:,-1],
        marker = dict(
            size = df_recovered_size*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'green',
            opacity = 0.7,
            ),
        name='total recovered'
        )
    )

fig_asia.add_trace(go.Scattergeo(
        locationmode = 'country names',
        locations = df_deaths['Country'],
        text = df_deaths.iloc[:,-1],
        marker = dict(
            size = df_deaths.iloc[:,-1]*1000/scale,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            color = 'yellow',
            opacity = 0.7,
            ),
        name='total deceased'
        )
    )

fig_asia.update_layout(
        title = 'Asia',
        showlegend = True,
        legend_orientation="h",
        legend=dict(x=0.25, y=0),
        height = 400,
        margin = {"r":0,"t":50,"l":0,"b":0},
        geo = dict(
            scope = 'asia',
            landcolor = 'rgb(217, 217, 217)',
            showcountries = True,
            countrycolor = "white",
            coastlinecolor = "white",
            showframe = True,
            #lonaxis_range= [ -150, None ],
            #lataxis_range= [ -60, 90 ],
            projection_type = 'natural earth'
        )
    )


### App Layout
app.layout = html.Div([
    html.Div([
        html.H1("COVID-19 Live Analytics"),
        dcc.Markdown("**Current Status: Under Construction!** The main purpose of this dashboard is to provide a simple, interactive tool to visualize publicly available data about the COVID-19 pandemic. All graphs rely on data collected by the team at [John Hopkins University CSSE](https://github.com/CSSEGISandData/COVID-19). Live counts above the graphs rely on [NovelCovid APIs](https://github.com/NOVELCOVID/API). Note: All graphs and figures only visualize the number of reported cases and not the actual case numbers. In addition, the  quantity and type of conducted tests, case definitions and reporting protocols may vary strongly between regions (e.g. regions with low number of conducted tests may have much higher actual case numbers than shown here).")
    ], className = "row"),
    dcc.Tabs(
        id="tabs-with-classes",
        value='tab-1',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='World',
                value='tab-1',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Country',
                value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Trends',
                value='tab-3', className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Models',
                value='tab-4',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Measures',
                value='tab-5',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Maps',
                value='tab-6',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ]),
    html.Div(id='tabs-content-classes')
], className='ten columns offset-by-one')

### Function to generate table
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

### Callbacks
# Callback Dropdown - KPIs
@app.callback(Output('card-cases', 'children'),
             [Input('my-dropdown', 'value')])
def update_children(X):
    return html.H3(str(f'{requests.get("https://corona.lmao.ninja/countries/"+str(X)).json()["cases"] :,}'), className="card-title")

@app.callback(Output('card-recovered', 'children'),
             [Input('my-dropdown', 'value')])
def update_children(X):
    return html.H3(str(f'{requests.get("https://corona.lmao.ninja/countries/"+str(X)).json()["recovered"] :,}'), className="card-title")

@app.callback(Output('card-deceased', 'children'),
             [Input('my-dropdown', 'value')])
def update_children(X):
    return html.H3(str(f'{requests.get("https://corona.lmao.ninja/countries/"+str(X)).json()["deaths"] :,}'), className="card-title")

# Callbacks Dropdown - Curves
@app.callback(Output('graph-confirmed', 'figure'),
             [Input('my-dropdown', 'value')])
def update_figure(X):
    fig = {
                                'data': [
                                    dict(
                                        x=df_cases.columns[1:],
                                        y=df_cases[df_cases['Country'] == i].sum()[1:],
                                        mode='lines+markers',
                                        opacity=0.7,
                                        marker={
                                            'size': 7,
                                            'line': {'width': 1}
                                        },
                                        line={
                                            'width': 5
                                        },
                                        name=i
                                    ) for i in [str(X)]
                                ],
                                'layout': dict(
                                    xaxis={'type': 'lin'},
                                    yaxis={'type': 'lin', 'title': 'Total Confirmed Cases'},
                                    margin={'l': 50, 'b': 100, 't': 0, 'r': 50},
                                    legend={'x': 1, 'y': 1},
                                    hovermode='closest',
                                    #paper_bgcolor='lightgrey',
                                    # title="Trend of total confirmed cases"
                                )
                            }
    return fig

@app.callback(Output('graph-deceased', 'figure'),
             [Input('my-dropdown', 'value')])
def update_figure(X):
    fig = {
                                'data': [
                                    dict(
                                        x=df_deaths.columns[1:],
                                        y=df_deaths[df_deaths['Country'] == i].sum()[1:],
                                        mode='lines+markers',
                                        opacity=0.7,
                                        marker={
                                            'size': 7,
                                            'line': {'width': 1},
                                            'color':'orange'
                                        },
                                        line={
                                            'width': 5,
                                            'color':'orange'
                                        },
                                        name=i
                                    ) for i in [str(X)]
                                ],
                                'layout': dict(
                                    xaxis={'type': 'lin'},
                                    yaxis={'type': 'lin', 'title': 'Total Deceased'},
                                    margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
                                    legend={'x': 1, 'y': 1},
                                    hovermode='closest',
                                    # title="Trend of total confirmed cases"
                                )
                            }
    return fig

@app.callback(Output('graph-daily', 'figure'),
             [Input('my-dropdown', 'value')])
def update_figure(X):
    fig={
                            'data': [
                                dict(
                                    x=df_cases.columns[1:],
                                    y=df_cases[df_cases['Country'] == i].sum()[1:].diff(),
                                    type='bar',
                                    opacity=0.7,
                                    name=i
                                ) for i in [str(X)]
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'title': 'Daily New Cases'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
                                legend={'x': 1, 'y': 1},
                                hovermode='closest',
                                # title="Trend of total confirmed cases"
                            )
                        }
    return fig

# Callback tabs
@app.callback(Output('tabs-content-classes', 'children'),
              [Input('tabs-with-classes', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
                html.Div([
                        html.Div([
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Total Cases:"),
                                        dbc.CardBody(
                                            [html.H3(str(f'{live_all["cases"] :,}'), className="card-title")]
                                        ),
                                    ],
                                    style={"width": "30rem"},
                                )
                        ], className="three columns"),
                        html.Div([
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Active Cases:"),
                                        dbc.CardBody(
                                            [
                                                html.H3(str(f'{live_all["active"] :,}'), className="card-title")
                                            ]
                                        ),
                                    ],
                                    style={"width": "30rem"},
                                )
                        ], className="three columns"),
                        html.Div([
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Total Recovered:"),
                                        dbc.CardBody(
                                            [
                                                html.H3(str(f'{live_all["recovered"] :,}'), className="card-title")
                                            ]
                                        ),
                                    ],
                                    style={"width": "30rem"},
                                )
                        ], className="three columns"),
                        html.Div([
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Total Deceased:"),
                                        dbc.CardBody(
                                            [
                                                html.H3(str(f'{live_all["deaths"] :,}'), className="card-title")
                                            ]
                                        ),
                                    ],
                                    style={"width": "30rem"},
                                )
                        ], className="three columns"),
                    ], className="row"),
                    html.Div([
                        html.Div([
                        dcc.Graph(
                            id='graph-confirmed-world',
                            figure={
                                'data': [
                                    dict(
                                        x=df_cases.columns[1:],
                                        y=df_cases.sum()[1:],
                                        mode='lines+markers',
                                        opacity=0.7,
                                        marker={
                                            'size': 7,
                                            'line': {'width': 1}
                                        },
                                        line={
                                            'width': 5
                                        },
                                        name="World"
                                    )
                                ],
                                'layout': dict(
                                    xaxis={'type': 'lin'},
                                    yaxis={'type': 'lin', 'title': 'Total Confirmed Cases'},
                                    margin={'l': 50, 'b': 100, 't': 0, 'r': 50},
                                    legend={'x': 1, 'y': 1},
                                    hovermode='closest',
                                    # title="Trend of total confirmed cases"
                                )
                            }
                        )
                        ], className="row"),
                    html.Div([
                    dcc.Graph(
                        id='graph-daily-world',
                        figure={
                            'data': [
                                dict(
                                    x=df_cases.columns[1:],
                                    y=df_cases.sum()[1:].diff(),
                                    type='bar',
                                    opacity=0.7,
                                    name="World"
                                )
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'title': 'Daily New Cases'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
                                legend={'x': 1, 'y': 1},
                                hovermode='closest',
                                # title="Trend of total confirmed cases"
                            )
                        }
                    )
                    ], className="row"),
                    html.Div([
                    dcc.Graph(
                        id='graph-deceased-world',
                        figure={
                            'data': [
                                dict(
                                    x=df_deaths.columns[1:],
                                    y=df_deaths.sum()[1:],
                                    mode='lines+markers',
                                    opacity=0.7,
                                    marker={
                                        'size': 7,
                                        'line': {'width': 1},
                                        'color':'orange'
                                    },
                                    line={
                                        'width': 5,
                                        'color':'orange'
                                    },
                                    name="World"
                                )
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'type': 'lin', 'title': 'Total Deceased'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
                                legend={'x': 1, 'y': 1},
                                hovermode='closest',
                                # title="Trend of total confirmed cases"
                            )
                        }
                    )
                    ], className="row"),
                    ])
        ])
    elif tab == 'tab-2':
        return html.Div([
                html.Div([
                    html.Div([
                        html.Label("Select a country:"),
                        dcc.Dropdown(
                            id="my-dropdown",
                            options=dropdown_options,
                            value="Germany",
                            placeholder="Select a country",
                        ),
                    ], className="three columns"),
                    html.Div([
                            dbc.Card(
                                [
                                    dbc.CardHeader("Total Cases:"),
                                    dbc.CardBody(id="card-cases", children=
                                        [
                                            html.H3(str(f'{requests.get("https://corona.lmao.ninja/countries/"+"Germany").json()["cases"] :,}'), className="card-title")
                                        ]
                                    )
                                ],
                                style={"width": "10rem"},
                            )
                    ], className="three columns"),
                    html.Div([
                            dbc.Card(
                                [
                                    dbc.CardHeader("Total Recovered:"),
                                    dbc.CardBody(id="card-recovered", children=
                                        [
                                            html.H3(str(f'{requests.get("https://corona.lmao.ninja/countries/Germany").json()["recovered"] :,}'), className="card-title")
                                        ]
                                    ),
                                ],
                                style={"width": "30rem"},
                            )
                    ], className="three columns"),
                    html.Div([
                            dbc.Card(
                                [
                                    dbc.CardHeader("Total Deceased:"),
                                    dbc.CardBody(id="card-deceased", children=
                                        [
                                            html.H3(str(f'{requests.get("https://corona.lmao.ninja/countries/Germany").json()["deaths"] :,}'), className="card-title")
                                        ]
                                    ),
                                ],
                                style={"width": "30rem"},
                            )
                    ], className="three columns"),
                ], className="row"),
                html.Div([
                    html.Div([
                    dcc.Graph(
                        id='graph-confirmed',
                        figure={
                            'data': [
                                dict(
                                    x=df_cases.columns[1:],
                                    y=df_cases[df_cases['Country'] == i].sum()[1:],
                                    mode='lines+markers',
                                    opacity=0.7,
                                    marker={
                                        'size': 7,
                                        'line': {'width': 1}
                                    },
                                    line={
                                        'width': 5
                                    },
                                    name=i
                                ) for i in ["Germany"]
                            ],
                            'layout': dict(
                                xaxis={'type': 'lin'},
                                yaxis={'type': 'lin', 'title': 'Total Confirmed Cases'},
                                margin={'l': 50, 'b': 100, 't': 0, 'r': 50},
                                legend={'x': 1, 'y': 1},
                                hovermode='closest',
                                #paper_bgcolor="rgb(245, 247, 249)",
                                #plot_bgcolor="rgb(245, 247, 249)"
                                # title="Trend of total confirmed cases"
                            )
                        }
                    )
                    ], className="twelve columns")
                ], className="row"),
                html.Div([
                    html.Div([
                    dcc.Graph(
                        id='graph-daily',
                        figure={
                            'data': [
                                dict(
                                    x=df_cases.columns[1:],
                                    y=df_cases[df_cases['Country'] == i].sum()[1:].diff(),
                                    type='bar',
                                    opacity=0.7,
                                    name=i
                                ) for i in ["Germany"]
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'title': 'Daily New Cases'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
                                legend={'x': 1, 'y': 1},
                                hovermode='closest',
                                # title="Trend of total confirmed cases"
                            )
                        }
                    )
                    ], className="twelve columns"),
                ], className="row"),
                html.Div([
                    html.Div([
                    dcc.Graph(
                        id='graph-deceased',
                        figure={
                            'data': [
                                dict(
                                    x=df_deaths.columns[1:],
                                    y=df_deaths[df_deaths['Country'] == i].sum()[1:],
                                    mode='lines+markers',
                                    opacity=0.7,
                                    marker={
                                        'size': 7,
                                        'line': {'width': 1},
                                        'color':'orange'
                                    },
                                    line={
                                        'width': 5,
                                        'color':'orange'
                                    },
                                    name=i
                                ) for i in ["Germany"]
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'type': 'lin', 'title': 'Total Deceased'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 50},
                                legend={'x': 1, 'y': 1},
                                hovermode='closest',
                                # title="Trend of total confirmed cases"
                            )
                        }
                    )
                    ], className="twelve columns"),
                ], className="row"),
        ])
    elif tab == 'tab-3':
        return html.Div([
                    dcc.Markdown('To show only one country, double-click on the country in the legend. Single-click on other countries in the legend to add them to the selection. Double-click again to reset the selection.'),
                    html.Div([
                        dcc.Graph(
                            id='graph-trend-1',
                            figure={
                                'data': [
                                    dict(
                                        y=df_cases[df_cases['Country'] == i].sum()[1:][df_cases[df_cases['Country'] == i].sum()[1:].gt(threshold)],
                                        mode='lines',
                                        opacity=0.7,
                                        marker={
                                            'size': 5,
                                            'line': {'width': 1},
                                        },
                                        name=i
                                    ) for i in df_cases["Country"].unique()
                                ],
                                'layout': dict(
                                    xaxis={'range':[0,120],'type': 'lin', 'title':'''Number of days since >100 cases'''},
                                    yaxis={'type': 'log', 'title': 'Total Confirmed Cases'},
                                    margin={'l': 100, 'b': 100, 't': 50, 'r': 100},
                                    legend={'x': 1, 'y': 1},
                                    hovermode='closest',
                                    title="Trend of confirmed cases",
                                )
                            }
                        )
                    ], className="row"),
                    html.Div([
                        dcc.Graph(
                            id='graph-trend-2',
                            figure={
                                'data': [
                                    dict(
                                        y=df_cases[df_cases['Country'] == i].sum()[1:][df_cases[df_cases['Country'] == i].sum()[1:].gt(threshold)],
                                        mode='lines+markers',
                                        opacity=0.7,
                                        marker={
                                            'size': 5,
                                            'line': {'width': 1}
                                        },
                                        name=i
                                    ) for i in countries_europe
                                ],
                                'layout': dict(
                                    xaxis={'range':[0,120],'type': 'lin', 'title':'''Number of days since >100 cases'''},
                                    yaxis={'range':[2,None], 'type': 'log', 'title': 'Total Confirmed Cases'},
                                    legend={'x': 1, 'y': 1},
                                    hovermode='closest',
                                    title="Countries with most cases in Europe"
                                )
                            }
                        )
                    ], className="row"),
                    html.Div([
                        dcc.Graph(
                            id='graph-trend-3',
                            figure={
                                'data': [
                                    dict(
                                        y=df_cases[df_cases['Country'] == i].sum()[1:][df_cases[df_cases['Country'] == i].sum()[1:].gt(threshold)],
                                        mode='lines+markers',
                                        opacity=0.7,
                                        marker={
                                            'size': 5,
                                            'line': {'width': 1}
                                        },
                                        name=i
                                    ) for i in countries_asia
                                ],
                                'layout': dict(
                                    xaxis={'range':[0,120],'type': 'lin', 'title':'''Number of days since >100 cases'''},
                                    yaxis={'range':[2,None], 'type': 'log', 'title': 'Total Confirmed Cases'},
                                    legend={'x': 1, 'y': 1},
                                    hovermode='closest',
                                    title="Countries with most cases in Asia"
                                )
                            }
                        )
                    ], className="row")
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.P('''Simulations/Projections by ML supported SEIR Model. Fit to currently available data (confirmed cases, active cases, measures, hospital capacity, ICU beds, ...). Goal: Visualize projections and effects of different measures in a way that can be understood by everybody. Display uncertainty of input data and projections.''')
            #generate_table(df_deathsf["Lat", "Long"], axis=1))
        ])
    elif tab == 'tab-5':
        return html.Div([
            html.Div([
                 dcc.Markdown('''Visualization of available data (total cases, critical cases, deaths, doubling times etc.) in combination with past actions (closing schools, closing borders, number of test, contact tracing, lockdown, social distancing, widespread public mask usage etc) to learn more about/display the effects of different actions. **Preliminary** example: Trends of countries with widespread public mask usage vs countries without widespread public mask usage.
                 **Caution: Correlation does not imply causation!** The number of reported cases is strongly influenced by many different factors such as each countries case definition, testing capacity (number of tests, type of tests, who is being tested, ...), official reporting protocols etc. In addition, the effect of a specific measure is dependent on other measures which may or may not take place at the same time. Furthermore, different strains of 2019-n-Cov may react to certain measures differently.'''),
            #     html.Div([
            #         html.Div([
            #         dcc.Graph(
            #             id='graph-trend-2',
            #             figure={
            #                 'data': [
            #                     dict(
            #                         y=df_cases[df_cases['Country'] == i].sum()[1:][df_cases[df_cases['Country'] == i].sum()[1:].gt(threshold)],
            #                         mode='lines+markers',
            #                         opacity=0.7,
            #                         marker={
            #                             'size': 5,
            #                             'line': {'width': 1}
            #                         },
            #                         name=i
            #                     ) for i in countries_nomask
            #                 ],
            #                 'layout': dict(
            #                     xaxis={'range':[0,45],'type': 'lin', 'title':'''Number of days since >100 cases'''},
            #                     yaxis={'range':[2,None], 'type': 'log', 'title': 'Total Confirmed Cases'},
            #                     legend={'x': 1, 'y': 1},
            #                     hovermode='closest',
            #                     title="Countries without widespread public mask usage"
            #                 )
            #             }
            #         )
            #         ], className="six columns"),
            #         html.Div([
            #         dcc.Graph(
            #             id='graph-trend-3',
            #             figure={
            #                 'data': [
            #                     dict(
            #                         y=df_cases[df_cases['Country'] == i].sum()[1:][df_cases[df_cases['Country'] == i].sum()[1:].gt(threshold)],
            #                         mode='lines+markers',
            #                         opacity=0.7,
            #                         marker={
            #                             'size': 5,
            #                             'line': {'width': 1}
            #                         },
            #                         name=i
            #                     ) for i in countries_mask
            #                 ],
            #                 'layout': dict(
            #                     xaxis={'range':[0,45],'type': 'lin', 'title':'''Number of days since >100 cases'''},
            #                     yaxis={'range':[2,None], 'type': 'log', 'title': 'Total Confirmed Cases'},
            #                     legend={'x': 1, 'y': 1},
            #                     hovermode='closest',
            #                     title="Countries with widespread public mask usage"
            #                 )
            #             }
            #         )
            #         ], className="six columns")
            #     ], className="row")
            ])
        ])
    elif tab == 'tab-6':
        return html.Div([
            #dcc.Markdown('''Visualization of available data on maps (World, Europe, Germany, ...) to display regional clusters and the spread of the pandemic.'''),
            html.Div([
                dcc.Graph(id='map-world', figure=fig_world),
            ], className='row'),
            html.Div([
                dcc.Graph(id='map-europe', figure=fig_europe),
            ], className='row'),
            html.Div([
                dcc.Graph(id='map-asia', figure=fig_asia),
            ], className='row'),
            #generate_table(df_cases["Lat", "Long"], axis=1)),
            #generate_table(df_deaths.drop(["Lat", "Long"], axis=1))
        ])

### Run App
if __name__ == '__main__':
    app.run_server(debug=True)
