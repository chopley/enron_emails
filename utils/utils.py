'''
Created on 01 Nov 2019

@author: charles
'''

import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

def return_email_heatmap(dataframe, id_col, date_col, count_col):
    groups = dataframe[[id_col,date_col,count_col]].groupby([id_col,pd.Grouper(key=date_col,freq='M')]).sum()
    groups[count_col] = np.log10(groups[count_col]) #log scale of the counts to provide better 
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

def save_heatmap_plot_to_file(df, filename, x_size, y_size, title_text):
    fig = plt.figure(figsize= (x_size,y_size))
    ax = sns.heatmap(df,xticklabels =  7,cmap="Greys")
    ax.set_ylabel("Name",fontsize=15)
    ax.set_xticklabels(df.columns.strftime("%Y-%m")[::7])
    ax.set_title(title_text,fontsize=15, pad=30)
    ax.set_xlabel("Date",fontsize=15)
    fig.autofmt_xdate()
    ax.collections[0].colorbar.set_label("Log10(Messages Sent)")
    fig.autofmt_xdate()
    fig.savefig(filename,bbox_inches='tight')