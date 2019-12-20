# Main app for KivaExplore.

# TODO: Add additional images and wordclouds.  Wordcloud generator stored locally in code/KivaExploreProcesses
# TODO: Refactor callbacks to be more DRY.

# ===============================================PART 1 of 3: SETUP====================================================|

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import base64

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# -----------------------------------------------Data Prep-------------------------------------------------------------|

mpi_df = pd.read_csv('./data/cleaned_data/mpi.csv')
genders_df = pd.read_csv('./data/cleaned_data/genders.csv')
totals_df = pd.read_csv('./data/cleaned_data/totals.csv')
sectors_df = pd.read_csv('./data/cleaned_data/sectors.csv')
table_df = pd.DataFrame({'Country': totals_df['country'], 'ISO': totals_df['ISO'],
                         'MPI': totals_df['MPI'], 'GII': totals_df['GII']})

# ===============================================PART 2 of 3: APP LAYOUT===============================================|


app.layout = \
    dbc.Container(
        fluid=True,
        children=[

# -----------------------------------------------Jumbotron-------------------------------------------------------------|

            dbc.Jumbotron([
                html.H1(
                    id="Title",
                    className="display-3",
                    style={"text-align": "center"},
                    children=["KivaExplore"],
                ), html.H3("Browse By Gender and Poverty", style={"text-align": "center"})],
            ),

# -----------------------------------------------Dropdown Selector-----------------------------------------------------|

            html.Div(
                children=[
                    dcc.Dropdown(
                        id="Metrics",
                        options=[
                            {'label': 'Multidimensional Poverty Index (MPI)', 'value': 'MPI'},
                            {'label': 'Gender Inequality Index (GII)', 'value': 'GII'},
                        ],
                        value='MPI',
                        style={"padding-left": "400px", "padding-right": "400px"}
                    ),
                ]
            ),

# -----------------------------------------------Choropleth Map--------------------------------------------------------|

            html.Div(
                children=[
                    dbc.Row([
                        dbc.Col(
                            dcc.Graph(
                                style={'height': '90vh', 'width': '90vh'},
                                id='Choropleth',
                                clickData={'points': [{'location': 'ALB'}]},
                            ), width={"size": 6, "offset": 1}
                        ),
                    ]
                    )
                ]
            ),

# -----------------------------------------------Scatterplot & ListView------------------------------------------------|

            html.Div(
                children=[
                    dbc.Row([

# -----------------------------------------------Scatterplot-----------------------------------------------------------|

                        dbc.Col(
                            dcc.Graph(id="Scatter")),

# -----------------------------------------------ListView--------------------------------------------------------------|

                        dbc.Col(
                            dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i} for i in table_df.columns],
                                fixed_rows={'headers': True, 'data': 0},
                                style_table={
                                    'maxHeight': '280px',
                                    'overflowY': 'scroll'
                                },
                                style_cell={'textAlign': 'center'},
                                data=table_df.to_dict('records')
                            ), width=6, style={'padding-top': '100px'},

                        )
                    ]
                    ),

                ]
            ),

# -----------------------------------------------Jumbotron 2-----------------------------------------------------------|

            html.Div(
                children=[
                    dbc.Jumbotron([
                        html.H4("Explore", style={"text-align": "center"}),
                        html.H1(id='SubplotHeader', style={"text-align": "center"}, className='display-3'),
                        html.H4(html.A(id="URL", target="_blank"), style={"text-align": "center"}),
                    ])
                ]
            ),

# -----------------------------------------------Image & Wordcloud-----------------------------------------------------|

            html.Div(
                children=[
                    dbc.Row([

# -----------------------------------------------Image-----------------------------------------------------------------|

                        dbc.Col(
                            html.Div(
                                html.Img(id="Image"), style={'text-align': 'center', 'padding-left': '100px'}),
                            width=4),

# -----------------------------------------------Wordcloud-------------------------------------------------------------|

                        dbc.Col(
                            html.Div(
                                html.Img(id="Wordcloud"), style={'text-align': 'center'}), width=8)])]),

