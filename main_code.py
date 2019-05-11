import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_extendable_graph as deg
from dash.dependencies import Input, Output, State

import dash_extendable_graph as deg
import plotly.figure_factory as ff

import pandas as pd
import numpy as np
import datetime as dt

import csv
import os, sys, signal, subprocess
from pathlib import Path
import itertools    
from file_read_backwards import FileReadBackwards

import urllib
import flask

## Imported custom functions
from twitter_functions import id_extractor, old_tweets#, Tweet_Author_Placement
from sentiment_analysis_functions import tweet_cleaning, tweet_sentiment


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
        
#                        dcc.Checklist(id='checklist',
#                            options=[
#                                     {'label': 'Stream_on', 'value': 'Stream on'},
#                                     {'label': 'Stream_off', 'value': 'Stream off'}],
#                            values=['Stream off'],
#                            style={'grid-row':'2 / 3', 'grid-column':'5 / 6'},
#                            labelStyle={'display': 'inline-block'})
        
#                        html.Button(id='time_Stream', children='Stream time',
#                                    style={'grid-row':'2 / 3', 'grid-column':'5 / 6'}),
        
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
                                     # Tweet text scrollable if it's too big
#                                    n_fixed_columns = 5,
                                  
                                   style_cell = {'whiteSpace':'normal'},
                                  
                                   ## Left-aligning test, setting fonts, and setting some column widths
                                   style_cell_conditional=[{'textAlign':'left',
                                                            'font': fonts}],
#                                                            {'if':{'column_id':'Date'}, ## The Date stuff here screws up my rows.
#                                                             'width':'40px'}],
#                                                            {'if':{'column_id':'Len'},
#                                                             'width':'20px'},
#                                                            {'if':{'column_id':'Favs'},
#                                                             'width':'20px'},
#                                                            {'if':{'column_id':'Retw'},
#                                                             'width':'20px'}],
                                  
                                   ## Bolding of column titles
                                   style_header={'fontWeight':'bold'},
                                  
                                  ## Following only works without n_fixed_columns
                                   ## Horizontal and vertical scrolling
                                   style_table={'maxHeight': '600',
                                                'overflowY': 'scroll',
                                                'minWidth':'50',
                                                'maxWidth':'300'},
                                 
                                   ## Enabling selection of multiple tweets for use in analysis on right
#                                    row_selectable = 'multi',
                                  
#                                    editable=True                                  
                                 ),
        
        
        
        
        
        
        
