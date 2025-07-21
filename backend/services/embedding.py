from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pinecone

# init Pinecone
pinecone.init(api_key="YOUR_API_KEY", environment="gcp-starter")

index = pinecone.Index("your-index-name")

def embed_and_store(text: str, namespace: str = "resume"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectors = embedding_model.embed_documents(chunks)

    # Format for Pinecone upsert
    items = [{"id": f"{namespace}-{i}", "values": vec, "metadata": {"text": chunk}}
             for i, (chunk, vec) in enumerate(zip(chunks, vectors))]

    index.upsert(items=items, namespace=namespace)

    return {"chunks_uploaded": len(items)}
