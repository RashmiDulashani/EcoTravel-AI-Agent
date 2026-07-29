import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Resolve paths relative to the project root, regardless of where this script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_documents():
    """Loads all .txt documents from data/ (recursively through category subfolders)."""
    loader = DirectoryLoader(
        path=DATA_DIR,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"  📄 Loaded {len(documents)} documents")
    return documents


def split_documents(documents):
    """Splits documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"  ✂️  Split into {len(chunks)} chunks")
    return chunks


def build_vectorstore(chunks):
    """Embeds chunks and persists them to a Chroma vector store on disk."""
    if os.path.exists(CHROMA_DIR):
        raise FileExistsError(
            f"Chroma database already exists at {CHROMA_DIR}. "
            f"Delete it first if you want to rebuild from scratch: "
            f"rmdir /s /q data\\chroma_db (Windows) or rm -rf data/chroma_db (Mac/Linux)"
        )

    print(f"  🧠 Loading embedding model: {EMBEDDING_MODEL_NAME} (may take a moment on first run)")
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )
    print(f"  💾 Vector store saved to: {CHROMA_DIR}")
    return vectorstore


def run_ingestion():
    """Runs the full ingestion pipeline: load -> split -> embed -> store."""
    print("🚀 Starting ingestion pipeline...\n")

    documents = load_documents()
    if len(documents) == 0:
        raise ValueError(
            f"No documents found in {DATA_DIR}. "
            "Did you run scripts/create_sample_docs.py first?"
        )

    chunks = split_documents(documents)
    vectorstore = build_vectorstore(chunks)

    count = vectorstore._collection.count()
    print(f"\n✅ Ingestion complete: {count} chunks stored in Chroma")
    return vectorstore


if __name__ == "__main__":
    run_ingestion()