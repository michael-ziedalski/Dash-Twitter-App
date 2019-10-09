import plotly
import plotly.figure_factory as ff
from file_read_backwards import FileReadBackwards


## Function to concurrently read 1) csv from bottom and 2) live table from top, 
## and perform what updates need to be done.
def read_csv_backwards(file_name, rows, lines):
    
    newest_tweets = []
    with FileReadBackwards(file_name) as fb:
        j = 0
        for i, line in enumerate(fb):
            line_formatted = line.split(sep=',')

            print('\n\nCHECKING:\n{}\n\n'.format(line_formatted))
            
            line_formatted = {'Date': line_formatted[0], 'Author': line_formatted[1], 'Len': line_formatted[2], 
                              'Favs': line_formatted[3], 'Retw': line_formatted[4], 'Text': line_formatted[5]}  

            if (line_formatted == rows[i]) or (line_formatted['Date'] == 'Date'):
                print("MATCH!!!!")
                return rows, newest_tweets

            elif line_formatted != rows[i]:
                newest_tweets.append(line_formatted)
                rows.insert(i+j, line_formatted)
                j = j + 1

                

## Creating traces that Dash/plotly can make graphs out of
def generate_trace_per_author(tweets_dict, Graph_trace_indices, create_or_append = 1, Only_Keywords_Search = 0):

    x_input = list(tweets_dict.values())

    ## If traces are being created, either at start of app, or when picking new twitter accounts
    if create_or_append == 1:


        # print("\n\nCREATING trace: x_input\n{}\n\n".format(x_input))



        ## Using automative plotly method to plot histograms + kde's at once
        fig = ff.create_distplot(x_input, [i for i in tweets_dict.keys()], bin_size=.2, show_rug=False)

        traces = []
        for i in fig['data']:
            traces.append(i)

        ## To create a dict carrying the index of each trace, 
        ## so future tweets know which trace to go into
        trace_indices = {}
        for i, j in enumerate(tweets_dict.keys()):
            trace_indices[j] = i



        print("\n\nCREATING trace_indices:\n{}\n\n".format(trace_indices))



        ## Slight visual editing
        for i in traces:
            if isinstance(i, plotly.graph_objs.Histogram):
                i['xbins'] = {'end': 1, 'size': 0.2, 'start': -1.0}
                i['histnorm'] = 'probability'



        # print("\n\nCREATING trace: traces\n{}\n\n".format(traces))



        figure = {'data': traces}

        return figure, trace_indices

    ## Or appending to existing traces
    elif create_or_append == 2:

        ## Check if tweets should be grouped by author, such as when not searching purely by keyword
        if Only_Keywords_Search == 0:

            # print("\n\nAPPENDING trace: x_input\n{}\n\n".format(x_input))


            fig = {'data': [{'x': i} for i in x_input]}

            traces = []
            for i in fig['data']:
                traces.append(i)

            traces = [traces]


            print("\n\nAPPENDING trace: trace itself\n{}\n\n".format(traces))


            # print("\n\nAPPENDING trace: traces\n{}\n\n".format(traces))


            trace_indices = []
            for i in tweets_dict.keys():
                trace_indices.extend([Graph_trace_indices[i]])

            traces.append(trace_indices)


            print("\n\nAPPENDING trace: trace_indices\n{}\n\n".format(trace_indices))


            return traces

        ## Searching by pure keywords
        elif Only_Keywords_Search == 1:

            traces = [[{'x': x_input[0]}]] ## x_input has some unnecessary nested list, so getting out with [0]
            trace_indices = [0]



            print("\n\nAPPENDING trace: trace itself\n{}\n\n".format(traces))

            print("\n\nAPPENDING trace: trace_indices\n{}\n\n".format(trace_indices))



            traces = traces.append(trace_indices)

            return traces

