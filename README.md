This project demonstrates a local Retrieval-Augmented Generation (RAG) setup using LangChain, Chroma (for vector storage), and a Flask + Streamlit front-end/back-end.

It includes:

    Rotating User Agents to reduce 403 blocks when scraping (useful for WordPress/Yoast sitemaps and common scraper blocking techniques).
    PDF, DOCX, TXT, MD, and more - embedding for general file ingestion.
    A sitemap scraper that recursively parses WordPress/Yoast or standard sitemaps to index entire domains.
    Domain-level grouping of scraped pages, so you can chat with an entire domain at once.

FEATURES

    Embed Documents
    You can upload PDF, DOCX, TXT, or MD files. The chunks are stored in Chroma.

    Query Database (RAG)
    You can choose “All Documents,” a specific PDF, or a scraped domain. The system retrieves relevant chunks from your chosen docs or domains and then passes them to the LLM to generate an answer.

    NO RAG Chat
    You can directly converse with the LLM without any retrieval context.

    Sitemap Scraper
    Recursively parses sub-sitemaps (including Yoast-style sitemap indexes) and rotates user agents to help avoid 403 errors. It then embeds the scraped data with domain-based grouping.

REPOSITORY STRUCTURE

.
├── app.py                  # Main Flask server (endpoints: embed, query, list_docs, etc.)
├── app_frontend.py         # Streamlit front-end with four tabs (Embed, Query, NO RAG, Sitemap Scraper)
├── embed.py                # Embeds uploaded files using UnstructuredFileLoader
├── get_vector_db.py        # Returns a Chroma-based vector store configured with OllamaEmbeddings
├── query.py                # RAG query logic (filters by doc or domain)
├── rotating_user_agent.py  # Handles rotating user-agent logic & recursive sitemap parsing
├── requirements.txt        # Python dependencies (optional)
└── README.md               # This readme

REQUIREMENTS

    Python 3.8 or higher is recommended.
    You need various Python libraries: streamlit, requests, beautifulsoup4, lxml, pandas, unstructured, langchain_community, flask, python-dotenv, werkzeug (usually installed with Flask).
    
    requirements.txt:

        streamlit
        requests
        beautifulsoup4
        lxml
        pandas
        unstructured
        langchain_community
        flask
        python-dotenv
        werkzeug

You can install everything by running: pip install -r requirements.txt

If you do not have a requirements.txt, install each library manually.

INSTALLING AND USING MODELS

This project references ChatOllama and OllamaEmbeddings from langchain_community. That typically requires Ollama if you want to run local LLMs on macOS or certain Linux builds.

    Install Ollama by downloading from the official Ollama GitHub Releases page.
    Verify installation by running: ollama --version
    Pull the LLM model you plan to use, for example, mistral is written in to this project: ollama pull mistral
    Pull a text embedding model, for example: ollama pull nomic-embed-text
    
    [Run the Ollama server: ollama serve 
    Keep this process running so the system can access your models.]

ENVIRONMENT VARIABLES

You can create a .env file in the project root. Possible keys are: 
LLM_MODEL=mistral
TEXT_EMBEDDING_MODEL=nomic-embed-text
CHROMA_PATH=chroma
COLLECTION_NAME=local-rag

Alternatively, export them directly in your shell. Make sure they match any models you pulled with Ollama.

SETUP AND INSTALLATION

    Clone the repository: git clone https://github.com/Floproast500/local-rag.git cd local-rag

    (Optional) Create and activate a virtual environment: python3 -m venv venv source venv/bin/activate (Use the equivalent command for Windows if needed.)

    Install dependencies: pip install -r requirements.txt (Or install libraries manually if no requirements.txt.)

    Install and run Ollama as described above. Also pull and serve your chosen models.

    Start the Flask backend: python3 app.py This will run on http://localhost:8080.

    Start the Streamlit frontend: streamlit run app_frontend.py This will open on http://localhost:8501.

USAGE FLOW

    Embed Document Tab: Upload PDF, DOCX, TXT, or MD. These files are chunked and stored in Chroma, with metadata["filename"] set.
    Query Database (RAG) Tab: You can select All Documents, a PDF, or Scraped Domain. Enter your query and click Submit to get an LLM-powered answer with retrieved context.
    NO RAG Chat Tab: A direct conversation with the LLM, without retrieving anything.
    Sitemap Scraper Tab: Enter a sitemap URL. The scraper will recursively parse the sitemap and sub-sitemaps, rotating user agents to avoid 403. Click "Embed CSV" to store the scraped data in Chroma, where each page is associated with metadata["domain"]. Then you can query the entire domain at once.

TROUBLESHOOTING

If you do not see your scraped domain in the Query Database dropdown, ensure that you have clicked "Embed CSV" after scraping, and then refresh the browser. You can also run curl localhost:8080/list_documents to confirm the domain is in scrapedDomains.

If you encounter 403 errors during scraping, rotating user agents may not be enough for certain sites, so consider additional steps like proxies, time delays, or respecting robots.txt.

Large PDFs or sitemaps may be slow to embed; you can adjust chunk size or add concurrency.

If Ollama cannot find a model, verify you pulled that model name and that ollama serve is running in the background.

CONTRIBUTING

Feel free to open issues or pull requests to improve the codebase, fix bugs, or add new features such as advanced model selection, multi-domain queries, or proxy rotation for scraping.

LICENSE

You may release this project under the MIT License or any license of your choosing. Update the LICENSE file or this readme accordingly.