# -----------------------------------------------Gender & Sector Breakdowns--------------------------------------------|

            html.Div(
                children=[
                    dbc.Row([

# -----------------------------------------------Gender Barchart-------------------------------------------------------|

                        dbc.Col(
                            dcc.Graph(
                                id='GenderBreakdown',
                                className='six columns'), width=6
                        ),

# -----------------------------------------------Sector Barchart-------------------------------------------------------|

                        dbc.Col(
                            dcc.Graph(
                                id='SectorBreakdown',
                                className='six columns'), width=6
                        )]
                    )
                ]
            ),

        ]
    )

# ===============================================PART 3 of 3: CALLBACKS================================================|


# -----------------------------------------------Choropleth Callback---------------------------------------------------|


@app.callback(
    dash.dependencies.Output('Choropleth', 'figure'),
    [dash.dependencies.Input('Metrics', 'value')])
def update_choropleth(selector):
    """
    Updates the choropleth map in the "Browse" section based on user's metric choice.

    :param clickData: Selected metric (ie. MPI or GII).
    :return: A choropleth map.
    """
    if selector == "MPI":
        return {
            'data': [
                go.Choropleth(
                    locations=totals_df['ISO'],
                    z=totals_df['MPI'].astype(float),
                    colorscale='Reds',
                    colorbar={"thickness": 10, "len": 0.65, "x": 0.95, "y": 0.5},
                    text=totals_df['country']
                )],
            'layout': {
                'height': 800,
                'width': 1300,
                'title': 'MPI by Country'
            }
        }
    else:
        return {
            'data': [
                go.Choropleth(
                    locations=totals_df['ISO'],
                    z=totals_df['GII'].astype(float),
                    colorscale='Blues',
                    colorbar={"thickness": 10, "len": 0.65, "x": 0.85, "y": 0.5},
                    text=totals_df['country']
                )],
            'layout': {
                'height': 800,
                'width': 1300,
                'title': 'GII by Country'
            }
        }


# -----------------------------------------------Scatterplot Callback--------------------------------------------------|


