import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_extendable_graph as deg
from dash.dependencies import Input, Output, State

import plotly
import plotly.figure_factory as ff

import dash_extendable_graph as deg

## Data handling
import numpy as np
import pandas as pd
import datetime as dt

## Miscl. imports
import csv
import os, sys, signal, subprocess
from pathlib import Path
import itertools    
from file_read_backwards import FileReadBackwards

## For creating the download link
import urllib
import flask

## Custom functions
from twitter_functions import id_extractor, old_tweets
from sentiment_analysis_functions import tweet_cleaning, tweet_sentiment
from table_and_graph_functions import read_csv_backwards, generate_trace_per_author


###### Setup ######

## Pointing subprocess to active directory
os.chdir(sys.path[0])

app = dash.Dash(dev_tools_hot_reload=True)
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

fonts = '12px Verdana, Geneva, sans-serif'

## Name of csv file that stream creates
csv_name = 'stream.csv'
my_csv = Path(csv_name)


###### Main code ######

app.layout = html.Div(children=[

    html.H2('Twitter App', style={'font-size':'26px'}),
    
    html.Div(children=[
                       html.Label('Twitter id(s)',
                                  style={'grid-row':'1 / 2', 'grid-column':'1 / 2'}),
                       dcc.Input('ScreenName_Input', type='text',
                                  style={'grid-row':'2 / 3', 'grid-column':'1 / 2'}),
    
                       html.Label('# of tweets',
                                  style={'grid-row':'1 / 2', 'grid-column':'2 / 3'}),
                       dcc.Input(id='Num_of_Tweets_Input', value=10, type='number',
                                  style={'grid-row':'2 / 3', 'grid-column':'2 / 3'}),
        
                       html.Label('Time (min)',
                                  style={'grid-row':'1 / 2', 'grid-column':'3 / 4'}),
                       dcc.Input(id='Length_of_stream_Input', value=10, type='number',
                                  style={'grid-row':'2 / 3', 'grid-column':'3 / 4'}),
        
                       html.Button(id='Submit_Button', children='Submit',
                                   style={'grid-row':'2 / 3', 'grid-column':'4 / 5'}),
        
        
                       html.Button(id='Pause_Stream', children='Pause stream',
                                   style={'grid-row':'2 / 3', 'grid-column':'5 / 6'}),
        
                       html.A(html.Button(children='Save to CSV', id='table_download_button',
                                          style={'grid-row':'2 / 3', 'grid-column':'6 / 7'}),
                              id='table_download_link',
                              download="raw_tweet_data.csv",
                              href="",
                              target="_blank"),

    ],
              style={'display':'grid', 'grid-template-rows':'25px 25px 25px 25px', 
                     'grid-auto-columns': '100px 100px 100px 100px 140px 140px '} # 100px 150px
            ),
    
    
    html.Div(children=[
        
             dash_table.DataTable(id='tweet_table', columns=[
                                                {'name': 'Date', 'id': 'Date'},
                                                {'name': 'Author', 'id': 'Author'},
                                                {'name': 'Len', 'id': 'Len'},
                                                {'name': 'Favs', 'id': 'Favs'},
                                                {'name': "Retw", 'id': 'Retw'},
                                                {'name': 'Text', 'id': 'Text'}],
                                  
                                   ## Column titles always visible
                                   n_fixed_rows = 1,

                                   style_cell = {'whiteSpace':'normal'},
                                  
                                   ## Left-aligning test, setting fonts, and setting some column widths
                                   style_cell_conditional=[{'textAlign':'left',
                                                            'font': fonts}],

                                  
                                   ## Bolding of column titles
                                   style_header={'fontWeight':'bold'},
                                  
                                   ## Following only works without n_fixed_columns
                                   ## Horizontal and vertical scrolling
                                   style_table={'maxHeight': '600',
                                                'overflowY': 'scroll',
                                                'minWidth':'50',
                                                'maxWidth':'300'},
                                                                 
                                 ),
        



            html.Div(children=[
            
                html.Div(children=[
                    
                    html.H4(children = 'Analysis',
                        style = {'font-size': '24px'}),
                
                    dcc.Checklist(id = 'kde_checklist',
                                  options =[{'label': "KDE's", 'value': 1}],
                                  values = [1],
                                  style = {'margin-top':'-20px'}),
                    
                    dcc.Dropdown(id = 'dropdown',
                                 options = [{'label': 'Technique 1', 'value': 1},
                                            {'label': 'Technique 2', 'value': 2},
                                            {'label': 'Technique 3', 'value': 3}],
                                 value = 1,
                                 style={'margin-top': '13px', 'width': '200px'})
                    
                ],
                         style={'margin-top':'-137px'}),
                

                  dcc.Loading(id='graph_loading_symbol', type='circle', children=[
                      deg.ExtendableGraph(id='Sentiment_Graph', 
                                          figure={'layout': {'title': '% of tweets positive or negative',
                                                             'barmode':'overlay'},
                                                  'data': []
                                      }
                              )
                  ])

                
                
                
                
                
                
            ])
    ],

              style={'display':'grid', 'grid-template-columns': '50% 50%', 'column-gap':'20px',
                     'margin-top':'-25px'}),
    
    
    ## Saving most recent tweet from stream, as well as
    ## name of most recent csv created in quick cache
    dcc.Store(id='Table_Exists_Or_Not_Check'),
    dcc.Store(id='Newest_Tweets'),
    dcc.Store(id='Last_Following_Info'),
    dcc.Store(id='Tweet_Author_Indices'),
    dcc.Store(id='Stream_Process_Id'),
    dcc.Store(id='Stream_Killed_or_Not'),
    dcc.Store(id='Graph_trace_indices'),
    dcc.Interval(id='Table_Update_Component', interval=3*1000, n_intervals=0,
                 max_intervals=0), ## Interval component is disabled as default, until it is enabled
    
])
                      

