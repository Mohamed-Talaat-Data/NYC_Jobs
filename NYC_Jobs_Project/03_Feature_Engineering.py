import pandas as pd
import numpy as np
from sqlalchemy import create_engine

username = "root"
password = ""
host = "localhost"
db_name = 'NYC_Jobs'

engine =create_engine(f'mysql+pymysql://{username}:{password}@{host}/{db_name}')

df= pd.read_sql('SELECT * FROM nyc_jobs_cleaned', con=engine) 

df['Clean_Title'] = df['Clean_Title'].astype(str).str.strip()


invalid_values = ['',' ','nan','NaN','NAN','null','Null','NULL','None','NONE','none','n/a','N/A','unknown','UNKNOWN','blank','BLANK',]
df['Clean_Title'] = df['Clean_Title'].replace(invalid_values, np.nan)

# 3. حذف الصفوف الفارغة مباشرة
df = df.dropna(subset=['Clean_Title'])



df['Avg_Salary'] = (df['Salary_Range_From'] + df['Salary_Range_To']) / 2

df.to_sql('nyc_jobs_cleaned', con=engine, if_exists='replace', index=False)

df_annual = df[df['Pay_Type'] == 'Annual']
df_Hourly = df[df['Pay_Type'] == 'Hourly']
df_Daily = df[df['Pay_Type'] == 'Daily']


df_unique_annual = df_annual.sort_values(
    'Avg_Salary', ascending=False
).drop_duplicates(subset=['Clean_Title'])


top_10_jobs = df_unique_annual.nlargest(10, 'Avg_Salary')[
    ['Clean_Title', 'Sector', 'Avg_Salary']
]

print('Top 10 jobs')
print(top_10_jobs)

print(100 * '~')

print(100 * '~')



# 1. تصفية وظائف Data Analyst، مسح التكرارات، ثم الترتيب تنازلياً
data_analyst_df = (
    df[df['Clean_Title'].str.contains('Data Analyst', case=False, na=False)]
    .drop_duplicates(subset=['Avg_Salary', 'Sector'])
    .sort_values('Avg_Salary', ascending=False)
)


print(data_analyst_df[['Clean_Title', 'Avg_Salary', 'Sector']])

print(len(df))