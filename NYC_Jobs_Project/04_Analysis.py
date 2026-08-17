import pandas as pd
import numpy as np
from sqlalchemy import create_engine

username = "root"
password = ""
host = "localhost"
db_name = 'NYC_Jobs'

engine =create_engine(f'mysql+pymysql://{username}:{password}@{host}/{db_name}')

df= pd.read_sql('SELECT * FROM nyc_jobs_cleaned', con=engine) 




# Filter out Hourly/Daily to avoid salary calculation errors
df_annual = df[df['Pay_Type'].str.strip().str.title() == 'Annual'].copy()


# 1. Salary Flexibility Percentage (Avoid Division by Zero)
df_annual['Salary_Flexibility_Pct'] = np.where(
    df_annual['Avg_Salary'] > 0, ((df_annual['Salary_Range_To'] - df_annual['Salary_Range_From']) / df_annual['Avg_Salary'])* 100,0,)

# 2. Executive Flag (True / False)
exec_keywords = ['director', 'chief', 'manager', 'head', 'commissioner']
df_annual['Is_Executive'] = df_annual['Clean_Title'].str.contains(
    '|'.join(exec_keywords), case=False, na=False
)

# 3. Days Remaining to Apply
df_annual['Post_Until'] = pd.to_datetime(
    df_annual['Post_Until'], errors='coerce'
)
today = pd.to_datetime('today')
df_annual['Days_To_Apply'] = (df_annual['Post_Until'] - today).dt.days



# Summary 1: Sector Performance
sector_summary = (
    df_annual.groupby('Sector')
    .agg(
        Total_Jobs=('Clean_Title', 'count'),
        Mean_Salary=('Avg_Salary', 'mean'),
        Avg_Flexibility_Pct=('Salary_Flexibility_Pct', 'mean'),
    )
    .reset_index()
    .sort_values('Mean_Salary', ascending=False)
)

sector_summary['Avg_Flexibility_Pct'] = sector_summary[
    'Avg_Flexibility_Pct'
].apply(lambda x: f'{x:.2f}%')
sector_summary['Mean_Salary'] = sector_summary['Mean_Salary'].apply(
    lambda x: f'${x:,.2f}'
)

# Summary 2: Job Level Performance
level_summary = (
    df_annual.groupby('Level')
    .agg(
        Total_Jobs=('Clean_Title', 'count'), Mean_Salary=('Avg_Salary', 'mean')
    )
    .reset_index()
    .sort_values('Mean_Salary', ascending=False)
)

# Summary 3: Executive vs Non-Executive Salaries
exec_summary = (
    df_annual.groupby('Is_Executive')
    .agg(
        Total_Jobs=('Clean_Title', 'count'), Mean_Salary=('Avg_Salary', 'mean')
    )
    .reset_index()
)



print('=== 1. SECTOR SUMMARY (ANNUAL PAY ONLY) ===')
print(sector_summary.to_string(index=False))

print('\n=== 2. LEVEL SUMMARY (ANNUAL PAY ONLY) ===')
print(level_summary.to_string(index=False))

print('\n=== 3. EXECUTIVE VS NON-EXECUTIVE (ANNUAL PAY ONLY) ===')
print(exec_summary.to_string(index=False))


# ==========================================
# Top 10 Most In-Demand Jobs Analysis
# ==========================================

# 1. Group by Clean_Title and count total postings
top_jobs = (
    df_annual.groupby('Clean_Title')
    .agg(
        Total_Postings=('Clean_Title', 'count'),
        Mean_Salary=('Avg_Salary', 'mean'),
    )
    .reset_index()
    .sort_values('Total_Postings', ascending=False)
    .head(10)
)

# 2. Format salary column for display
top_jobs['Mean_Salary'] = top_jobs['Mean_Salary'].apply(lambda x: f'${x:,.2f}')

# 3. Print output
print('=== TOP 10 MOST IN-DEMAND JOBS ===')
print(top_jobs.to_string(index=False))






# ==========================================
# Data Analytics Jobs Demand Analysis
# ==========================================

# 1. Define keywords for Data roles
data_keywords = [
    'data analyst',
    'data analytics',
    'data scientist',
    'business intelligence',
    'data specialist',
    'database',
]

# 2. Filter dataset for Data-related titles
df_data = df_annual[
    df_annual['Clean_Title'].str.contains(
        '|'.join(data_keywords), case=False, na=False
    )
].copy()

# 3. Calculate Overall Metrics
total_data_postings = len(df_data)
pct_of_all_jobs = (total_data_postings / len(df_annual)) * 100
overall_avg_salary = df_data['Avg_Salary'].mean()

# 4. Summary by Specific Data Titles
data_titles_summary = (
    df_data.groupby('Clean_Title')
    .agg(
        Total_Postings=('Clean_Title', 'count'),
        Mean_Salary=('Avg_Salary', 'mean'),
    )
    .reset_index()
    .sort_values('Total_Postings', ascending=False)
)

# 5. Summary by Sectors hiring Data roles
data_sectors_summary = (
    df_data.groupby('Sector')
    .agg(
        Total_Postings=('Clean_Title', 'count'),
        Mean_Salary=('Avg_Salary', 'mean'),
    )
    .reset_index()
    .sort_values('Total_Postings', ascending=False)
)

# 6. Format Salary columns for clean display
data_titles_summary['Mean_Salary'] = data_titles_summary['Mean_Salary'].apply(
    lambda x: f'${x:,.2f}'
)
data_sectors_summary['Mean_Salary'] = data_sectors_summary[
    'Mean_Salary'
].apply(lambda x: f'${x:,.2f}')


# ==========================================
# Terminal Output
# ==========================================

print('=== DATA JOBS OVERALL METRICS ===')
print(f'Total Data Postings: {total_data_postings}')
print(f'Percentage of Total Dataset: {pct_of_all_jobs:.2f}%')
print(f'Average Salary for Data Roles: ${overall_avg_salary:,.2f}')

print('\n=== BREAKDOWN BY JOB TITLE ===')
print(data_titles_summary.to_string(index=False))

print('\n=== SECTORS HIRING DATA ROLES ===')
print(data_sectors_summary.to_string(index=False))
print(f'Total Data Postings: {sum(data_sectors_summary["Total_Postings"])}')




# ==========================================
# Data Roles Salary Analysis by Job Level
# ==========================================

# 1. Group Data jobs by Level and calculate average salary
data_level_summary = (
    df_data.groupby('Level')
    .agg(
        Total_Postings=('Clean_Title', 'count'),
        Mean_Salary=('Avg_Salary', 'mean'),
    )
    .reset_index()
    .sort_values('Mean_Salary', ascending=False)
)

# 2. Format salary column for clean terminal display
data_level_summary['Mean_Salary'] = data_level_summary['Mean_Salary'].apply(
    lambda x: f'${x:,.2f}'
)

# 3. Print the result
print('=== DATA ROLES AVERAGE SALARY BY LEVEL ===')
print(data_level_summary.to_string(index=False))

print(len(df))