###### Callbacks ######


## Opens/closes streaming
@app.callback(
    [Output(component_id='Stream_Process_Id', component_property='data'),
     Output(component_id='Stream_Killed_or_Not', component_property='data'),
     Output(component_id='Submit_Button', component_property='disabled'),
     Output(component_id='Pause_Stream', component_property='disabled'),
     Output(component_id='ScreenName_input', component_property='disabled')],
    [Input(component_id='Submit_Button', component_property='n_clicks_timestamp'),
     Input(component_id='Pause_Stream', component_property='n_clicks_timestamp')],
    [State(component_id='ScreenName_Input', component_property='value'),
     State(component_id='Length_of_stream_Input', component_property='value'),
     ## Circular hack below
     State(component_id='Stream_Process_Id', component_property='data'),
     State(component_id='Stream_Killed_or_Not', component_property='data')]
)
def open_close_stream(Submit_Button, Pause_Stream, ScreenName_Input, Length_of_stream_Input, Stream_Process_Id, Stream_Killed_or_Not):
    
    ## Additional check to make sure nothing starts until Submit is hit, 
    ## and then starting stream in its own process
    if Submit_Button and ScreenName_Input: 
        
        if Pause_Stream is None:
            Pause_Stream = 0
                       
        if Submit_Button > Pause_Stream:

            print('Stream starts...')

            stream = subprocess.Popen(['python3', 'twitter_stream.py'] + [str(ScreenName_Input), str(Length_of_stream_Input)])

            return stream.pid, 0, True, False, True

        elif Pause_Stream > Submit_Button:
        
            print('Killing stream...')

            os.kill(Stream_Process_Id, signal.SIGTERM)
            
            return 0, 1, False, True, True
            
        
    else:
    ## Returning nothing
        return 0, 0, False, True, False

    
    
## Main callback creating table - either Submit or Table_Update triggers it
@app.callback(
    [Output(component_id='tweet_table', component_property='data'),
     Output(component_id='Last_Following_Info', component_property='data'),
     Output(component_id='Newest_Tweets', component_property='data')],
    [Input(component_id='Table_Update_Component', component_property='n_intervals'),
     Input(component_id='Submit_Button', component_property='n_clicks_timestamp')],
    [State(component_id='Table_Update_Component', component_property='max_intervals'),
     State(component_id='ScreenName_Input', component_property='value'),
     State(component_id='Num_of_Tweets_Input', component_property='value'),
     State(component_id='Table_Exists_Or_Not_Check', component_property='data'),#]#, , table_rows, table_columns
     State(component_id='Stream_Killed_or_Not', component_property='data'),
     # Hack below to allow circular code
     State(component_id='tweet_table', component_property='data'),
     State(component_id='tweet_table', component_property='columns'),
     State(component_id='Last_Following_Info', component_property='data')]
)
def tweet_table(Table_Update_Component, Submit_Button, max_intervals, ScreenName_Input, number_tweets, Table_Exists_Or_Not_Check, Stream_Killed_or_Not, rows, columns, Last_Following_Info): # ScreenName_Input, number_tweets, Table_Exists_Or_Not_Check, rows, columns, Latest_Tweet_Info

    print('tweet_table ran at least')
    print('\n\nRESTART CHECK, \nTAable_Exists: {}\nStream_Killed: {}\nmax_inervals: {}\n'.format(Table_Exists_Or_Not_Check, Stream_Killed_or_Not, max_intervals))

    ## Create table with old tweets first if table has not been created yet, 
    ## or recreate table if new tweet sources have been picked
    if (Table_Exists_Or_Not_Check == 0 and ScreenName_Input) or (Table_Exists_Or_Not_Check == 1 and Stream_Killed_or_Not == 1 and max_intervals == 0):
        
        tweets = old_tweets(ScreenName_Input, number_tweets)

        return tweets.to_dict(orient='rows'), ScreenName_Input, 1

    
    ## Otherwise, update table with stream's output in csv file
    elif Table_Exists_Or_Not_Check == 1:
            
            ## Check if csv exists        
            if not my_csv.is_file():
                                
                return rows, dash.no_update, 2
  

            if my_csv.is_file():
                
                f = open(csv_name, newline='')
                lines = sum(1 for line in f)
                f.close()
                
                ## If only header exists, csv is empty and should be ignored
                if lines <2:
                                        
                    return rows, dash.no_update, 2
                

                ## Function to concurrently read 1) csv from bottom and 2) live table from top, 
                ## and perform what updates need to be done.
                rows, newest_tweets = read_csv_backwards(csv_name, rows, lines)
                                
                print('\n\nNEWEST_TWEETS: \n{}\n'.format(newest_tweets))    
                
                ## After first new tweet comes in (after table has already loaded first time), 
                ## read_csv_backwards will always run, so check is necessary to see if it
                ## picked up any new tweets.
                if not newest_tweets:
                    return rows, dash.no_update, 2
                elif newest_tweets:
                    return rows, dash.no_update, newest_tweets

    
    else:
        print('Something went wrong with tweet_table.')
        return [], dash.no_update, 2
    

