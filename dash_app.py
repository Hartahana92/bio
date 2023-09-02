# -*- coding: utf-8 -*-

'''
Created on 24 09. 2022

@author: Alex
'''
import base64
from dash import Dash

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State

import io

# import numpy as np
import pandas as pd

from dash_table.Format import Format, Scheme


import bio_df_processing as helper


app = Dash(__name__, 
           meta_tags=[{"name": "viewport", "content": "width=device-width"}])


# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color
bar_bgcolor = "#b0bec5"  # material blue-gray 200
bar_unselected_color = "#78909c"  # material blue-gray 400
bar_color = "#546e7a"  # material blue-gray 600
bar_selected_color = "#37474f"  # material blue-gray 800
bar_unselected_opacity = 0.8

# Figure template
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}   


def patient_info(df):
    return html.Div(children=[
        html.H5('Информация о пациенте'),
        dash_table.DataTable(
            columns=[{"name": str(i), "id": str(i)} for i in df.columns],
            data = df.to_dict('records'),
            style_header={
                'fontWeight': 'bold',
                },
            style_cell = {'font-family':'sans-serif', 'fontSize':12, },
            id = 'patient_info_table'
        )
    ])
    

def metabolit_info(df_in, name = 'Метаболиты'):
    """
    conditional formatting link
    https://dash.plotly.com/datatable/conditional-formatting
    """
    df = df_in.copy()
    df = df.dropna(subset=['Верхняя граница'])
    df['Метаболит'] = df.index.values
    cols = df.columns.to_list()
    df = df[[cols[-1]] + cols[:-1]]
    
    return html.Div(children=[
        html.H3(name,
                style={'text-align':'center'}),
        dash_table.DataTable(
            id = 'metabolit-table',
            columns=[{"name": str(i), "id": str(i), 
                      'type' :'numeric',
                      "format" : Format(precision=2, scheme=Scheme.fixed)} for i in df.columns],
            data = df.to_dict('records'),
            style_header={
                'fontWeight': 'bold',
                'textAlign': 'center'},
            style_cell={
                'textAlign': 'center',
                'fontSize':12, 
                'font-family':'sans-serif'
            },
            style_data_conditional=[                
                {
                    'if': {
                        'filter_query': '{Понижено} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'aqua',
                    'color': 'black'
                },
                {
                    'if': {
                        'filter_query': '{Риск понижения} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'aliceblue',
                    'color': 'black'
                },
                                {
                    'if': {
                        'filter_query': '{Риск повышения} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'lightyellow',
                    'color': 'black'
                },  
                {
                    'if': {
                        'filter_query': '{Повышено} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'red',
                    'color': 'white'
                },                                                      
                
                ],
            style_table={
                'maxHeight': '600px',
                'minWidth': '98%', 'width': '98%', 'maxWidth': '98%',
                'overflowY' : 'auto'
                },
            fixed_columns={'headers': True, 'data': 1},
        ),
    ],
    className = "six columns pretty_container")
     
    
    
def get_graph_color(value, b = 50):
    """
    value - in range 0-100
    """    
    r = int(255*value/100.)
    g = 255 - r
    return f'rgb({r},{g},{b})'

def models_output(deseases): 
    """ 
    deseases - dict: {'desease name' : desease probability} 
    """ 
    categories = list(deseases.keys())[::-1] 
    proba = list(deseases.values())[::-1] 
     
    colors = [] 
    labels = [] 
    for cat in categories: 
        colors.append(get_graph_color(deseases[cat])) 
        labels.append(f'<b>{deseases[cat]:.2f} %</b>') 
         
    fig = { 
        "data": [ 
            { 
                "type": "bar", 
                "x": proba, 
                "y": categories, 
                "marker": { 
                    "color": colors, 
                    }, 
                "text" : labels, 
                "textposition" : 'inside', 
                "insidetextanchor" : 'middle', 
                "hoverinfo": 'skip', 
             
                "orientation": "h", 
                "showlegend": False, 
            }, 
        ], 
        "layout": { 
            "template": template, 
            "barmode": "overlay", 
            "selectdirection": "v", 
            "height": 120, 
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10}, 
            "width" : "90%", 
            "xaxis": { 
                "range": [-1, 100], 
                "automargin": True, 
            }, 
            "yaxis": { 
                "type": "category", 
                "categoryorder": "array", 
                "categoryarray": categories, 
                "side": "left", 
                "automargin": True, 
            }, 
        }, 
    }     
     
    return html.Div(children = [ 
        html.H3('Сердечно-сосудистые патологии', 
                style={'text-align':'center'}), 
        html.Label('Классификационная модель построена на основе алгоритма машинного обучения "Случайный Лес"'), 
        html.Br(), 
        html.Label('Метрика качества AUCROC первой модели (ССЗ vs Контроль) - 89%\n'), 
        html.Br(), 
        html.Label('Метрика качества AUCROC второй модели (ГБ vs ИБС) - 86%\n'), 
        dcc.Graph( 
            id='example-graph', 
            figure=fig, 
            config={ 
                'displayModeBar': False 
                } 
        ) 
         
        ], 
        className="six columns pretty_container",)    
   



#LC part introduction
def models_output_lc(deseases):
    """
    deseases - dict: {'desease name' : desease probability}
    """
    categories = list(deseases.keys())[::-1]
    proba = list(deseases.values())[::-1]
    
    colors = []
    labels = []
    for cat in categories:
        colors.append(get_graph_color(deseases[cat]))
        labels.append(f'<b>{deseases[cat]:.2f} %</b>')
        
    fig = {
        "data": [
            {
                "type": "bar",
                "x": proba,
                "y": categories,
                "marker": {
                    "color": colors,
                    },
                "text" : labels,
                "textposition" : 'inside',
                "insidetextanchor" : 'middle',
                "hoverinfo": 'skip',
            
                "orientation": "h",
                "showlegend": False,
            },
        ],
        "layout": {
            "template": template,
            "barmode": "overlay",
            "selectdirection": "v",
            "height": 60,
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
            "width" : "90%",
            "xaxis": {
                "range": [-1, 100],
                "automargin": True,
            },
            "yaxis": {
                "type": "category",
                "categoryorder": "array",
                "categoryarray": categories,
                "side": "left",
                "automargin": True,
            },
        },
    }    
    
    return html.Div(children = [
        html.H3('Рак легкого',
                style={'text-align':'center'}),
        html.Label('Классификационная модель построена на основе алгоритма машинного обучения "Случайный Лес"'),
        html.Br(),
        html.Label('Метрика качества AUCROC - 92%\n'),
        dcc.Graph(
            id='example-graph',
            figure=fig,
            config={
                'displayModeBar': False
                }
        )
        
        ],
        className="six columns pretty_container",)





#LC part introduction
def models_output_lc(deseases):
    """
    deseases - dict: {'desease name' : desease probability}
    """
    categories = list(deseases.keys())[::-1]
    proba = list(deseases.values())[::-1]
    
    colors = []
    labels = []
    for cat in categories:
        colors.append(get_graph_color(deseases[cat]))
        labels.append(f'<b>{deseases[cat]:.2f} %</b>')
        
    fig = {
        "data": [
            {
                "type": "bar",
                "x": proba,
                "y": categories,
                "marker": {
                    "color": colors,
                    },
                "text" : labels,
                "textposition" : 'inside',
                "insidetextanchor" : 'middle',
                "hoverinfo": 'skip',
            
                "orientation": "h",
                "showlegend": False,
            },
        ],
        "layout": {
            "template": template,
            "barmode": "overlay",
            "selectdirection": "v",
            "height": 60,
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
            "width" : "90%",
            "xaxis": {
                "range": [-1, 100],
                "automargin": True,
            },
            "yaxis": {
                "type": "category",
                "categoryorder": "array",
                "categoryarray": categories,
                "side": "left",
                "automargin": True,
            },
        },
    }    
    
    return html.Div(children = [
        html.H3('Рак легкого',
                style={'text-align':'center'}),
        html.Label('Классификационная модель построена на основе алгоритма машинного обучения "Случайный Лес"'),
        html.Br(),
        html.Label('Метрика качества AUCROC - 92%\n'),
        dcc.Graph(
            id='example-graph',
            figure=fig,
            config={
                'displayModeBar': False
                }
        )
        
        ],
        className="six columns pretty_container",)










app.layout = html.Div(children=[
    html.H1(children='Скрининговая система диагностики патологий',
            style = {'textAlign': 'center'
                }),

    html.Div(children=['''
        Загрузите файл с результатами метаболомного профиля
    ''',
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'background':  'whitesmoke'
            },
            # Allow multiple files to be uploaded
            multiple=True
        )],
        # className = 'inputPart'
        className = "six columns pretty_container"
    ),
    html.Br(),
    
    html.Div(children = [],
             id = 'output-data-upload',
             # className = "six columns pretty_container"
             ),
    ],
    
    className = 'page'
    )



def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_excel(io.BytesIO(decoded))  
        # df = pd.read_excel('C:\\Users\\MATH\\bio\\TEST_test.xlsx')
            
        info, profile, groups_content = helper.prepare_data(df)
        
        desease = helper.desease_prediction(profile)
        desease_lc=helper.desease_prediction_lc(profile)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ], className="six columns pretty_container")

    
    meta_tables = []
    for name, values in groups_content.items():
        meta_tables.append(metabolit_info(profile.loc[values], name=name))

    return html.Div([
            html.Div([
                    html.H3(children='Результаты метаболомного профилирования',
                            style = {'textAlign': 'center'
                                }),        
                
                    patient_info(info),
                    ],
                className="six columns pretty_container"
                ),
            models_output(desease),
            models_output_lc(desease_lc)
            
            ] + meta_tables,
        )


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children




# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
    