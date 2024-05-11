import pandas as pd
import numpy as np
import tiktoken
import psycopg2
import math
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from transformers import AutoTokenizer, AutoModel


def process_csv_and_create_embeddings_table():
    tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-large")
    model = AutoModel.from_pretrained("thenlper/gte-large")

    def get_gte_large_embeddings(text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return embeddings

    df = pd.read_csv('./news_headlines.csv', delimiter=',', quotechar='"')
    df.head()

    def num_tokens_from_string(string: str, encoding_name = "cl100k_base") -> int:
        if not string:
            return 0
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    new_list = []
    for i in range(len(df.index)):
        text = df['article'][i]
        token_len = num_tokens_from_string(text)
        if token_len <= 512:
            new_list.append([df['title'][i], df['url'][i], df['category'][i], df['article'][i], token_len])
        else:
            start = 0
            ideal_token_size = 512
            ideal_size = int(ideal_token_size // (4/3))
            end = ideal_size
            words = text.split()
            words = [x for x in words if x != ' ']
            total_words = len(words)            
            chunks = total_words // ideal_size
            if total_words % ideal_size != 0:
                chunks += 1
            new_content = []
            for j in range(chunks):
                if end > total_words:
                    end = total_words
                new_content = words[start:end]
                new_content_string = ' '.join(new_content)
                new_content_token_len = num_tokens_from_string(new_content_string)
                if new_content_token_len > 0:
                    new_list.append([df['title'][i], df['url'][i], df['category'][i], new_content_string, new_content_token_len])
                start += ideal_size
                end += ideal_size

    for i in range(len(new_list)):
        text = new_list[i][3]
        embedding = get_gte_large_embeddings(text)
        new_list[i].append(embedding.flatten().tolist())

    df_new = pd.DataFrame(new_list, columns=['title', 'url', 'category', 'article', 'tokens', 'embeddings'])
    df_new.head()

    df_new.to_csv('./news_headlines_embeddings.csv', index=False)

    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="m1n1g3r1t",
        host="localhost"
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
    """)
    conn.commit()

    register_vector(conn)

    table_create_command = """
        CREATE TABLE news_headlines (
            id BIGSERIAL PRIMARY KEY,
            title TEXT,
            url TEXT,
            category Text,
            article Text,
            tokens INTEGER,
            embeddings VECTOR(1024),
            );
                """

    cur.execute(table_create_command)
    cur.close()
    conn.commit()

    register_vector(conn)
    cur = conn.cursor()
    data_list = [(row['title'], row['url'], row['category'], row['article'], int(row['tokens']),  np.array(row['embeddings'])) for index, row in df_new.iterrows()]

    try:
        print("trying insertion")
        execute_values(cur, """
            INSERT INTO news_headlines (title, url, category, article, tokens, embeddings) 
            VALUES %s""", data_list)
        conn.commit()
    except Exception as e:
        print(f"An error occurred during insertion: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

    cur.execute("SELEC COUNT(*) as cnt FROM news_headlines;")
    num_records = cur.fetchone()[0]
    print("Number of vector records in table: ", num_records,"\n")

    cur.execute("SELECT * FROM news_headlines LIMIT 1;")
    records = cur.fetchall()
    print("First record in table: ", records)
    
    num_lists = num_records / 1000
    if num_lists < 10:
        num_lists = 10
    if num_records > 1000000:
        num_lists = math.sqrt(num_records)

    cur.execute(f'CREATE INDEX ON news_headlines USING ivfflat (embeddings vector_cosine_ops) WITH (lists = {num_lists});')
    conn.commit()
    cur.close()
    conn.close()

process_csv_and_create_embeddings_table()