#                 figure = { 'data': [ {'type':'histogram',
#                              'x': selected_tweets_sentiment,
#                              'histnorm': 'probability'} ],
#                    'layout': {'title': '% of tweets positive or negative'}
#                  }
        


            html.Div(children=[
            
                html.Div(children=[
                    
                    html.H4(children = 'Analysis',
                        style = {'font-size': '24px'}),
                
                    dcc.Checklist(id = 'checklist',
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
                
                  ## Reminder to add appending ability to graphs at some point.
#                 deg.ExtendableGraph(id='Sentiment_Graph', 
#                                     figure={'data': [{'type':'histogram',
#                                             'histnorm': 'probability'}]
#                                            }
#                                    )
            
#                             'layout': {'title': '% of tweets positive or negative',
#                              'barmode':'overlay'}
                

                
               
#                  dcc.Graph(id='Sentiment_Graph', 
#                            figure={'layout': {'title': '% of tweets positive or negative',
#                                               'barmode':'overlay'},
#                                    'data': [{'x': [], 'type':'histogram'},
#                                             {'x': [], 'type':'histogram'},
#                                             {'x': [], 'type':'histogram'}
#                                            ]
#                                   }
#                           )
                
                
                  deg.ExtendableGraph(id='Sentiment_Graph', 
                                      figure={'layout': {'title': '% of tweets positive or negative',
                                              'barmode':'overlay'},
                                              
                                              'data': []
                                  }
                          )
                
                
                
                
                
                
                
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
#     dcc.Store(id='temp')
    
])
                      

###### Callbacks ######



## Opens stream
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
        
        
#         if not Pause_Stream: 
#             Pause_Stream = 0
        
    
        # Forcing two variables into 0 as their default values, instead of NoneType
#         if Submit_Button is None:
#             Submit_Button = 0
        if Pause_Stream is None:
            Pause_Stream = 0
            
            
#         if (Submit_Button == Pause_Stream) or (Last_Following_Info != ScreenName_Input):
#             print('Submit_Button == pause_stream\n{}, {}'.format(Submit_Button, Pause_Stream))
            
#             return dash.no_update, 1, False, True
            
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
        print('Returning nothing')
        return 0, 0, False, True, False

    
    

## Either Input callback should be able to update table
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

    print('tweet_table ran at least, Table_Exists_Or_Not_Check: {}'.format(Table_Exists_Or_Not_Check))

    print('\n\nRESTART CHECK, \nTAable_Exists: {}\nStream_Killed: {}\nmax_inervals: {}\n'.format(Table_Exists_Or_Not_Check, Stream_Killed_or_Not, max_intervals))
    
    ## also missing  or (ScreenName_Input != Last_Following_Info)
    ## Create table with old tweets first if table has not been created yet # (Table_Exists_Or_Not_Check == 1 and not isinstance(Table_Update_Component, int))
    if (Table_Exists_Or_Not_Check == 0 and ScreenName_Input) or (Table_Exists_Or_Not_Check == 1 and Stream_Killed_or_Not == 1 and max_intervals == 0):
        
        print('Table DOES NOT exist.')
        
        tweets = old_tweets(ScreenName_Input, number_tweets)
        
        ## Crucial change below
        return tweets.to_dict(orient='rows'), ScreenName_Input, 1#None#, tweet_author_indices

    
    ## Otherwise, update table with stream's output in csv
    elif Table_Exists_Or_Not_Check == 1:
        
            print('Table DOES exist.')
            
            ## Check if csv exists even        
            if not my_csv.is_file():
                                
                ## Crucial change below as well, hopefully this does not trigger Interval_Helper by sending same things
                return rows, dash.no_update, 2#None

            
            if my_csv.is_file():
                
                f = open(csv_name, newline='')
                lines = sum(1 for line in f)
                f.close()
                
                ## If only header exists, csv is empty and should be ignored
                if lines <2:
                                            
                    ## Crucial change below as well, hopefully this does not trigger Interval_Helper by sending same things
                    return rows, dash.no_update, 2#None
            

                ## Function to read 1) csv from bottom, and 2) live table from top, 
                ## and perform what updates need to be done.
                def read_csv_backwards(file_name, rows, lines):
                    newest_tweets = []
                    
                    with FileReadBackwards(file_name) as fb:
                        j = 0
                        for i, line in enumerate(fb):
                            line_formatted = line.split(sep=',')
                            line_formatted = {'Date': line_formatted[0], 'Author': line_formatted[1], 'Len': line_formatted[2], 
                                              'Favs': line_formatted[3], 'Retw': line_formatted[4], 'Text': line_formatted[5]}  


                            print('\n\n\nCSV ROWS: \n{}\nTABLE ROWS: \n{}\n'.format(line_formatted, rows))
                            
                            if (line_formatted == rows[i]) or (line_formatted['Date'] == 'Date'):
                                print("MATCH!!!!")
                                return rows, newest_tweets

                            elif line_formatted != rows[i]:
                                newest_tweets.append(line_formatted)
                                rows.insert(i+j, line_formatted)
                                j = j + 1

                                    
                ## Needed to place above into function, to utilize return statement to break out of both loops.
                rows, newest_tweets = read_csv_backwards(csv_name, rows, lines)
                
                
                                
                print('\n\nNEWEST_TWEETS: \n{}\n'.format(newest_tweets))
                
                
                
                
                ## After first new tweet comes in (after table has already loaded first time), 
                ## check above function will always run, so check is necessary to see if it
                ## picked up any new tweets.
                if not newest_tweets:
                    return rows, dash.no_update, 2
                elif newest_tweets:
                    return rows, dash.no_update, newest_tweets

    
    else:
        print('No table_exists info yet.')
        
        ## Not sure if to implement crucial change below.
        return [], dash.no_update, 2#None
    

    
@app.callback(
    Output(component_id='Table_Exists_Or_Not_Check', component_property='data'),
   [Input(component_id='tweet_table', component_property='data')]
)
def table_data_check(tweet_data_exists_or_not):
    
    print('\nDOES TWEET TABLE EXIST?\n')#: {}'.format(tweet_data_exists_or_not))
    
    if tweet_data_exists_or_not:
        print('Table existence CONFIRMED.')
        return 1
        
    else:
        print('Table existence NOT HERE.')
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
        
        if (Table_Exists_Or_Not_Check == 1) and (Stream_Killed_or_Not != 1): # and (ScreenName_Input == Last_Following_Info)
            return -1#, 0
        
        elif (Table_Exists_Or_Not_Check == 0) or (Stream_Killed_or_Not == 1): # or (ScreenName_Input != Last_Following_Info)
            return 0#, 0
    
    

## Control over graph(s), runs on same interval component as Data Table visualizer callback
@app.callback(
   [Output(component_id='Sentiment_Graph', component_property='extendData'),
    Output(component_id='Graph_trace_indices', component_property='data')],
   [Input(component_id='Newest_Tweets', component_property='data')],
#    [State(component_id='Interval_Helper', component_property='data'),
#    [State(component_id='Table_Update_Component', component_property='n_intervals'),
    [State(component_id='tweet_table', component_property='data'),
     ## Semi-circular hack below
     State(component_id='Graph_trace_indices', component_property='data')],
)
def sentiment_selected_tweets(Newest_Tweets, tweet_table, Graph_trace_indices):
    
    def generate_trace_per_author(tweets_dict, Graph_trace_indices, create_or_append = 1):
        
#         traces = []
#         for author in tweets_dict.keys():
#             traces.append({'type':'histogram',
#                            'x': tweets_dict[author],
#                            'name': author
#                           })

        print('\n\ntweets_dict: \n{}\n'.format(tweets_dict))


        x_input = list(tweets_dict.values())
        num_tweet_authors = len(x_input)
    
        print('\n\nX_INPUT: {}\n'.format(x_input))

        ## DEG + plotly way to do it, for built-in kde plots
        if create_or_append == 1:
            fig = ff.create_distplot(x_input, [i for i in tweets_dict.keys()], bin_size=.2, show_rug=False)
        elif create_or_append == 2:
            fig = {'data': [{'x': i} for i in x_input]}
            print('\n\nFIGURE: \n{}\n'.format(fig))

            
        traces = []
        for i in fig['data']:
            traces.append(i)
            
        ## Creating traces
        if  create_or_append == 1:
                
            trace_indices = {}
            for i, j in enumerate(tweets_dict.keys()):
                trace_indices[j] = i
                
            print('\n\n\n\nTRACE_INDICES: \n{}\n\n'.format(trace_indices))
            return traces, trace_indices
                
        ## Appending to already existing traces with new tweets      
        elif create_or_append == 2:
            
            traces = [traces]

            trace_indices = []
            for i in tweets_dict.keys():
                trace_indices.extend([Graph_trace_indices[i]])
                
            traces.append(trace_indices)
            
            print('\n\nTRACES_EXTEND: \n{}\n'.format(traces))
            
            return traces
    
    
    
    
    
    if Newest_Tweets == 1:
        
        tweets_sentiment = tweet_sentiment(tweet_table)        
        
        print('\n\nFIRST RUN 1st!!\n{}\n'.format(tweets_sentiment))

        # Tweets' sentiments grouped by Author and then fed in
        traces, trace_indices = generate_trace_per_author(tweets_sentiment, [], 1)
                    
        print('\n\nFIRST RUN 2nd!!\n{}\n'.format(traces))
        
        
        
        print('\n\n\nTHIS IS TRACE: \n{}\n'.format(traces))
        
        return traces, trace_indices
        

    elif Newest_Tweets == 2:
        
        ## Returning same table, if no new tweets have come in since table load
        print('\n\ndash.no_update should be working\n\n')
        
        return dash.no_update, dash.no_update
    
    
        

    elif (Newest_Tweets != 1) or (Newest_Tweets != 2):


        print('\n\nSECOND 1st RUN!!\n{}\n'.format(Newest_Tweets))

        newest_tweets_sentiment = tweet_sentiment(Newest_Tweets) 

        print('\n\nSECOND 2nd RUN!!\n{}\n'.format(newest_tweets_sentiment))
        
        traces = generate_trace_per_author(newest_tweets_sentiment, Graph_trace_indices, 2)


        return traces, dash.no_update

        
    else:
        return {"data": []}, dash.no_update


    
    
## For downloading table data 
@app.callback(
    Output('table_download_link', 'href'),
    [Input('table_download_button', 'n_clicks_timestamp')],
    [State('tweet_table', 'data')]
)
def update_download_link(table_download_button, data):
    
    if table_download_button:
        
    #     dff = df
        dff = pd.DataFrame(data)

        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

        return csv_string
    
    
    
    


if __name__ == '__main__':
    app.run_server(debug=True)