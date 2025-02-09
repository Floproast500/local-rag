import os
from datetime import datetime
from werkzeug.utils import secure_filename

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_vector_db import get_vector_db

TEMP_FOLDER = os.getenv('TEMP_FOLDER', './_temp')
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def embed_any_file(file):
    """
    Embeds a file (pdf, docx, txt, md) into Chroma DB, storing 'filename' in metadata.
    """
    if file.filename != '' and file and allowed_file(file.filename):
        # Save locally
        ts_name = str(datetime.now().timestamp()) + "_" + secure_filename(file.filename)
        file_path = os.path.join(TEMP_FOLDER, ts_name)
        os.makedirs(TEMP_FOLDER, exist_ok=True)
        file.save(file_path)

        # Load via UnstructuredFileLoader
        loader = UnstructuredFileLoader(file_path=file_path)
        data = loader.load()

        # Chunk if needed
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
        chunks = text_splitter.split_documents(data)

        # Store the original user-facing filename
        for c in chunks:
            c.metadata["filename"] = file.filename

        db = get_vector_db()
        db.add_documents(chunks)
        db.persist()

        # Optionally remove local file
        # os.remove(file_path)

        return True
    return False