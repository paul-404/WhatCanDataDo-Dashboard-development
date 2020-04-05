import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
import requests

from dash.dependencies import Input, Output


### Launch app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True # suppress callback errors
server = app.server
app.title="Dashboard"

### Import Data from JHU CSSE & rename columns to single word names
df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
df = df.rename(columns={"Country/Region": "Country", "Province/State": "Province"})

df1 = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
df1 = df1.rename(columns={"Country/Region": "Country", "Province/State": "Province"})

### Call APIs for live counts
live_all = requests.get("https://corona.lmao.ninja/all").json()

### Create Time Series and Country Selection Lists
time = df.columns[4:]
#countries_all = df["Country"].unique() # all Countries
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
dropdown_options = [{"label" : i, "value" : i} for i in df["Country"].unique()]

### App Layout
app.layout = html.Div([
    html.Div([
        html.H1("COVID-19 Live Analytics"),
        dcc.Markdown("The main purpose of this dashboard is to provide a simple, interactive tool to visualize publicly available data about the COVID-19 pandemic. All graphs rely on data collected by the awesome team at [John Hopkins University CSSE](https://github.com/CSSEGISandData/COVID-19). Live counts above the graphs are relying on [NovelCovid APIs](https://github.com/NOVELCOVID/API) since they are updated more frequently.")
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
                label='Projections',
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
# Callback Cards
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


@app.callback(Output('graph-confirmed', 'figure'),
             [Input('my-dropdown', 'value')])
def update_figure(X):
    fig = {
                                'data': [
                                    dict(
                                        x=df.columns[4:],
                                        y=df[df['Country'] == i].sum()[4:],
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
                                    margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
                                    legend={'x': 1, 'y': 1},
                                    hovermode='closest',
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
                                        x=df1.columns[4:],
                                        y=df1[df1['Country'] == i].sum()[4:],
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
                                    yaxis={'type': 'lin', 'title': 'Total Confirmed Cases'},
                                    margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
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
                                    x=df.columns[4:],
                                    y=df[df['Country'] == i].sum()[4:].diff(),
                                    type='bar',
                                    opacity=0.7,
                                    name=i
                                ) for i in [str(X)]
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'title': 'Daily New Cases'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
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
                                        x=df.columns[4:],
                                        y=df.sum()[4:],
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
                                    margin={'l': 50, 'b': 100, 't': 0, 'r': 0},
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
                                    x=df.columns[4:],
                                    y=df.sum()[4:].diff(),
                                    type='bar',
                                    opacity=0.7,
                                    name="World"
                                )
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'title': 'Daily New Cases'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
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
                                    x=df1.columns[4:],
                                    y=df1.sum()[4:],
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
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
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
                                    x=df.columns[4:],
                                    y=df[df['Country'] == i].sum()[4:],
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
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
                                legend={'x': 1, 'y': 1},
                                hovermode='closest',
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
                                    x=df.columns[4:],
                                    y=df[df['Country'] == i].sum()[4:].diff(),
                                    type='bar',
                                    opacity=0.7,
                                    name=i
                                ) for i in ["Germany"]
                            ],
                            'layout': dict(
                                xaxis={},
                                yaxis={'title': 'Daily New Cases'},
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
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
                                    x=df1.columns[4:],
                                    y=df1[df1['Country'] == i].sum()[4:],
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
                                margin={'l': 50, 'b': 100, 't': 50, 'r': 0},
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
                                        y=df[df['Country'] == i].sum()[4:][df[df['Country'] == i].sum()[4:].gt(threshold)],
                                        mode='lines',
                                        opacity=0.7,
                                        marker={
                                            'size': 5,
                                            'line': {'width': 1},
                                        },
                                        name=i
                                    ) for i in df["Country"].unique()
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
                                        y=df[df['Country'] == i].sum()[4:][df[df['Country'] == i].sum()[4:].gt(threshold)],
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
                                        y=df[df['Country'] == i].sum()[4:][df[df['Country'] == i].sum()[4:].gt(threshold)],
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
            html.P('''Forecast/Projections by ML supported SEIR Model. Fit to currently available data (confirmed cases, active cases, measures, hospital capacity, ICU beds, ...). Goal: Visualize predictions and effects of different measures in a way that can be understood by everybody.''')
            #generate_table(df1f["Lat", "Long"], axis=1))
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
            #                         y=df[df['Country'] == i].sum()[4:][df[df['Country'] == i].sum()[4:].gt(threshold)],
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
            #                         y=df[df['Country'] == i].sum()[4:][df[df['Country'] == i].sum()[4:].gt(threshold)],
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
            dcc.Markdown('''Visualization of available data on maps (World, Europe, Germany, ...) to display local clusters and regional spread of the pandemic.'''),
            #generate_table(df["Lat", "Long"], axis=1)),
            #generate_table(df1.drop(["Lat", "Long"], axis=1))
        ])

### Run App
if __name__ == '__main__':
    app.run_server(debug=True)
