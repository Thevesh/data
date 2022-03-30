import urllib.request
import pandas as pd
import time

df = pd.read_csv('sessions.csv',parse_dates=['date'])
df.date = df.date.dt.date
sessions = df.session.tolist()
session_date = dict(zip(df.session,df.date))

for s in sessions:
    print(s)
    tdate = session_date[s].strftime('%d%m%Y')
    url_hansard = 'https://www.parlimen.gov.my/files/hindex/pdf/DR-' + tdate +  '.pdf'
    urllib.request.urlretrieve(url_hansard, 'src_hansard/hansard_' + s + '.pdf')
    time.sleep(10)