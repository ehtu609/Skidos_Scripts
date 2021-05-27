import json
import pandas as pd
from pandas.io.json import json_normalize

#function for appfollow data processing

def af_data_process(data):
	afjdata = json.loads(data)
	af_df = pd.json_normalize(afjdata['apps_app'])
	af_df_cleaned = af_df.drop(af_df.iloc[:, 16:22], axis = 1)
	af_df_cleaned = af_df.rename({'app.ext_id':'ext_id'}, inplace=False)
	af_df_cleaned.to_csv('D:/Data/appfollownew.csv')
	return af_df_cleaned
