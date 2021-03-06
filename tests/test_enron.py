'''
Created on 01 Nov 2019
Tests of the utils.py functions
@author: charles
'''

from unittest import TestCase
import numpy.testing as npt
from utils.utils import *

class test_utils(TestCase):
    def setUp(self):
        #dummy test data
        self.test_data = pd.DataFrame([['896308260000', '<GKNWYZTKAVMKBCTMA3ZZSQIBITG5OD1KA@zlsvr22>','Christopher Behney','Toni P Schulenburg|mary hain|Mark legal taylor','','email'],
                     ["909792120000","<NFC21LWTHYCKD4JV1IQMLSQ4JX2WY1JCB@zlsvr22>","Mark legal taylor","shari stack|William bradford",'',"email"],
                     ["909802120000","<LFNS0QCMTV4MTA3UELU01XUOIJG1QZ23B@zlsvr22>","mark legal taylor","marie heard|debbie brackett|william bradford|Nidia A Martinez|brandon wax|bob bowen|Christopher Behney|Mary Jones",'',"email"],
                     ["909802220000","<NFLS0QCMTV4MTA3UELU01XUOIJG1QZ23B@lzsvr22>","Mary Jones","debbie brackett|william bradford|Christopher Behney",'',"email"]
                     ])
        
    def test_clean_data_columns(self):
        #do the columns names get set correctly
        df =  clean_data(self.test_data)
        npt.assert_array_equal(df.columns, ['time', 'message_id', 'sender', 'recipients', 'topic', 'mode', 'date'])
    
    def test_clean_data_sender_names(self):
        #does the clean still lowercase the sender names get correctly- test data includes capitalised vs non-capitalised versions of both
        df =  clean_data(self.test_data)
        npt.assert_array_equal(pd.unique(df['sender']),['christopher behney','mark legal taylor','mary jones'])
        
    def test_clean_data_receiver_names(self):
        #does the clean still lowercase the recipient names get correctly- 
        df =  clean_data(self.test_data)
        npt.assert_array_equal(df['recipients'],['toni p schulenburg|mary hain|mark legal taylor','shari stack|william bradford','marie heard|debbie brackett|william bradford|nidia a martinez|brandon wax|bob bowen|christopher behney|mary jones','debbie brackett|william bradford|christopher behney'])

    def test_split_recipients(self):
        #does the recipient column get split correctly- 
        df =  clean_data(self.test_data)
        df_split = split_recipients(df)
        df_received_message_counts = df_split.groupby(df_split).count().reset_index()
        self.assertEqual(df_received_message_counts.values.tolist(),
                         [['bob bowen', 1], ['brandon wax', 1],['christopher behney', 2], \
                          ['debbie brackett', 2], ['marie heard', 1], ['mark legal taylor', 1], \
                          ['mary hain', 1],['mary jones', 1], ['nidia a martinez', 1], ['shari stack', 1], \
                          ['toni p schulenburg', 1], ['william bradford', 3]])
        
    def test_generate_receiver_counts(self):
        #generate the number of emails received by different individuals
        df =  clean_data(self.test_data)
        df_split = split_recipients(df)
        df_rx_counts =  generate_receiver_counts(df_split)
        self.assertEqual(df_rx_counts.values.tolist(),
                         [['bob bowen', 1], ['brandon wax', 1], ['christopher behney', 2], ['debbie brackett', 2], ['marie heard', 1], ['mark legal taylor', 1], ['mary hain', 1],['mary jones', 1], ['nidia a martinez', 1], ['shari stack', 1], ['toni p schulenburg', 1], ['william bradford', 3]])

    def test_generate_sender_counts(self):
        #generate the number of emails sent- counting an email sent to multi parties as a 
        #single email
        df =  clean_data(self.test_data)
        df_sent_counts =  generate_sender_counts(df)
        self.assertEqual(df_sent_counts.values.tolist(),[['christopher behney', 1], ['mark legal taylor', 2], ['mary jones', 1]])
    
    def test_generate_total_counts(self): 
        #test for total received and sent counts 
        df =  clean_data(self.test_data)
        df_sent_counts =  generate_sender_counts(df)  
        df_split = split_recipients(df)
        df_rx_counts =  generate_receiver_counts(df_split)
        total_counts = generate_total_counts(df_rx_counts,df_sent_counts)
        self.assertEqual(total_counts.values.tolist(),\
                         [['christopher behney', 1.0, 2.0], ['mark legal taylor', 2.0, 1.0],['mary jones', 1.0, 1.0], ['bob bowen', 0.0, 1.0], 
                          ['brandon wax', 0.0, 1.0], ['debbie brackett', 0.0, 2.0], ['marie heard', 0.0, 1.0], 
                          ['mary hain', 0.0, 1.0], ['nidia a martinez', 0.0, 1.0], ['shari stack', 0.0, 1.0], 
                          ['toni p schulenburg', 0.0, 1.0], ['william bradford', 0.0, 3.0]])
        
    def test_return_highest_senders(self):
        #test the top percentage return. The test data set has two senders.
        #mark legal taylor = 2
        #christopher behney =1
        #So anything above 50% should return both
        #Anything below 50% should return 'mark legal taylor'
        df =  clean_data(self.test_data)
        df_sent_counts =  generate_sender_counts(df)  
        self.assertEqual(return_highest_senders(df_sent_counts,60).values.tolist(),\
                         [['mark legal taylor',2],['christopher behney',1],['mary jones', 1]])
        self.assertEqual(return_highest_senders(df_sent_counts,10).values.tolist(),\
                         [['mark legal taylor',2]])
       
    def test_return_email_heatmap(self): 
        df =  clean_data(self.test_data)
        sender_message_counts =  generate_sender_counts(df)  
        sent_messages = sender_message_counts.merge(df,left_on = 'id', right_on = 'sender')
        df_heatmap = return_email_heatmap(sent_messages,"id","date","sent_count",np.float32)
        #one message sent by Christopher Behney on 1998-05-27 22:31:00
        self.assertEqual(df_heatmap['1998-05-31'].tolist(),[1.0, 0.0, 0.0])
        #two messages sent by Christopher Behney on 1998-10-31 00:02:00 and 1998-10-31 02:48:40
        self.assertEqual(df_heatmap['1998-10-31'].tolist(),[0.0, 2.0, 1.0])
        #check response with log of the values
        df_heatmap = return_email_heatmap(sent_messages,"id","date","sent_count",np.log10)
        self.assertEqual(df_heatmap['1998-10-31'].tolist(),[0.0, 0.3010299956639812, 0.0])
        
    def test_return_highest_sender_received(self): 
        df =  clean_data(self.test_data)
        top_sender_received_messages = return_highest_sender_received(df,1)
        #print(top_sender_received_messages[['message_id','sender','recipient']].values.tolist())
        self.assertEqual(top_sender_received_messages[['message_id','sender','recipient']].values.tolist(),\
                         [['<GKNWYZTKAVMKBCTMA3ZZSQIBITG5OD1KA@zlsvr22>', 'christopher behney', 'mark legal taylor']])
        top_sender_received_messages = return_highest_sender_received(df,60)

        self.assertEqual(top_sender_received_messages[['message_id','sender','recipient']].values.tolist(),\
                         [['<GKNWYZTKAVMKBCTMA3ZZSQIBITG5OD1KA@zlsvr22>', 'christopher behney', 'mark legal taylor'], \
                          ['<LFNS0QCMTV4MTA3UELU01XUOIJG1QZ23B@zlsvr22>', 'mark legal taylor', 'christopher behney'],
                          ['<NFLS0QCMTV4MTA3UELU01XUOIJG1QZ23B@lzsvr22>', 'mary jones', 'christopher behney'],
                          ['<LFNS0QCMTV4MTA3UELU01XUOIJG1QZ23B@zlsvr22>','mark legal taylor','mary jones']
                          ])
        
    def test_return_distinct_received_heatmap(self):
        df =  clean_data(self.test_data)
        top_sender_received =  return_highest_sender_received(df,100)
        scaled_unique_responses = return_distinct_received_heatmap(top_sender_received, "id", "date","sender")
        self.assertEqual(scaled_unique_responses['1998-10-31'].values.tolist(),[1., 0., 0.5]) #should be 1 for mark legal taylor and 0.5 for mary jones





        

        
        
    
