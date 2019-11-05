# Enron Email sending

This repo will do the following:
1) **_message_count_totals.csv_**\
Produce a .csv file with three columns---"person", "sent", "received"---where the final two columns contain the number of emails that person sent or received in the data set. This file should be sorted by the number of emails sent.
2) **_top_emailers.png_**\
Produce a PNG image ( ) visualizing the number of emails sent over time by some of the most prolific senders in (1). There are no specific guidelines regarding the format and specific content of the visualization---you can choose which and how many senders to include, and the type of plot---but you should strive to make it as clear and informative as possible, making sure to represent time in some meaningful way.
3) **_top_emailers_distinct_responses.png_**\
A visualization that shows, for the same people, the number of unique people/email addresses who contacted them over the same time period. The raw number of unique incoming contacts is not quite as important as the relative numbers (compared across the individuals from (2) ) and how they change over time.



**Installation**\
_Setup and activate a virtual environment using Python 3_
```bash
python3 -m venv enron_data
source enron_data/bin/activate
pip install -r requirements.txt
```

_Check the code works using the unit tests_
```bash
python -m unittest discover tests -v
```

_Run the script_
```bash
python summarize-enron.py enron-event-history-all.csv
```
