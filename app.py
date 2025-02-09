import os
import io
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embed import embed_any_file
from query import query
from get_vector_db import get_vector_db

from langchain.schema import HumanMessage
from langchain_community.chat_models import ChatOllama

app = Flask(__name__)

@app.route('/embed', methods=['POST'])
def route_embed():
    """Embed a file (pdf, docx, txt, md, etc.) into the vector database."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        embedded = embed_any_file(file)
        if embedded:
            return jsonify({"message": "File embedded successfully"}), 200
        else:
            return jsonify({"error": "File embedding failed"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list_documents', methods=['GET'])
def list_documents():
    """
    Return a unified list of docs from the vector store:
      - PDFs / file-based docs have metadata['filename'].
      - Scraped domain-based docs have metadata['domain'].
    We'll return two lists: 'pdfDocs' and 'scrapedDomains'.
    """
    try:
        db = get_vector_db()
        raw = db._collection.get()
        all_metadata = raw.get("metadatas", [])

        pdf_docs = set()
        scraped_domains = set()

        for meta in all_metadata:
            if "filename" in meta:
                pdf_docs.add(meta["filename"])
            elif "domain" in meta:
                scraped_domains.add(meta["domain"])

        return jsonify({
            "pdfDocs": sorted(list(pdf_docs)),
            "scrapedDomains": sorted(list(scraped_domains))
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def route_query():
    """
    RAG query over the vector store.
    JSON body can include:
      {
        "query": "...",
        "doc_type": "pdf" or "scraped_domain",
        "doc_name": "my.pdf or example.com"
      }
    or nothing => "All Documents".
    """
    data = request.get_json()
    user_query = data.get('query', '').strip()
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    doc_type = data.get('doc_type')  # "pdf" or "scraped_domain"
    doc_name = data.get('doc_name')

    try:
        response = query(user_query, doc_type=doc_type, doc_name=doc_name)
        if response:
            return jsonify({"message": response}), 200
        else:
            return jsonify({"error": "Something went wrong"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/no_rag_query', methods=['POST'])
def route_no_rag_query():
    """Directly query the LLM (NO RAG)."""
    data = request.get_json()
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    model_name = os.getenv('LLM_MODEL', 'mistral')
    llm = ChatOllama(model=model_name)

    try:
        messages = [HumanMessage(content=prompt)]
        response = llm(messages)
        return jsonify({"message": response.content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/embed_csv', methods=['POST'])
def route_embed_csv():
    """
    Embed CSV data with columns 'URL' and 'Content' into the vector store.
    Each row is chunked => metadata={"url": row["URL"], "domain": <parsed domain>}.
    """
    from urllib.parse import urlparse

    try:
        csv_text = request.data.decode("utf-8", errors="replace")
        if not csv_text.strip():
            return jsonify({"error": "No CSV data provided"}), 400

        df = pd.read_csv(io.StringIO(csv_text))
        if "URL" not in df.columns or "Content" not in df.columns:
            return jsonify({"error": "CSV must have 'URL' and 'Content' columns"}), 400

        db = get_vector_db()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        docs_to_add = []

        for _, row in df.iterrows():
            url = str(row["URL"])
            content = str(row["Content"])

            # parse domain from the URL
            parsed = urlparse(url)
            domain = parsed.netloc  # e.g. "example.com"

            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                doc = Document(
                    page_content=chunk,
                    metadata={"url": url, "domain": domain}
                )
                docs_to_add.append(doc)

        if not docs_to_add:
            return jsonify({"error": "No documents found in CSV"}), 400

        db.add_documents(docs_to_add)
        db.persist()

        return jsonify({"message": f"Successfully embedded {len(docs_to_add)} chunks from CSV"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Flask on port 8080
    app.run(host="0.0.0.0", port=8080, debug=True)