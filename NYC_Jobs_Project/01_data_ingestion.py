import pandas as pd
from sqlalchemy import create_engine

file_path = r"D:\Data analysis\Datasets\NYC Jobs\Data\NYC_Jobs.csv"
df = pd.read_csv(file_path)

df.columns = [c.replace(' ', '_') for c in df.columns]

username = "root"
password = ""
host = "localhost"
db_name = "NYC_Jobs"

engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{db_name}')

df.to_sql('nyc_jobs_raw', con=engine, if_exists='replace', index=False)

print("Done")