@app.callback(
    dash.dependencies.Output('Scatter', 'figure'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def update_scatter(clickData):
    """
    Updates the scatterplot in the "Browse" section based on choropleth selection.
    Namely, it highlights the selected country in the scatterplot.

    :param clickData: Selected country from choropleth map.
    :return: An scatterplot.
    """
    ISO = clickData['points'][0]['location']
    dff = totals_df[totals_df['ISO'] == ISO]
    return {
        'data': [
            go.Scatter(
                x=totals_df['GII'],
                y=totals_df['MPI'],
                text=totals_df['country'],
                mode='markers',
                opacity=0.7,
                marker={
                    'color': '#999999',
                    'size': 10,
                    'line': {'width': 0.2, 'color': 'white'}
                }
            ),
            go.Scatter(
                x=dff['GII'],
                y=dff['MPI'],
                text=dff['country'],
                mode='markers',
                opacity=0.7,
                marker={
                    'color': '#3D9970',
                    'size': 10,
                    'line': {'width': 2, 'color': 'Black'}
                }
            )
        ],

        'layout': dict(
            title=f"Gender Inequality Index vs. Multidimensional Poverty Index for {dff.iloc[0]['country']}",
            xaxis={'title': 'Gender Inequality Index'},
            yaxis={'title': 'Multidimensional Poverty Index'},
            hovermode='closest',
            showlegend=False,
        )
    }


# -----------------------------------------------ListView Callback-----------------------------------------------------|


@app.callback(
    dash.dependencies.Output('table', 'style_data_conditional'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def highlight_table(clickData):
    """
    Updates the ListView in the "Browse" section based on choropleth selection.
    Namely, it highlights the selected country in the ListView.

    :param clickData: Selected country from choropleth map.
    :return: An ListView style attribute.
    """
    ISO = clickData['points'][0]['location']
    dff = totals_df[totals_df['ISO'] == ISO]
    index = dff.index.to_list()[0]
    return [{
        "if": {f"row_index": index},
        "backgroundColor": "#3D9970",
        'color': 'white'
    }
    ]


# -----------------------------------------------Jumbotron 2 Callbacks-------------------------------------------------|


@app.callback(
    dash.dependencies.Output('SubplotHeader', 'children'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def generate_subplot_header(clickData):
    """
    Updates the JumboTron 2 header the "Explore" section based on the user's choropleth selection.
    For example, if Mali is selected, the JumboTron will read "Explore Mali".

    :param clickData: Selected country from choropleth map.
    :return: A jumbotron header.
    """
    ISO = clickData['points'][0]['location']
    if ISO:
        dff = sectors_df.reset_index()
        dff = dff[dff['ISO'] == ISO]
        country = dff.iloc[0]['country']
        return f"{country}"


@app.callback(
    dash.dependencies.Output('URL', 'children'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def update_url_anchor(clickData):
    """
    Updates the Kiva URL anchor in the "Explore" section based on the user's choropleth selection.
    For example, if Mali is selected, the link will be displayed as "Find your perfect borrower in Mali now."

    :param clickData: Selected country from choropleth map.
    :return: An updated link.
    """
    ISO = clickData['points'][0]['location']
    if ISO:
        dff = sectors_df.reset_index()
        dff = dff[dff['ISO'] == ISO]
        country = dff.iloc[0]['country']
        return f"Find your perfect borrower in {country} now."


@app.callback(
    dash.dependencies.Output('URL', 'href'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def update_url(clickData):
    """
    Updates the Kiva URL in the "Explore" section based on the user's choropleth selection.
    For example, if Mali is selected, the link will direct the user to the Kiva page for Mali.

    :param clickData: Selected country from choropleth map.
    :return: An updated link destination.
    """
    ISO = clickData['points'][0]['location']
    country = ISO[:2]
    return f"https://www.kiva.org/lend?country={country}"


# -----------------------------------------------Image Callback--------------------------------------------------------|


@app.callback(
    dash.dependencies.Output('Image', 'src'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def update_image(clickData):
    """
    Updates the image the "Explore" section based on the user's choropleth selection.

    :param clickData: Selected country from choropleth map.
    :return: An image placed in the src attribute of id Image.
    """
    ISO = clickData['points'][0]['location']
    image_filename = f'images/{ISO}.jpg'
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    if ISO:
        return 'data:image/png;base64,{}'.format(encoded_image.decode())


# -----------------------------------------------Wordcloud Callback----------------------------------------------------|


@app.callback(
    dash.dependencies.Output('Wordcloud', 'src'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def update_wordcloud(clickData):
    """
    Updates the wordcloud the "Explore" section based on the user's choropleth selection.

    :param clickData: Selected country from choropleth map.
    :return: An wordcloud placed in the src attribute of id Wordcloud.
    """
    ISO = clickData['points'][0]['location']
    image_filename = f'wordclouds/{ISO}.jpg'
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    if ISO:
        return 'data:image/png;base64,{}'.format(encoded_image.decode())


@app.callback(
    dash.dependencies.Output('GenderBreakdown', 'figure'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def generate_genderbar(clickData):
    """
    Updates the gender breakdown barchart in the "Explore" section based on the user's choropleth selection.

    :param clickData: Selected country from choropleth map.
    :return: A barchart.
    """
    ISO = clickData['points'][0]['location']
    if ISO:
        dff = genders_df[genders_df['ISO'] == ISO]
        country = dff.iloc[0]['country']
        dff.set_index('ISO', inplace=True)
        female = dff.loc[ISO]['Female']
        male = dff.loc[ISO]['Male']
        mixed = dff.loc[ISO]['Mixed']
        return {
            'data': [
                go.Bar(
                    x=["Female", "Male", "Mixed"],
                    y=[female, male, mixed]
                )],
            'layout': {
                'title': f'Gender Breakdown'
            }
        }
    else:
        return None


@app.callback(
    dash.dependencies.Output('SectorBreakdown', 'figure'),
    [dash.dependencies.Input('Choropleth', 'clickData')]
)
def generate_sectorbar(clickData):
    """
    Updates the sector breakdown barchart in the "Explore" section based on the user's choropleth selection.

    :param clickData: Selected country from choropleth map.
    :return: A barchart.
    """
    ISO = clickData['points'][0]['location']
    if ISO:
        dff = sectors_df.reset_index()
        dff = dff[dff['ISO'] == ISO]
        country = dff.iloc[0]['country']
        dff.drop('country', inplace=True, axis=1)
        series = dff.iloc[0]
        x = series.index.to_list()
        y = series.to_list()
        return {
            'data': [
                go.Bar(
                    x=x[2:],
                    y=y[2:],
                    marker={'color': 'grey'}
                )],
            'layout': {
                'title': f'Sector Breakdown'
            }
        }
    else:
        return None


if __name__ == '__main__':
    app.run_server(debug=True)
