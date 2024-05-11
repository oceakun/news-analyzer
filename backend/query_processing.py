import psycopg2
import numpy as np
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from transformers import AutoTokenizer, AutoModel

def retrieve_similar_content(query):
    def get_top_similar_docs(query_embedding):
        conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="m1n1g3r1t",
        host="localhost"
            )
        embedding_array = np.array(query_embedding)
        register_vector(conn)
        cur = conn.cursor()
        cur.execute("SELECT title,url, category,article FROM news_headlines ORDER BY embeddings <-> %s::vector LIMIT 10", (embedding_array,))
        top3_docs = cur.fetchall()
        return top3_docs

    def get_gte_large_embeddings(text):
            tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-large")
            model = AutoModel.from_pretrained("thenlper/gte-large")
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
            embedding_1d = embeddings.flatten()
            return embedding_1d
    
    return get_top_similar_docs(get_gte_large_embeddings(query))
