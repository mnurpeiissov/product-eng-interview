import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import data_utils
import plotly.figure_factory as ff


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

input_data_original, used_apps, app_names = data_utils.get_competitive_matrix()

default_val = ['PayPal', 'Stripe', 'PaymentKit']
input_data = data_utils.get_updated_data_from_df(default_val, input_data_original)

fig = go.Figure(data=ff.create_annotated_heatmap(
    z=data_utils.normalize_by_row(input_data.loc[default_val + ['None'], default_val + ['None']].values),
    x=default_val + ['None'],
    y=default_val + ['None'],
    colorscale='YlOrRd',
    annotation_text=data_utils.z_to_text(
        input_data.loc[default_val + ['None']][default_val + ['None']].values)))

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
                multi=True),
                ],),
        dcc.Graph(id='heatmap', figure=fig),
        dcc.Graph(id='table')

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
        input_data = data_utils.get_updated_data_from_df(value, input_data_original)
        fig = go.Figure(data=ff.create_annotated_heatmap(
            z=data_utils.normalize_by_row(input_data.loc[value + ['None'], value+ ['None']].values),
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
        return go.Figure(data=[go.Table(header=dict(values=['Used Apps']), cells=dict(values=[]))])
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

