import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from data_utils import get_competitive_matrix
import plotly.figure_factory as ff
import numpy as np
import dash_table
import json
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

input_data_original, used_apps, app_names = get_competitive_matrix()


def get_data_from_df(col_names_chosen):
    copy_of_data = input_data_original.copy(deep=True)
    for col_name in col_names_chosen:
        copy_of_data.loc[col_name]['None'] = sum(input_data_original.loc[col_name, ~input_data_original.columns.isin(col_names_chosen)].values)
        copy_of_data.loc['None'][col_name] = sum(input_data_original.loc[~input_data_original.columns.isin(col_names_chosen), col_name].values)

    for col_name in input_data_original.columns:
        if col_name in col_names_chosen or col_name == 'None':
            continue
        copy_of_data.loc['None']['None'] += input_data_original.loc[col_name][col_name]
    return copy_of_data

def z_to_text(z):
    result = np.zeros(z.shape)
    for i in range(len(z)):
        for j in range(len(z)):
            result[i][j] = (str(z[i][j]))
    return result


def normalize_by_row(data):
    for row in range(len(data)):
        data[row][:] /= sum(data[row][:])
        data[row][:] *= 100
        data[row][:] = np.round(data[row][:])
    return data


default_val = ['PayPal', 'Stripe', 'PaymentKit']
input_data = get_data_from_df(default_val)

fig = go.Figure(data=ff.create_annotated_heatmap(
    z=normalize_by_row(input_data.loc[default_val + ['None'], default_val + ['None']].values),
    x=default_val + ['None'],
    y=default_val + ['None'],
    colorscale='YlOrRd',
    annotation_text=z_to_text(
        input_data.loc[default_val + ['None']][default_val + ['None']].values)
                ),)
fig.update_layout(clickmode='event+select')
fig.update_xaxes(side="bottom")
app.layout = html.Div(children=[
    html.H1('Competitive Matrix'),
    html.Div([

        html.Div([
            html.H4('Select SDK'),
            dcc.Dropdown(
                id='SDK_dropdown',
                options=[{'label': i, 'value': i} for i in input_data_original.columns if i != 'None'],
                value=default_val,
                multi=True
            ),

        ],
            ),

        dcc.Graph(id='heatmap', figure=fig),

        dcc.Graph(id='table', figure=go.Figure(data=[go.Table(header=dict(values=['Used Apps']), cells=dict(values=[]))]))

    ]),

])

@app.callback(
    Output('heatmap', 'figure'),
    Input('SDK_dropdown', 'value')
)
def update_figure(value):
    if value is None:
        return {'data': []}

    else:
        input_data = get_data_from_df(value)
        fig = go.Figure(data=ff.create_annotated_heatmap(
            z=normalize_by_row(input_data.loc[value + ['None'], value+ ['None']].values),
            y=value + ['None'],
            x=value + ['None'],
            colorscale='YlOrRd'
        ),
        )
        fig.update_layout(
            title="Usage of SDK by apps",
            xaxis_title="To SDK",
            yaxis_title="From SDK",
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="RebeccaPurple"
            )
        )
        fig.update_xaxes(side="bottom")
        fig.update_layout(clickmode='event+select')
        return fig

@app.callback(
    Output('table', 'figure'),
    Input('heatmap', 'clickData')
)
def display_click_data(clickData):
    if not clickData:
        return {'data': []}
    else:
        label_x = clickData['points'][0]['x']
        label_y = clickData['points'][0]['y']
        if label_x == label_y:
            label = "Apps using: " + label_x
        else:
            label = 'Apps churned to {} from {}'.format(label_y, label_x)

        apps = used_apps.loc[label_y][label_x]
        apps = app_names[app_names['id'].isin(apps)]
        apps = apps['name']
        table = go.Figure(data=[go.Table(header=dict(values=[label]), cells=dict(values=[apps]))])
        return table




if __name__ == '__main__':
    app.run_server()

