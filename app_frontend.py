import streamlit as st
import requests
import pandas as pd
import io

from rotating_user_agent import fetch_sitemap_urls, fetch_page_content

def main():
    st.set_page_config(page_title="Document Embed & Query App", layout="centered")
    st.title("Document Embedding & Query Interface")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Embed Document", 
        "Query Database", 
        "NO RAG Chat", 
        "Sitemap Scraper"
    ])

    # ----------------------------------------------------------------
    # (1) Embed Document Tab
    # ----------------------------------------------------------------
    with tab1:
        st.header("Upload a Document to Embed")
        st.write("Accepted file types: pdf, docx, txt, md, etc.")
        file = st.file_uploader("Upload a file", type=["pdf","docx","txt","md"])
        
        if file is not None:
            if st.button("Embed File"):
                with st.spinner("Embedding file..."):
                    files = {'file': file}
                    response = requests.post("http://localhost:8080/embed", files=files)
                    try:
                        data = response.json()
                        if response.status_code == 200:
                            st.success(data.get("message", "File embedded successfully!"))
                        else:
                            st.error(f"Error: {data.get('error', 'Something went wrong')}")
                    except requests.exceptions.JSONDecodeError:
                        st.error("Server returned non-JSON response.")
                        st.write("Raw response text:")
                        st.write(response.text)

    # ----------------------------------------------------------------
    # (2) Query Database Tab
    # ----------------------------------------------------------------
    with tab2:
        st.header("Query the Embedded Data")

        # Load doc lists: pdfDocs, scrapedDomains
        with st.spinner("Loading available documents..."):
            try:
                doc_resp = requests.get("http://localhost:8080/list_documents")
                if doc_resp.status_code == 200:
                    # Parse the JSON response
                    docs_data = doc_resp.json()
                    # DEBUG: Show the raw data from the endpoint
                    st.write("DEBUG: response from /list_documents:")
                    st.write(docs_data)

                    pdf_docs = docs_data.get("pdfDocs", [])
                    scraped_domains = docs_data.get("scrapedDomains", [])

                    # DEBUG: Show the parsed lists
                    st.write("DEBUG: pdf_docs =", pdf_docs)
                    st.write("DEBUG: scraped_domains =", scraped_domains)

                else:
                    st.error("Could not fetch documents.")
                    pdf_docs = []
                    scraped_domains = []
            except Exception as e:
                st.error(f"Error fetching documents: {e}")
                pdf_docs = []
                scraped_domains = []

        # Build a combined list:
        # "All Documents", "PDF: <filename>", "Scraped Domain: <domain>"
        doc_options = ["All Documents"]
        for pdf_name in pdf_docs:
            doc_options.append(f"PDF: {pdf_name}")
        for domain in scraped_domains:
            doc_options.append(f"Scraped Domain: {domain}")

        selected_doc = st.selectbox("Select a document or domain", doc_options)
        query_input = st.text_input("Enter your query")

        if st.button("Submit Query"):
            if query_input.strip():
                with st.spinner("Querying database..."):
                    payload = {"query": query_input}

                    # Determine doc_type & doc_name
                    if selected_doc == "All Documents":
                        pass
                    elif selected_doc.startswith("PDF: "):
                        doc_name = selected_doc.replace("PDF: ", "")
                        payload["doc_type"] = "pdf"
                        payload["doc_name"] = doc_name
                    elif selected_doc.startswith("Scraped Domain: "):
                        domain_name = selected_doc.replace("Scraped Domain: ", "")
                        payload["doc_type"] = "scraped_domain"
                        payload["doc_name"] = domain_name

                    response = requests.post("http://localhost:8080/query", json=payload)
                    try:
                        data = response.json()
                        if response.status_code == 200:
                            st.success("Query successful!")
                            st.write(data.get("message", "No response"))
                        else:
                            st.error(f"Error: {data.get('error', 'Something went wrong')}")
                    except requests.exceptions.JSONDecodeError:
                        st.error("Server returned non-JSON response.")
                        st.write("Raw response text:")
                        st.write(response.text)
            else:
                st.warning("Please enter a query before submitting.")

    # ----------------------------------------------------------------
    # (3) NO RAG Chat Tab
    # ----------------------------------------------------------------
    with tab3:
        st.header("NO RAG Chat - Direct Model Conversation")
        no_rag_input = st.text_area("Enter your message here", "")

        if st.button("Send to Model"):
            if no_rag_input.strip():
                with st.spinner("Talking to the model (NO RAG mode)..."):
                    response = requests.post(
                        "http://localhost:8080/no_rag_query",
                        json={"prompt": no_rag_input}
                    )
                    try:
                        data = response.json()
                        if response.status_code == 200:
                            st.success("Model responded:")
                            st.write(data.get("message", "No response"))
                        else:
                            st.error(f"Error: {data.get('error', 'Something went wrong')}")
                    except requests.exceptions.JSONDecodeError:
                        st.error("Server returned non-JSON response.")
                        st.write("Raw response text:")
                        st.write(response.text)
            else:
                st.warning("Please enter a message before sending.")

    # ----------------------------------------------------------------
    # (4) Sitemap Scraper Tab
    # ----------------------------------------------------------------
    with tab4:
        st.header("Sitemap Scraper")
        st.write("This scraper will handle sitemap indexes (like Yoast) and normal sitemaps, "
                 "rotating user agents to avoid 403 blocks.")
        sitemap_url = st.text_input("Enter the sitemap URL (e.g., https://example.com/sitemap_index.xml)")

        if "scraped_df" not in st.session_state:
            st.session_state["scraped_df"] = None

        if st.button("Scrape Sitemap"):
            if sitemap_url.strip():
                with st.spinner("Recursively parsing sitemap..."):
                    all_page_urls = fetch_sitemap_urls(sitemap_url.strip())

                if not all_page_urls:
                    st.warning("No pages found in the sitemap.")
                else:
                    rows = []
                    with st.spinner(f"Scraping {len(all_page_urls)} pages with rotating user agents..."):
                        for i, page_url in enumerate(all_page_urls, start=1):
                            st.write(f"Scraping {i}/{len(all_page_urls)}: {page_url}")
                            content = fetch_page_content(page_url)
                            if content:
                                rows.append((page_url, content))
                            else:
                                st.error(f"Failed or empty content for {page_url}")

                    if rows:
                        df = pd.DataFrame(rows, columns=["URL", "Content"])
                        st.session_state["scraped_df"] = df
                        st.success(f"Scraped {len(rows)} pages. Preview below:")
                        st.dataframe(df.head(5))
                    else:
                        st.warning("No content scraped.")
            else:
                st.warning("Please enter a valid sitemap URL.")

        # Button to embed the CSV data
        if st.session_state["scraped_df"] is not None:
            if st.button("Embed CSV"):
                df = st.session_state["scraped_df"]
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_text = csv_buffer.getvalue()

                with st.spinner("Embedding CSV into the vector store..."):
                    try:
                        embed_resp = requests.post(
                            "http://localhost:8080/embed_csv",
                            data=csv_text.encode("utf-8")  
                        )
                        if embed_resp.status_code == 200:
                            st.success(embed_resp.json().get("message", "Embedding successful!"))
                        else:
                            st.error(embed_resp.json().get("error", "Error embedding CSV data."))
                    except Exception as e:
                        st.error(f"Error sending CSV to /embed_csv: {e}")

            # Also let the user download the CSV
            if st.button("Download CSV"):
                df = st.session_state["scraped_df"]
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download Scraped CSV",
                    data=csv_data,
                    file_name="sitemap_scrape.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()