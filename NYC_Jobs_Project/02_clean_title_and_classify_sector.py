import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


username = "root"
password = ""
host = "localhost"
db_name = "NYC_Jobs"

engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{db_name}')

df = pd.read_sql('SELECT * FROM nyc_jobs_raw', con=engine) 





import spacy
nlp = spacy.load('en_core_web_sm')

def clean_title(title):
    normalized = title.lower()
    doc = nlp(normalized)
    tokens = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    return ' '.join(tokens)

df['Clean_Title'] = df['Business_Title'].apply(clean_title)


# -------------------------------------------------

# -------------------------------------------------

# 1. تحميل النموذج أوفلاين
model = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)

# 2. القطاعات
candidate_labels = [
    'Software & Technology', 
    'Finance & Banking', 
    'Healthcare & Medicine', 
    'Education & Training', 
    'Project & Operations Management',
    'Customer Support & Administration',
    'Human Resources',
    'Marketing & Sales'
]

# حساب الـ Embeddings للقطاعات مرة واحدة
label_embeddings = model.encode(candidate_labels)

def classify_job(row):
    title = str(row['Clean_Title'])
    desc = str(row['Job_Description'])[:300] if pd.notna(row['Job_Description']) else ""
    
    
    title_emb = model.encode([title])
    desc_emb = model.encode([desc]) if desc else title_emb
    
    
    sim_title = cosine_similarity(title_emb, label_embeddings)[0]
    sim_desc = cosine_similarity(desc_emb, label_embeddings)[0]
    
  
    final_sims = (0.7 * sim_title) + (0.3 * sim_desc)
    
    best_idx = np.argmax(final_sims)
    return candidate_labels[best_idx]

df['Sector'] = df.apply(classify_job, axis=1)



selected_columns = [
    'Clean_Title', 
    'Sector', 
    'Post_Until', 
    'Salary_Frequency', 
    'Salary_Range_From', 
    'Salary_Range_To', 
    'Level'
]

df = df[selected_columns]


df.rename(columns={'Salary_Frequency': 'Pay_Type'}, inplace=True)

df['Post_Until'] = pd.to_datetime(df['Post_Until'],format='mixed').dt.date

def clean_level_en(val):
    if pd.isna(val):
        return 'Unspecified'
    
    val_str = str(val).strip().upper()
    
    # Entry-Level
    if val_str in ['00', '01', '02', '1', '2', 'ENTRY']:
        return 'Entry-Level'
    
    # Mid-Level
    elif val_str in ['03', '04', '3', '4', 'MID']:
        return 'Mid-Level'
    
    # Senior / Executive
    elif any(char in val_str for char in ['05', '06', 'M', 'M1', 'M2', 'M3', 'M4', 'M5', 'EXECUTIVE', 'SENIOR']):
        return 'Senior'
    
    else:
        return 'Mid-Level'
    
# تطبيق التعديل على عمود Level
df['Level'] = df['Level'].apply(clean_level_en)


df.to_sql('nyc_jobs_cleaned', con=engine, if_exists='replace', index=False)


