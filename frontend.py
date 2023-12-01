# streamlit_app.py

import streamlit as st
import requests
import urllib.parse
from io import BytesIO
from PIL import Image

backend_url = "http://localhost:8000"
base_url = "http://localhost:8000"

def display_pdf_page_as_image(pdf_url, page_number):
    # Download the PDF file from the backend URL
    pdf_response = requests.get(pdf_url)

    if pdf_response.status_code == 200:
        # ... (same as your existing code)
        return image
    else:
        return None

st.title("CourtDoc Navigator 🔎")

query = st.text_input("Enter your query:")

# ...
if st.button("Search"):
    if query:
        # Make a GET request to the FastAPI backend
        response = requests.get(backend_url + "/find_similar_text/", params={"query_text": query})

        if response.status_code == 200:
            similar_chunks = response.json()
            if similar_chunks:
                st.subheader("Similar Chunks:")
                for idx, chunk in enumerate(similar_chunks, 1):
                    # ... (same as your existing code)

                    # Move page_number declaration outside the loop
                    page_number = chunk["page_number"]

                    # Move pdf_filename declaration outside the loop
                    pdf_filename = chunk["document_file_name"]

                    # Create a clickable link to the PDF document with the page number
                    pdf_link = f"{base_url}/pdfs/{urllib.parse.quote(pdf_filename)}#page={page_number}"
                    st.write(f"View PDF: [Open PDF]({pdf_link})")

                    pdf_url = f"{base_url}/pdfs/{urllib.parse.quote(pdf_filename)}"

                    image_link = f"{base_url}/pdf_image/{urllib.parse.quote(pdf_filename)}/{page_number}"
                    st.markdown(f"Preview: [View]({image_link})")

                    # Add a button to fetch and display the document summary
                    button_key = f"summarize_document_{idx}"
                    if st.button("Summarize Document", key=button_key):
                        summary_request = {"filepath": pdf_filename}
                        summary_response = requests.post(backend_url + "/summarize_document/", json=summary_request)

                        if summary_response.status_code == 200:
                            summary_text = summary_response.json()["summary"]
                            st.success(f"Document Summary:\n{summary_text}")
                        else:
                            st.error("Error fetching document summary.")
                    
                    st.markdown("---")  # Add a horizontal line to separate cards
            else:
                st.write("No similar chunks found.")
        else:
            st.write("Error connecting to the backend.")
    else:
        st.write("Please enter a query.")