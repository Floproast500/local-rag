import os
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from get_vector_db import get_vector_db

LLM_MODEL = os.getenv('LLM_MODEL', 'mistral')

def get_prompt():
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question,
        your goal is to help the user overcome limitations of distance-based similarity.
        
        Original question: {question}
        """
    )

    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    return QUERY_PROMPT, prompt

def query(user_query, doc_type=None, doc_name=None):
    """
    If doc_type=='pdf', filter by metadata["filename"] = doc_name
    If doc_type=='scraped_domain', filter by metadata["domain"] = doc_name
    Otherwise, no filter => all docs
    """
    if not user_query:
        return None

    llm = ChatOllama(model=LLM_MODEL)
    db = get_vector_db()
    QUERY_PROMPT, prompt = get_prompt()

    metadata_filter = None
    if doc_type == "pdf" and doc_name:
        metadata_filter = {"filename": doc_name}
    elif doc_type == "scraped_domain" and doc_name:
        metadata_filter = {"domain": doc_name}

    retriever = MultiQueryRetriever.from_llm(
        retriever=db.as_retriever(search_kwargs={"filter": metadata_filter}),
        llm=llm,
        prompt=QUERY_PROMPT
    )

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(user_query)
    return response