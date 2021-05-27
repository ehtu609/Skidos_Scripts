import os
import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta

def top_funnel_ios_report():
    for (root,dirs,files) in os.walk('D:\ios raw data', topdown=True):
        for file in files:
            substring=file[-14:-4]
            dated_substring=datetime.strptime(substring, '%Y-%m-%d')
            dated_substring=dated_substring.date()
            #file_date.append(dated_substring)
            #print(dated_substring)
            
            current_date=datetime.today()
            current_date=current_date.date()
            #print(current_date)
            
            difference_in_dates=current_date - dated_substring
            difference_in_days=difference_in_dates.days
            #print(difference_in_days)
            #datetime.timedelta(days=1)):
            #diff_days=timedelta(days=1)
            critical_view=[]
            critical_view_ID=[]
            reports_name=[]
            fetch_file_until_date=[]
            curr_date_list=[]
            
            if (difference_in_days==1):
                critical_view_ID.append("CVBR1")
                reports_name.append("AppFollow ios top funnel")
                critical_view.append("Updated")
                fetch_file_until_date.append(dated_substring)
                curr_date_list.append(current_date)
                
                timeliness_reports={'Business Rule no.':critical_view_ID,'Reports name':reports_name,'Status':critical_view, 'Reports date':fetch_file_until_date, 'Current Date':curr_date_list}
                
                df=DataFrame(timeliness_reports, columns=['Business Rule no.', 'Reports name','Status', 'Reports date', 'Current Date'])
                
            else:
                critical_view_ID.append("CVBR1")
                reports_name.append("AppFollow ios top funnel")
                critical_view.append("Not Updated")
                fetch_file_until_date.append(dated_substring)
                curr_date_list.append(current_date)
                timeliness_reports={'Business Rule no.':critical_view_ID,'Reports name':reports_name,'Status':critical_view, 'Reports date':fetch_file_until_date, 'Current Date':curr_date_list}
                df=DataFrame(timeliness_reports, columns=['Business Rule no.','Reports name', 'Status', 'Reports date', 'Current Date'])
    df.to_csv(r'D:\Data\Redflag_reports\redflag_reports.csv', index=False)


def ios_subscription_report():
    with os.scandir('D:\othermonthlyreports') as files:
        for file in files:
            substring=file.name[-17:-9]
            dated_substring=datetime.strptime(substring, '%Y%m%d')
            dated_substring=dated_substring.date()
            current_date=datetime.today()
            current_date=current_date.date()
            #print(dated_substring)
        
            difference_in_dates=current_date - dated_substring
            difference_in_days=difference_in_dates.days

                
            df=pd.read_csv(r'D:\Data\Redflag_reports\redflag_reports.csv')
               
            if "CVBR2" in df["Business Rule no."].unique():
                pass
            
            else:
                 df=df.append({'Business Rule no.':"CVBR2", 'Reports name': "ios subscription", 'Status':"Updated",'Reports date':dated_substring,'Current Date':current_date}, ignore_index=True)

            if (difference_in_days<=2):
                df.loc[df['Business Rule no.'] == "CVBR2", 'Status'] = "Updated"
                df.loc[df['Business Rule no.'] == "CVBR2", 'Reports date'] = dated_substring 
                df.loc[df['Business Rule no.'] == "CVBR2", 'Current Date'] = current_date
            else:
                df.loc[df['Business Rule no.'] == "CVBR2", 'Status'] = "Not Updated"
                df.loc[df['Business Rule no.'] == "CVBR2", 'Reports date'] = dated_substring 
                df.loc[df['Business Rule no.'] == "CVBR2", 'Current Date'] = current_date
                    
        df.to_csv(r'D:\Data\Redflag_reports\redflag_reports.csv', index=False)



        
