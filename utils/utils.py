'''
Created on 01 Nov 2019
Utility functions to assist with enron email data processing
@author: charles
'''

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from math import ceil
from sklearn import preprocessing 

def clean_data(dataframe):
    """manually set the column names since they aren't in the csv file
    """
    dataframe.columns = ['time','message_id','sender',
                     'recipients','topic','mode']
    #create date column using the unix timestamp
    dataframe['date'] = pd.to_datetime(dataframe['time'],unit='ms')
    #rudimentary data cleaning- remove capitalization, apostrophes etc.
    dataframe['sender'] = dataframe['sender'].astype(str).str.lower().\
        replace('\*','',regex=True).replace('\"', '',regex=True)
    #force NaN to be treated as a string- also lower case to standardise the names,
    #remove a few unwanted characters etc.
    dataframe["recipients"] = dataframe["recipients"].astype(str).str.\
        lower().replace('\*','',regex=True).replace('\"', '',regex=True)
    return(dataframe)
        
def split_recipients(dataframe):
    """the recipients are stored multiple ids per row, and separated by |
    character- we need to explode those out
    see https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows
    """
    dataframe_recipients = pd.DataFrame(dataframe.recipients.str.\
                                     split('|').values.tolist(), \
                                     index=dataframe.message_id).stack()
    return(dataframe_recipients)

def generate_receiver_counts(dataframe):
    """do the counts for received and sent separately as this avoids a big join
    """
    receiver_message_counts = dataframe.groupby(dataframe).count().reset_index()
    receiver_message_counts.columns = ["id","received_count"]
    receiver_message_counts['id'] = receiver_message_counts['id'].astype(str).str.lower().replace('\*','',regex=True).replace('\"', '',regex=True)
    return(receiver_message_counts)

def generate_sender_counts(dataframe):
    """how many email were sent by each sender- if multiple recipients I count this as one
    """
    enron_data_senders = dataframe.drop(["time","recipients","topic","mode","date"],axis=1)
    sender_message_counts = enron_data_senders.groupby("sender").count().reset_index()
    sender_message_counts.columns = ["id","sent_count"]
    return(sender_message_counts)

def generate_total_counts(dataframe_rx_count,
                          dataframe_sent_count):
    """how many email were sent and received by each id
    """
    total_messages = pd.DataFrame.merge(dataframe_sent_count,dataframe_rx_count,how='outer',left_on = 'id', right_on = 'id')
    total_messages
    return(total_messages.fillna(0))

def return_highest_senders(dataframe,
                           percent):
    """return the senders that had highest percentage sent
    """
    alength = len(dataframe)
    percent_of_messages = percent
    top_senders = ceil(alength * percent_of_messages/100)
    #extract the top senders from the dataframe
    top_sender_df = dataframe.nlargest(n=top_senders, columns = "sent_count", keep='all')
    return(top_sender_df)

def return_highest_sender_received(dataframe,
                                   percent):
    """Return the messages sent to the top email senders
    """
    df_sent_counts = generate_sender_counts(dataframe) 
    top_sender_df = return_highest_senders(df_sent_counts,percent)
    df_split = split_recipients(dataframe)
    df_split_reindex = df_split.reset_index()
    df_split_reindex.columns = ['message_id','level','recipient']
    top_sender_received_messages = dataframe[['date','message_id','sender']].\
        merge(df_split_reindex,'outer',right_on = 'message_id', left_on = 'message_id').\
        merge(top_sender_df,how='inner',left_on = 'recipient', right_on = 'id')
    return(top_sender_received_messages)

def return_email_heatmap(dataframe, 
                         id_col, 
                         date_col, 
                         count_col,
                         func_to_apply):
    """
    """
    groups = dataframe[[id_col,date_col,count_col]].groupby([id_col,pd.Grouper(key=date_col,freq='M')]).count()
    groups[count_col] = func_to_apply(groups[count_col]) #apply scaling function to the count column e.g. np.log10
    groups = groups.reset_index()
    groups[date_col] = pd.to_datetime(groups[date_col])
    groups_df = groups.set_index([date_col, id_col]
    ).unstack(
    fill_value=0
    ).asfreq(
    'M', fill_value=0
    ).stack().sort_index(level=1).reset_index()
    gg = groups_df.pivot(index=date_col,columns=id_col,values=count_col).T.fillna(value=0)
    return(gg)

def return_distinct_received_heatmap(dataframe, 
                                     id_col, 
                                     date_col, 
                                     sender_col):
    """count the number of distinct incoming addresses per month
    """
    groups = dataframe[[id_col,date_col,sender_col]].\
        groupby([id_col,pd.Grouper(key=date_col,freq='M')]).\
        agg('nunique')[sender_col] 
    groups = groups.reset_index()
    groups[date_col] = pd.to_datetime(groups[date_col])
    groups_df = groups.set_index([date_col, id_col]
    ).unstack(
    fill_value=0
    ).asfreq(
    'M', fill_value=0
    ).stack().sort_index(level=1).reset_index()
    gg = groups_df.pivot(index=date_col,columns=id_col,values=sender_col).T.fillna(value=0)
    #now we scale things to maximum per column
    x = gg.values #returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    df = pd.DataFrame(x_scaled) 
    df.columns = gg.columns
    df = df.set_index(gg.index) 
    return(df)


def save_heatmap_plot_to_file(df, 
                              filename, 
                              x_size, 
                              y_size, 
                              title_text, 
                              legend_text):
    """ Create timeseries heatmap from a matrix of dates + values
    """
    fig = plt.figure(figsize= (x_size,y_size))
    ax = sns.heatmap(df,xticklabels =  7,cmap="Greys")
    ax.set_ylabel("Name",fontsize=15)
    ax.set_xticklabels(df.columns.strftime("%Y-%m")[::7])
    ax.set_title(title_text,fontsize=15, pad=30)
    ax.set_xlabel("Date",fontsize=15)
    fig.autofmt_xdate()
    ax.collections[0].colorbar.set_label(legend_text)
    fig.autofmt_xdate()
    fig.savefig(filename,bbox_inches='tight')
