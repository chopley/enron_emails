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



#file =  str(sys.argv[1])
file =  "enron-event-history-all.csv"
#read csv file
enron_data = pd.read_csv(file)
#manually set the column names since they aren't in the csv file
enron_data.columns = ['time','message_id','sender',
                     'recipients','topic','mode']

#create date column using the unix timestamp
enron_data['date'] = pd.to_datetime(enron_data['time'],unit='ms')

#rudimentary data cleaning- remove capitalization, apostrophes etc.
enron_data['sender'] = enron_data['sender'].astype(str).str.lower().\
    replace('\*','',regex=True).replace('\"', '',regex=True)
#force NaN to be treated as a string- also lower case to standardise the names,
#remove a few unwanted characters etc.
enron_data["recipients"] = enron_data["recipients"].astype(str).str.\
lower().replace('\*','',regex=True).replace('\"', '',regex=True)


#the recipients are stored multiple ids per row, and separated by |
#character- we need to explode those out
#see https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows
enron_data_recipients = pd.DataFrame(enron_data.recipients.str.\
                                     split('|').values.tolist(), \
                                     index=enron_data.message_id).stack()

#do the counts for received and sent separately as this avoids a big join
receiver_message_counts = enron_data_recipients.groupby(enron_data_recipients).count().reset_index()
receiver_message_counts.columns = ["id","received_count"]
receiver_message_counts['id'] = receiver_message_counts['id'].astype(str).str.lower().replace('\*','',regex=True).replace('\"', '',regex=True)


enron_data_senders = enron_data.drop(["time","recipients","topic","mode","date"],axis=1)
sender_message_counts = enron_data_senders.groupby("sender").count().reset_index()
sender_message_counts.columns = ["id","sent_count"]

total_messages = pd.DataFrame.merge(sender_message_counts,receiver_message_counts,how='outer',left_on = 'id', right_on = 'id')
total_messages.to_csv("message_count_totals.csv")

alength = len(sender_message_counts)
percent_of_messages = 0.2
top_senders = np.int(alength * percent_of_messages/100)

#extract the top senders from the dataframe
top_sender_df = sender_message_counts.nlargest(n=top_senders,columns = "sent_count")
all_messages = sender_message_counts.merge(enron_data,left_on = 'id', right_on = 'sender')
top_sender_messages = top_sender_df.merge(enron_data,left_on = 'id', right_on = 'sender')

#all_messages_df = return_email_heatmap(all_messages,"id","date","sent_count")
top_messages_df = return_email_heatmap(top_sender_messages,"id","date","sent_count")

#save_heatmap_plot_to_file(all_messages_df,"./all_emailers.png",5,300)
save_heatmap_plot_to_file(top_messages_df,"./top_emailers.png",5,20,"Most Prolific Email Senders")




print("hello")

