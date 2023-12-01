import sqlite3
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model for encoding text chunks
# model = SentenceTransformer("thenlper/gte-large")

# # Dimensions for the vector embeddings (adjust based on model's output)
# VEC_INDEX_DIM = 1024

model = SentenceTransformer("all-MiniLM-L6-v2")

# Dimensions for the vector embeddings (adjust based on model's output)
VEC_INDEX_DIM = 384


# Initialize the Annoy index for storing and searching vectors
vec_index = AnnoyIndex(VEC_INDEX_DIM, 'angular')

# Connect to the SQLite database
conn = sqlite3.connect('my_chunks2.db')
cursor = conn.cursor()


# Fetch a batch of rows based on the offset and limit
# cursor.execute(f"SELECT chunk_id, chunk_text FROM chunks_fact")
# rows = cursor.fetchall()
offset=0
limit=100
print(offset)
while True:
    cursor.execute(f"SELECT chunk_id, chunk_text FROM chunks_fact LIMIT {limit} OFFSET {offset}")
    rows = cursor.fetchall()
    if not rows:
        break
    # For each row in the batch, extract the text chunk, encode it, and add it to the Annoy index
    for row in rows:
        chunk_id = row[0]
        chunk_text = row[1]
        embeddings = model.encode(str(chunk_text))
        vec_index.add_item(chunk_id, embeddings)          

    offset+=limit
    print(offset)

# Close the SQLite database connection
conn.close()

# Build the Annoy index for efficient querying
vec_index.build(100) #100 specifies number of trees to build

# Save the built index to a file for future use
vec_index.save("./vecindex.ann")


