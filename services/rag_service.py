import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


logging.getLogger("pypdf").setLevel(logging.ERROR)


# -----------------------------
# Embeddings
# -----------------------------

embedding = HuggingFaceEmbeddings(
    model='sentence-transformers/all-MiniLM-L6-v2',
    )


# -----------------------------
# Vector store
# -----------------------------

vector_store=FAISS.load_local(
    "vectorstore/air_quality_faiss_index",
    embedding,
    allow_dangerous_deserialization=True
    )



# -----------------------------
# Retriever
# -----------------------------

# convert vector store into a retriever
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)


def get_guideline_retrieval_status(question):
    try:
        docs = retriever.invoke(question)

        useful_docs = [
            doc for doc in docs
            if doc.page_content and len(doc.page_content.strip()) > 100
        ]

        return {
            "retrieved_chunks": len(useful_docs)
        }

    except Exception:
        return {
            "retrieved_chunks": 0
        }



# -----------------------------
# LLM
# -----------------------------

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation",
    temperature=0.2
)

llm = ChatHuggingFace(llm=llm)



# -----------------------------
# Prompt
# -----------------------------

prompt = PromptTemplate(
    template="""
      You are an Air Quality Action Planner for India.

Answer the user's question using ONLY the provided CPCB/WHO guideline context.

Rules:
1. Use only the provided context.
2. Do not invent facts.
3. Do not give medical diagnosis.
4. Give practical public guidance.
5. If the context does not contain the answer, say:
   "I could not find this information in the provided guideline documents."
6. Mention the source organization when possible, such as CPCB or WHO.
7. Keep the answer simple and useful.
8. For Indian AQI categories, use only CPCB National AQI / IND-AQI categories.
9. Do not include categories from other countries such as USEPA, China, or EU unless the user specifically asks for comparison.
10. Do not invent formulas.
11. Do not use city ranking, healthy score, or AQIR formulas unless the user asks about city ranking.
12. Do not give medical diagnosis or medicine advice.


Guideline Context:
{context}

User Question:
{question}

    """,
    input_variables=['context','question']
)



# -----------------------------
# Helpers
# -----------------------------

def format_docs(docs):
    formatted_context = ""

    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown source")
        page = doc.metadata.get("page", "Unknown page")
        organization = doc.metadata.get("organization", "Unknown organization")

        formatted_context+=f"\n\n--- Source {i+1} ---\n"
        formatted_context+=f"Organization: {organization}\n"
        formatted_context+=f"Source file: {source}\n"
        formatted_context+=f"Page: {page}\n"
        formatted_context+=f"Content:\n{doc.page_content}\n"

    return formatted_context


def format_sources(docs):
    sources = []

    for i, doc in enumerate(docs):
        sources.append({
            "source_id": i + 1,
            "organization": doc.metadata.get("organization", "Unknown"),
            "source_file": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "Unknown"),
            "preview": doc.page_content[:300]
        })

    return sources


# -----------------------------
# RAG chain
# -----------------------------

parser=StrOutputParser()

parallel_chain=RunnableParallel({
    "context":retriever|RunnableLambda(format_docs),
    "question":RunnablePassthrough()
})

main_chain=parallel_chain|prompt|llm|parser


def is_medical_question(question):
    if not question:
        return False

    question = question.lower()

    medical_keywords = [
        "diagnose",
        "diagnosis",
        "asthma",
        "medicine",
        "medication",
        "tablet",
        "drug",
        "dose",
        "dosage",
        "prescription",
        "treatment",
        "treat",
        "cure",
        "lung disease",
        "lung problem",
        "breathing problem",
        "chest pain",
        "doctor",
        "hospital",
        "inhaler",
        "should i take",
        "do i have",
        "am i sick",
        "health condition"
    ]

    return any(keyword in question for keyword in medical_keywords)

def ask_guidelines(question, apply_safety_guard=True):
    if apply_safety_guard and is_medical_question(question):
        return (
            "This app cannot diagnose diseases or recommend medicines. "
            "It only provides general air-quality guidance. "
            "Please consult a medical professional for personal health concerns."
        )

    return main_chain.invoke(question)