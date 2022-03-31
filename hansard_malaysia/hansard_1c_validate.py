import pandas as pd
from tabulate import tabulate

empty_seats = ['P054','P185']

at = pd.read_csv('attendance.csv')
ab = pd.read_csv('absence.csv')
assert len(at.columns) == len(ab.columns), 'Dataframes are not of equal width'
n_sessions = len(at.columns) - 4

col_summary = ['seat_code','seat','mp','total']
df = pd.merge(at[col_summary],
              ab[col_summary],
              on=col_summary[:3],how='left').rename(columns={'total_x':'present','total_y':'absent'})
df['total'] = df.present + df.absent
df.mp = df.mp.fillna('')
df = df[~df.seat_code.isin(empty_seats)]

print('\nTotal: ' + str(n_sessions) + ' sessions\n\nTabulations for these MPs are problematic')
print('\n' + tabulate(df[df.total != n_sessions], headers='keys', tablefmt='psql', showindex=False))

dt = (at.set_index(col_summary[:3]) + ab.set_index(col_summary[:3])).reset_index()
dt.drop(['seat','mp'],axis=1,inplace=True)
dt = dt[(dt.total != n_sessions) & (~dt.seat_code.isin(empty_seats))].set_index('seat_code').transpose()[:-1]
dt['total'] = dt.sum(axis=1)
dt = dt[dt.total != len(dt.columns) - 1].transpose().reset_index()[:-1]
print('\n' + tabulate(dt, headers='keys', tablefmt='psql', showindex=False))