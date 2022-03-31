import pandas as pd
from datetime import date
import PyPDF2
from pdfminer.high_level import extract_text

attendance_start = date(2021,7,26)

ss = pd.read_csv('sessions.csv',dtype=str)
ss.date = pd.to_datetime(ss.date).dt.date
ss = ss[ss.date >= attendance_start]
sessions = ss.session.tolist()
session_date = dict(zip(ss.session,ss.date))

mp = pd.read_csv('mp_2021-07-26.csv',usecols=['seat_code','seat','mp'])
mp['seat_search'] = ['(' + ''.join(x.split()).lower() + ')' for x in mp.seat.tolist()]

df = pd.DataFrame(columns=['date'] + mp.seat_code.tolist())

# Strategy
# Step 1: Use the phrase "Senarai Kehadiran" to find the page where the present list starts
# Step 2: Use the phrase "Tidak Hadir" to find the page where the absent list starts
# Step 3: Extract text from these pages, join, and remove anything after the "tidak hadir" phrase
# Step 4: Encode everyone as absent; encode as present if in string from Step 3

def attendedSession(seat,string): return 1 if seat in string else 0

# for s in sessions:
for s in ['14-05-01-04']:
    print(s)
    pdf_active = PyPDF2.PdfFileReader(open('src_hansard/hansard_' + s + '.pdf', 'rb', ),strict=False)
    n_pages = pdf_active.numPages
    extract_start = 0
    start_set = 0
    extract_end = 0
    end_hook = ''
    for i in range(n_pages):
        page_active = ''.join(pdf_active.getPage(i).extractText().split()).lower()
        if start_set == 0 and 'ahliyangtidakhadir' in page_active:
            extract_start = i
            start_set = 1 # ensure first instance is taken and frozen
        if 'senatoryangtidakhadir' in page_active or 'dewanrakyat' in page_active:
            extract_end = i
            end_hook = 'senatoryangtidakhadir' if 'senatoryangtidakhadir' in page_active else 'dewanrakyat'
        if extract_start > 0 and extract_end > 0: break # break the moment we find the end of the section

    res = extract_text('src_hansard/hansard_' + s + '.pdf',page_numbers=[x for x in range(extract_start,extract_end+1)])
    res = ''.join(res.split()).lower()
    res = res.split('ahliyangtidakhadir',1)[1]
    res = res.split(end_hook,1)[0]
    res = res.replace('(johorbaru)','(johorbahru)')

    attendance = [attendedSession(x,res) for x in mp.seat_search.tolist()]
    df.loc[len(df)] = [session_date[s]] + attendance

df = df.set_index('date').transpose()
df['total'] = df.sum(axis=1)
session_dates = list(df.columns)
df = df.reset_index().rename(columns={'index':'seat_code'})
df = pd.merge(df,mp,on=['seat_code'],how='left')
df = df[['seat_code','seat','mp'] + session_dates]
df.to_csv('absence.csv',index=False)