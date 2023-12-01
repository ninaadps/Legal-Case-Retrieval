# main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict
from annoy import AnnoyIndex
import sqlite3
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

app = FastAPI()

# Load Sentence Transformer Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load Annoy Index
VEC_INDEX_DIM = 384
vec_index = AnnoyIndex(VEC_INDEX_DIM, 'angular')
vec_index.load("./vecindex.ann")

# SQLite connection
conn = sqlite3.connect("my_chunks2.db")
cursor = conn.cursor()

class QueryText(BaseModel):
    query_text: str

@app.get("/find_similar_text/", response_model=List[Dict[str, str]])
async def find_similar_text(query_text: str = Query(...)):
    """
    Given a query_text, find the top 10 text chunks from the database that are semantically similar.
    """
    try:
        # Convert the query text into an embedding
        embedding = model.encode([query_text])
        input_vec = embedding[0]

        # Retrieve the IDs of the top 10 most similar text chunks
        chunk_ids = vec_index.get_nns_by_vector(input_vec, 10, search_k=-1, include_distances=False)

        # Fetch the actual text chunks from the SQLite database
        list_chunk_ids = ','.join(map(str, chunk_ids))
        cursor.execute(
            "SELECT chunk_id, chunk_text, page_number, document_file_name FROM chunks_fact WHERE chunk_id IN (" + list_chunk_ids + ")"
        )
        res = cursor.fetchall()

        # Construct the result list
        result = [{"chunk_text": chunk[1], "page_number": str(chunk[2]), "document_file_name": chunk[3]} for chunk in res]
        return result
    except Exception as e:
        return HTTPException(detail=f"Error: {e}", status_code=500)

class SummaryRequest(BaseModel):
    filepath: str

@app.post("/summarize_document/")
async def summarize_document(request: SummaryRequest):
    """
    Given a filepath, summarize the document and return the summary.
    """
    try:
        filepath = request.filepath
        cursor.execute(
            "SELECT chunk_text FROM chunks_fact WHERE document_file_name = ?",
            (filepath,)
        )
        document_text = "\n".join(chunk[0] for chunk in cursor.fetchall())

        # Your summarization logic here
        # ...

        summary = "This is a sample summary. Replace this with your actual summarization logic."

        return {"summary": summary}
    except Exception as e:
        return HTTPException(detail=f"Error: {e}", status_code=500)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
