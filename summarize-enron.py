import sys
import pandas as pd


file =  str(sys.argv[1])
#read csv file
enron_data = pd.read_csv(file)
#manually set the column names
enron_data.columns = ['time','message_id','sender',
                     'recipients','topic','mode']
#force NaN to be treated as a string
enron_data["recipients"] = enron_data["recipients"].astype(str)  

#the recipients are stored multiple per row- we need to explode those out
#see https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows
enron_data_exploded = pd.DataFrame(enron_data.recipients.str.split(',').values.tolist(), 
        index=enron_data.message_id).stack() 





