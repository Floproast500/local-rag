Local RAG Project

This repository demonstrates a local Retrieval-Augmented Generation (RAG) setup using LangChain, Chroma (for vector storage), and a Flask + Streamlit front-end/back-end. Additionally, it includes:

    Rotating User Agents to avoid 403 blocks while scraping.
    PDF / DOCX / TXT / MD Embedding for general file ingestion.
    Sitemap Scraper that recursively parses Yoast/WordPress sitemaps (or standard sitemaps) to index entire domains.
    Domain-level grouping of scraped pages for “chat with this whole domain” functionality.

Features

    Embed Documents: Upload PDF, DOCX, TXT, MD; store chunks in Chroma.
    Query Database (RAG):
        Choose “All Documents,” a specific PDF, or a scraped domain.
        The LLM retrieves context from the selected source(s) to generate answers.
    NO RAG Chat: Directly converse with the LLM without retrieval.
    Sitemap Scraper:
        Handles sitemap indexes (WordPress, Yoast) and normal XML sitemaps.
        Rotates user agents for each request to reduce 403 errors.
        Embeds scraped content (with domain-based grouping).

Project Structure

.
├── app.py                  # Main Flask server (endpoints for embed/query/list_docs/etc.)
├── app_frontend.py         # Streamlit front-end with four tabs (Embed, Query, NO RAG, Sitemap Scraper)
├── embed.py                # Embeds uploaded files (pdf/docx/txt/md) using UnstructuredFileLoader
├── get_vector_db.py        # Returns a Chroma-based vector store with OllamaEmbeddings
├── query.py                # RAG query logic, optionally filtering by doc or domain
├── rotating_user_agent.py  # Rotating user-agent logic & recursive sitemap parser
├── requirements.txt        # (Optionally) Python dependencies
└── README.md               # This readme

Requirements

    Python 3.8+ recommended.
    The following Python libraries (install via pip install):
        streamlit
        requests
        beautifulsoup4
        lxml
        pandas
        unstructured and related dependencies (for multi-file ingestion)
        langchain_community (or whichever version you’re using for ChatOllama, OllamaEmbeddings, etc.)
        werkzeug (for secure_filename, typically installed with Flask)
        dotenv (if you use environment variables in .env)

Example:

pip install streamlit requests beautifulsoup4 lxml pandas unstructured langchain_community flask python-dotenv

Getting Started

Create a Virtual Environment:

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or .\venv\Scripts\activate  # Windows

Install Dependencies:

pip install -r requirements.txt

Set up Environment Variables (optional):

    .env file with keys like:

        LLM_MODEL=mistral
        TEXT_EMBEDDING_MODEL=nomic-embed-text
        CHROMA_PATH=chroma
        COLLECTION_NAME=local-rag

    Or rely on defaults in the code.

Running the App

    Start the Flask Backend:

python3 app.py

    This launches the backend on http://localhost:8080.

Start the Streamlit Frontend:

    streamlit run app_frontend.py

        This opens the frontend at http://localhost:8501 in your browser.

Usage Flow

    Embed Document Tab
        Upload a PDF, DOCX, TXT, or MD file.
        Chunks are stored in Chroma with metadata["filename"] = "<the uploaded filename>".

    Query Database Tab
        Dropdown:
            All Documents
            PDF: someFile.pdf
            Scraped Domain: example.com
        Enter a query, click Submit to do RAG.
        The system uses a retrieval step + ChatOllama to generate answers.

    NO RAG Chat Tab
        Type your question or message.
        Directly calls the LLM (no retrieval from docs).

    Sitemap Scraper Tab
        Enter a sitemap URL (index or normal).
        On “Scrape Sitemap,” the code:
            Recursively expands sub-sitemaps if needed (Yoast, etc.).
            Uses rotating user agents to reduce 403 blocks.
            Collects (URL, Content) for each final page.
        Click “Embed CSV” to store the results in Chroma:
            Each chunk has metadata["domain"] = parsedDomain, so you can chat with an entire domain at once.

Troubleshooting

    Not seeing a scraped domain in the Query Database dropdown?
        Make sure you clicked “Embed CSV” after scraping.
        Confirm in the console/logs that scrapedDomains is returned by GET /list_documents.
    403 Errors while scraping?**
        We rotate user agents, but some sites block more aggressively. Consider adding proxies or longer delays between requests.
    Large PDFs or big sitemaps can be slow to embed. Consider chunk size, concurrency, and other optimizations.

Contributing

    Feel free to open issues or PRs to improve the codebase, fix bugs, or add new features like advanced model selection, multi-domain queries, or proxy rotation for scraping.
