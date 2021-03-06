""" Module for anomaly detection system """
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime, date
from datetime import timedelta
import logging
import pandas as pd
import sys
import numpy as np
from fbprophet import Prophet
logger = logging.getLogger("Prophet")
logger.setLevel(logging.DEBUG)
import smtplib
# from premailer import transform

today = datetime.now().date()
# today = datetime.combine(today, datetime.min.time())
complete_data_date = today - timedelta(days=3)
complete_data_date = pd.to_datetime(complete_data_date)
print(complete_data_date)
m = Prophet()
print(m.stan_backend)

# creating a lastest week period after gettting the complete data
week_one_lastday = complete_data_date - timedelta(days=1)
week_one_firstday = week_one_lastday - timedelta(days=6)

# will be using a date_parser to convert Dates to datetime
d_parser = lambda x: datetime.strptime(x, "%Y-%m-%d")


def color_negative_red(value):
    """function colour negative value"""
    if value < 0:
        color = "red"
    elif value > 0:
        color = "green"
    else:
        color = "black"
    return "color: %s" % color


def format_row_wise(styler, formatter):
    """function to format row wise data"""
    for row, row_formatter in formatter.items():
        row_num = styler.index.get_loc(row)
        for col_num in range(len(styler.columns)):
            styler._display_funcs[(row_num, col_num)] = row_formatter
    return styler


# source data will also be use for EDA
df = pd.read_csv(
    r"C:\Users\Sriram\Desktop\KPI Dashboard\Script\skidosDailyFunnel.csv",
    parse_dates=["Date"],
    date_parser=d_parser,
)
df.set_index("Date")
#infer_datetime_format = True
print("Shape of the source data: ", df.shape)
print("-----------------------------------------")
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.replace(np.nan, 0, inplace=True)
df_for_model = df.copy()
mask1 = (df_for_model["Date"] >= "2020-07-01") & (
    df_for_model["Date"] <= complete_data_date
)
df_for_model = df_for_model.loc[mask1]
# the time series unlike previous year where pandemic had huge impact
print("Shape of the data to be modeled from last year july:", df_for_model.shape)
print("-----------------------------------------")
# saving the datasets into a csv (interim file )
df_for_model.to_csv(r"data_used_modeling.csv", index=False)

df_avg = df_for_model.copy()
mask2 = (df_avg["Date"] >= week_one_firstday) & (df_avg["Date"] <= week_one_lastday)
df_avg = df_avg.loc[mask2]
print(
    "Shape of the latest week data for complete data current date - 3 days:",
    df_avg.shape,
)
print("-----------------------------------------")
# filtering on for USA users
df_for_model = df_for_model.loc[df_for_model["Country"] == "USA"]
print("Shape of data for USA:", df_for_model.shape)
print("-----------------------------------------")

# cotextual anomaly as considering only USA and iOS users
print("Shape before filtering platform users:", df_for_model.shape)
print("-----------------------------------------")
df_for_model_ios = df_for_model.loc[df_for_model["Platform"] == "iOS"]
print("Shape after filtering only for iOS users:", df_for_model_ios.shape)
print("-----------------------------------------")

print("Max date of the data:", df_for_model_ios["Date"].max())
print("-----------------------------------------")
print("Min date of the data:", df_for_model_ios["Date"].min())

df_avg["month"] = df_avg["Date"].dt.strftime("%B")
df_avg["year"] = df_avg["Date"].dt.strftime("%Y")
df_avg["dayofweek"] = df_avg["Date"].dt.strftime("%A")
df_avg["quarter"] = df_avg["Date"].dt.quarter
df_avg["dayofyear"] = df_avg["Date"].dt.dayofyear
df_avg["dayofmonth"] = df_avg["Date"].dt.day
df_avg["weekofyear"] = df_avg["Date"].dt.weekofyear
df_avg = df_avg[
    [
        "Date",
        "month",
        "year",
        "dayofweek",
        "dayofyear",
        "dayofmonth",
        "weekofyear",
        "quarter",
        "Impressions",
        "Product Page Views",
        "Platform",
        "Downloads",
        "UserId",
        "New Trials",
        "New Subscriptions",
        "ReachedLimit",
        "Re-download",
        "Free or Paid app",
    ]
]

# this aggregation is only to the mean for downloads_to_new_trials for the latest week data
df_avg = (
    df_avg.groupby("Date")[
        "Impressions",
        "Product Page Views",
        "Downloads",
        "UserId",
        "New Trials",
        "New Subscriptions",
        "ReachedLimit",
        "Re-download",
        "Free or Paid app",
    ]
    .sum()
    .reset_index()
    .sort_values(by="Date")
)
df_avg["Downloads_to_New_Trials"] = (df_avg["New Trials"] / df_avg["Downloads"]) * 100
print("-----------------------------------------")
print("Shape of the Calculated dataframe after aggregation:", df_avg.shape)
print("-----------------------------------------")
df_avg = df_avg.groupby("Date")["Downloads_to_New_Trials"].agg(["mean"])
print(
    "Shape of the dataframe after calculating average for latest week data:",
    df_avg.shape,
)
print("-----------------------------------------")

