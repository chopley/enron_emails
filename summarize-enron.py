'''
Created on 01 Nov 2019
Main script to handle enron email data processing
@author: charles
'''

import sys
import pandas as pd
import matplotlib
import numpy as np
import scipy
import scipy.stats
import datetime
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib import pyplot as plt
from utils.utils import *

file =  str(sys.argv[1])
#read csv file
enron_data = pd.read_csv(file)

#clean enron data
enron_data_cleaned = clean_data(enron_data)
#split the receiver ids into multirows
enron_data_split = split_recipients(enron_data_cleaned)
#counts for received 
receiver_message_counts = generate_receiver_counts(enron_data_split)
#counts for sent 
sender_message_counts = generate_sender_counts(enron_data_cleaned)
#counts for sent and received
total_messages = generate_total_counts(receiver_message_counts,
                                       sender_message_counts)
#save output to csv
total_messages.sort_values(by='sent_count',ascending=False).\
    to_csv("message_count_totals.csv",index=False)
#get the IDs with the highest percentage sent
top_sender_df = return_highest_senders(sender_message_counts,
                                       0.2) #top 0.2 percent
#add the received data to the top sender data
top_sender_messages = top_sender_df.merge(enron_data_cleaned,
                                          left_on = 'id', 
                                          right_on = 'sender')
#all_messages_df = return_email_heatmap(all_messages,"id","date","sent_count")
top_sender_messages_df = return_email_heatmap(top_sender_messages,
                                              "id",
                                              "date",
                                              "sent_count",
                                              np.log10)
#save file to png file
save_heatmap_plot_to_file(top_sender_messages_df,
                          "./top_emailers.png",
                          5,
                          20,
                          "Most Prolific Email Senders",
                          "Log10(Messages Sent)")

#in order to get the received message counts, we can re-use the return_email_heatmap
#but we need to get the received counts rather than sent counts

top_sender_received =  return_highest_sender_received(enron_data_cleaned,
                                                      0.2)
top_sender_messages_df = return_email_heatmap(top_sender_received,
                                              "id",
                                              "date",
                                              "sent_count",
                                              np.log10)
distinct_received_heatmap_df = return_distinct_received_heatmap(top_sender_received,
                                                                 "id", 
                                                                 "date",
                                                                 "sender")
save_heatmap_plot_to_file(distinct_received_heatmap_df,
                          "./top_emailers_distinct_responses.png",
                          5,
                          20,
                          "Fraction of unique people contacting the top email senders \n Normalised by time period ",
                          "Fraction (normalised by time period")



