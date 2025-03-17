#4. Set Up Database for Vector Store

#Option 1: Use Cloud Storage (AWS S3)

# In vector_store.py
import boto3
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

def initialize_vector_store():
    # Connect to S3
    s3 = boto3.client('s3')

    # Check if we have a precomputed vector store
    try:
        s3.download_file('your-bucket', 'vectorstore.zip', '/tmp/vectorstore.zip')
        # Unzip the file
        import zipfile
        with zipfile.ZipFile('/tmp/vectorstore.zip', 'r') as zip_ref:
            zip_ref.extractall('/tmp/vectorstore')

        # Load the vector store
        embeddings = OpenAIEmbeddings()
        vector_store = Chroma(persist_directory='/tmp/vectorstore', embedding_function=embeddings)
        return vector_store

    except Exception as e:
        print(f"Creating new vector store: {e}")
        # Create a new vector store
        vector_store = create_modalai_vector_db()

        # Save and upload to S3
        vector_store.persist()

        # Zip the directory
        import shutil
        shutil.make_archive('/tmp/vectorstore', 'zip', '/tmp/vectorstore')

        # Upload to S3
        s3.upload_file('/tmp/vectorstore.zip', 'your-bucket', 'vectorstore.zip')

        return vector_store

#Option 2: Use Managed Vector Database

#For production, consider using a managed vector database like:

#1. Pinecone:
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
import pinecone

def initialize_vector_store():
    # Initialize Pinecone
    pinecone.init(
        api_key=os.environ["PINECONE_API_KEY"],
        environment=os.environ["PINECONE_ENVIRONMENT"]
    )

    # Create index if it doesn't exist
    if "modalai-docs" not in pinecone.list_indexes():
        pinecone.create_index(
            name="modalai-docs",
            dimension=1536,  # OpenAI embedding dimension
            metric="cosine"
        )

    # Load or create vector store
    embeddings = OpenAIEmbeddings()
    index = pinecone.Index("modalai-docs")

    # Check if index is empty
    stats = index.describe_index_stats()
    if stats["total_vector_count"] == 0:
        # Create and populate index
        documents = fetch_modalai_documentation()
        Pinecone.from_texts(
            texts=[doc for _, doc in documents.items()],
            embedding=embeddings,
            index_name="modalai-docs"
        )

    return Pinecone.from_existing_index("modalai-docs", embeddings)

