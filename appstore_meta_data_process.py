
import pandas as pd
from pandas.io.json import json_normalize

def appstore_processed_data(x):
    #ap_df = pd.DataFrame(x['data'])
    ap_df=pd.json_normalize(x, record_path=['data'])
    ap_df = ap_df.rename({'id': 'ext_id'}, axis=1, inplace = False)
    ap_df.drop(ap_df.iloc[:, 6:40], inplace = True, axis = 1)
    ap_df.to_csv('D:/Data/appstore.csv')
    return ap_df
    
