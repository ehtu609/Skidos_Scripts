import os
import io
import pandas as pd

def combine():
    appstore=pd.read_csv('D:/Data/appstore.csv')
    appfollow=pd.read_csv('D:/Data/appfollow_df.csv')
    consolidated = pd.merge(appstore, appfollow, on='ext_id', how='left')
    filter = consolidated['attributes.bundleId'].str.contains('prototype')
    consolidated=consolidated[~filter]
    consolidated.to_csv('D:/Data/status_combine.csv')
    return consolidated