# # aggregating on data to get sum of numeric inputs for per day
df_for_model = (
    df_for_model.groupby("Date")[
        "Impressions",
        "Product Page Views",
        "Downloads",
        "UserId",
        "New Trials",
        "New Subscriptions",
        "ReachedLimit",
        "Re-download",
        "Free or Paid app",
    ]
    .sum()
    .reset_index()
    .sort_values(by="Date")
)
print("Shape of the Calculated dataframe after aggregation:", df_for_model.shape)
# df['New Trials'] contains the sum of daily data similary df['Downloads']
df_for_model["Downloads_to_New_Trials"] = (
    df_for_model["New Trials"] / df_for_model["Downloads"]
) * 100
# Using only datetime and Downloads_To_New_Trials columns
df_for_model = df_for_model[["Date", "Downloads_to_New_Trials"]]
# renaming as per prophet requirement
df_for_model.rename(
    columns={"Date": "ds", "Downloads_to_New_Trials": "y"}, inplace=True
)
df_for_model.set_index("ds")

m = Prophet(
    growth="linear",
    changepoint_prior_scale=0.1,
    holidays_prior_scale=0.2,
    n_changepoints=150,
    seasonality_mode="additive",
    weekly_seasonality=True,
    daily_seasonality=True,
    yearly_seasonality=True,
    interval_width=0.95,
)
m.add_country_holidays(country_name="US")
m.fit(df_for_model)

future = m.make_future_dataframe(periods=3, freq="D")
forecast = m.predict(future)
# this line assign actual downloads_to_new_trials
forecast["fact"] = df_for_model["y"].reset_index(drop=True)
print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "fact"]].tail(5))

forecast.drop(forecast.tail(3).index, inplace=True)
print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "fact"]].tail(5))


def detect_anomalies(forecast):
    forecasted = forecast[
        ["ds", "trend", "yhat", "yhat_lower", "yhat_upper", "fact"]
    ].copy()
    # forecast['fact'] = df['y']

    forecasted["anomaly"] = 0
    forecasted.loc[forecasted["fact"] > forecasted["yhat_upper"], "anomaly"] = 1
    forecasted.loc[forecasted["fact"] < forecasted["yhat_lower"], "anomaly"] = -1

    # anomaly importances
    forecasted["importance"] = 0
    forecasted.loc[forecasted["anomaly"] == 1, "importance"] = (
        forecasted["fact"] - forecasted["yhat_upper"]
    ) / forecast["fact"]
    forecasted.loc[forecasted["anomaly"] == -1, "importance"] = (
        forecasted["yhat_lower"] - forecasted["fact"]
    ) / forecast["fact"]

    return forecasted


pred = detect_anomalies(forecast)
pred.reset_index()

# checking only the latest date to which we have complete data
pred = pred.loc[pred["ds"] == complete_data_date]
print(pred)

# Set CSS properties for th elements in dataframe
th_props = [
    ("border-color", "black"),
    ("border-style ", "solid"),
    ("border-width", "1px"),
    ("font-size", "13px"),
    ("text-align", "left"),
    ("font-weight", "bold"),
    ("color", "#121212"),
    ("background-color", "#b6baba"),
]

# Set CSS properties for td elements in dataframe
td_props = [
    ("border-color", "black"),
    ("border-style ", "solid"),
    ("border-width", "1px"),
    ("font-size", "13px"),
    ("text-align", "left"),
]

# Set table styles
styles = [
    dict(selector="th", props=th_props),
    dict(selector="caption", props=[("caption-side", "bottom")]),
    dict(selector="td", props=td_props),
]

df1 = pred.copy()
html = (
    (df1.style.applymap(color_negative_red, subset=["anomaly"]))
    .format(
        {
            "trend": "{:.2f}",
            "yhat": "{:.2f}",
            "yhat_lower": "{:.2f}",
            "yhat_upper": "{:.2f}",
            "fact": "{:.2f}",
            "anomaly": "{:0f}",
        }
    )
    .set_table_styles(styles)
)


def send_email(styler):
#     sender = "ehtesham.ahmad@skidos.com"
#     recipients = """ehtesham.ahmad@skidos.comsriram@skidos.com,
#     rassel@skidos.com,
#     milan.parihar@skidos.com,
#     nirmal@skidos.com,ole@skidos.com,
#     aditya@skidos.com,
#     prashaant@skidos.com,
#     faizan@skidos.com,
#     oksana@skidos.com,
#     danish@skidos.com"""
    recipients = "ahmedehtesham609@gmail.com"
    msg = MIMEMultipart("related")
    msg["From"] = "ehtesham.ahmad@skidos.com"
    msg["To"] = "ahmedehtesham609@gmail.com"
    msg["Subject"] = "An Anomaly detected please investigate on " + "{}".format(
        complete_data_date
    )

    html = """
    <html>
        <head></head>
        <body>
            <p>Hi, Please find the stats for the anomaly detected <br>
                {0}<br><br><img src="cid:image1">
                <br>
                {1}
                <br>
                Thanks and regards
                <br>Ehtesham<br>
                Associate Data Analyst<br>
                Skidos Learning Labs<br>
            </p>
        </body>
    </html>
    """.format(
        complete_data_date, styler
    )

    part1 = MIMEText(html, "html")
    msg.attach(part1)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login("ehtesham.ahmad@skidos.com", "Talatjahan_9")
    server.sendmail(sender, recipients.split(","), msg.as_string())
    server.quit()
    return "Mail sent successfully."

# styler = transform(html.render())
# display(styler)
# Iterate over one or more given columns
# only from the dataframe
for column in pred[["anomaly"]]:
    # Select column contents by column
    # name using [] operator
    columnSeriesObj = pred["anomaly"]
    if columnSeriesObj.values == -1 or columnSeriesObj.values == 1:
        send_email(styler)
        print("Column Contents : ", columnSeriesObj.values)
    else:
        print("Its not an anomaly")
        pass
