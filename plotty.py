# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site}
    for site in spacex_df['Launch Site'].unique()
]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                  dcc.Dropdown(id='site-dropdown',
                                                options=site_options,
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True
                                                ),
                                            
    
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                    10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `success-pie-chart` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Group by launch site and sum success (class == 1)
        success_by_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(success_by_site, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['Outcome'] = outcome_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(outcome_counts, 
                     values='count', 
                     names='Outcome',
                     title=f'Launch Outcomes for {entered_site}',
                     color_discrete_map={'Success': 'green', 'Failure': 'red'})
        return fig
        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value"))
def get_chart(entered_site,selected_values):
    if entered_site == 'ALL':
        # Group by launch site and sum success (class == 1)
        filtered_df = spacex_df[
                                (spacex_df['Payload Mass (kg)'] >= selected_values[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= selected_values[1])
                              ]

        fig = px.scatter(
                            filtered_df,
                            x='Payload Mass (kg)',               
                            y='class',
                            color='Booster Version Category',
                            title='Payload vs Outcome by Booster Version',
                            labels={'class': 'Launch Outcome (0 = Fail, 1 = Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'},
                            hover_data=['Booster Version Category', 'Launch Site']
                        )
        return fig
    else:
        filtered_df = spacex_df[ (spacex_df['Launch Site'] == entered_site) &
                                  (spacex_df['Payload Mass (kg)'] >= selected_values[0]) & 
                                  (spacex_df['Payload Mass (kg)'] <= selected_values[1])
        ]        
        fig = fig = px.scatter(
                            filtered_df,
                            x='Payload Mass (kg)',               
                            y='class',
                            color='Booster Version Category',
                            title=f'Payload vs Outcome for {entered_site}',
                            labels={'class': 'Launch Outcome (0 = Fail, 1 = Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'},
                            hover_data=['Booster Version Category', 'Launch Site']
                        )
        return fig



# Run the app
if __name__ == '__main__':
    app.run()
