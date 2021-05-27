
import pandas as pd
import smtplib
import email
from email_contacts import myemail, password, my_second_email, email_sriram

def email_notification():
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(myemail, password)
    message = "Test Email For raw data timeliness reports"
    s.sendmail(myemail, my_second_email, message)
    s.quit()


"""
def email_notification():
    df=pd.read_csv('D:\Data\redflag_reports.csv')
    for index, row in df.iterrows():
        print (row["Reports name"], row["Status"])
        if row["Status"]=="Not Updated":
            print("Sent an email")
            li=[my_second_email]
            for dest in li:
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(myemail, password)
                message = "Test Email For raw data timeliness reports"
                s.sendmail(myemail, dest, message)
                s.quit()
        else:
            pass

"""
