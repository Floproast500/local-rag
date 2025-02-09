import streamlit as st
import requests

def main():
    st.set_page_config(page_title="Document Embed & Query App", layout="centered")
    st.title("Document Embedding & Query Interface")

    # Tabs for different functionalities
    tab1, tab2 = st.tabs(["Embed Document", "Query Database"])

    # Embed Document Tab
    with tab1:
        st.header("Upload a Document to Embed")
        file = st.file_uploader("Upload a PDF file", type="pdf")
        
        if file is not None:
            if st.button("Embed File"):
                with st.spinner("Embedding file..."):
                    files = {'file': file}
                    response = requests.post("http://localhost:8080/embed", files=files)
                    
                    if response.status_code == 200:
                        st.success("File embedded successfully!")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Something went wrong')}")

    # Query Database Tab
    with tab2:
        st.header("Query the Embedded Data")
        query_input = st.text_input("Enter your query")
        
        if query_input:
            if st.button("Submit Query"):
                with st.spinner("Querying database..."):
                    response = requests.post(
                        "http://localhost:8080/query",
                        json={"query": query_input}
                    )
                    
                    if response.status_code == 200:
                        st.success("Query successful!")
                        st.write(response.json().get("message", "No response"))
                    else:
                        st.error(f"Error: {response.json().get('error', 'Something went wrong')}")

if __name__ == "__main__":
    main()