## Callback for verifying table's existence    
@app.callback(
    Output(component_id='Table_Exists_Or_Not_Check', component_property='data'),
   [Input(component_id='tweet_table', component_property='data')]
)
def table_data_check(tweet_data_exists_or_not):
    
    if tweet_data_exists_or_not:
        return 1
    else:
        return 0    

    
    
## Callback controlling whether interval update, dcc.Interval(id='Table_Update_Component'), is active
@app.callback(
    Output(component_id='Table_Update_Component', component_property='max_intervals'),
   [Input(component_id='Table_Exists_Or_Not_Check', component_property='data'),
    Input(component_id='ScreenName_Input', component_property='value'),
    Input(component_id='Stream_Killed_or_Not', component_property='data')],
   [State(component_id='Last_Following_Info', component_property='data')]
)
def enable_disable_interval(Table_Exists_Or_Not_Check, ScreenName_Input, Stream_Killed_or_Not, Last_Following_Info):
    if Table_Exists_Or_Not_Check:
        
        if (Table_Exists_Or_Not_Check == 1) and (Stream_Killed_or_Not != 1):
            return -1
        
        elif (Table_Exists_Or_Not_Check == 0) or (Stream_Killed_or_Not == 1):
            return 0
    
    

## Control over graph, runs on same interval component as main tweet_table callback
@app.callback(
   [Output(component_id='Sentiment_Graph', component_property='extendData'),
    Output(component_id='Sentiment_Graph', component_property='figure'),
    Output(component_id='Graph_trace_indices', component_property='data')],
   [Input(component_id='Newest_Tweets', component_property='data')],
   [State(component_id='tweet_table', component_property='data'),
    State(component_id='kde_checklist', component_property='value'),
    ## Semi-circular hack below
    State(component_id='Graph_trace_indices', component_property='data')],
)
def sentiment_grapher(Newest_Tweets, tweet_table, kde_checklist, Graph_trace_indices):
    
    ## New stream has just started, and new graph needs to be made
    if Newest_Tweets == 1:
        
        tweets_sentiment = tweet_sentiment(tweet_table)        

        ## Tweets' sentiments grouped by Author and then fed in to make traces;
        ## creating traces that Dash/plotly can make graphs out of
        traces, trace_indices = generate_trace_per_author(tweets_sentiment, [], 1)

        return dash.no_update, traces, trace_indices
        
    ## Table exists, and no new tweets, so no update
    elif Newest_Tweets == 2:

        print('\n\ndash.no_update should be working\n\n')
        
        return dash.no_update, dash.no_update, dash.no_update

    ## New tweet data has come in
    elif (Newest_Tweets != 1) or (Newest_Tweets != 2):

        newest_tweets_sentiment = tweet_sentiment(Newest_Tweets) 
        traces = generate_trace_per_author(newest_tweets_sentiment, Graph_trace_indices, 2)


        return traces, dash.no_update, dash.no_update

        
    else:
        return {"data": []}, {"data": []}, dash.no_update


        
## For downloading table data 
@app.callback(
    Output('table_download_link', 'href'),
    [Input('table_download_button', 'n_clicks_timestamp')],
    [State('tweet_table', 'data')]
)
def update_download_link(table_download_button, data):
    
    if table_download_button:

        dff = pd.DataFrame(data)

        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

        return csv_string
    
    
    
    

if __name__ == '__main__':
    app.run_server(debug=True)
