import logging
import os
from pathlib import Path
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.schema import Document

from app.core.config import settings
from app.models.schemas import QueryResponse, SourceDoc

logger = logging.getLogger(__name__)

STRICT_SYSTEM_PROMPT = """You are DocTalk AI, a precise internal policy assistant.
CRITICAL RULES:
1. Answer ONLY using provided context.
2. If not found, say: FALLBACK: I could not find relevant information.
3. Do not hallucinate.
Context: {context}
Question: {question}
Answer:"""

class RAGService:
    def __init__(self):
        self._embeddings = None
        self._vectorstore = None
        self._llm = None

    def _get_clean_api_key(self) -> str:
        """Forcefully extracts a plain string to bypass SecretStr issues."""
        key = os.environ.get("GOOGLE_API_KEY", "")
        if hasattr(key, "get_secret_value"):
            return key.get_secret_value()
        return str(key)

    def _get_embeddings(self):
        if not self._embeddings:
            # Explicitly passing the key as a string fixes the gRPC error
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self._get_clean_api_key(),
                request_options={"timeout": 120} # Increased timeout for 504 errors
            )
        return self._embeddings

    def _get_llm(self):
        if not self._llm:
            self._llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=self._get_clean_api_key(),
                temperature=0.1,
                request_options={"timeout": 120}
            )
        return self._llm

    def _get_vectorstore(self) -> Chroma:
        if not self._vectorstore:
            persist_path = settings.VECTOR_STORE_PATH
            Path(persist_path).mkdir(parents=True, exist_ok=True)
            self._vectorstore = Chroma(
                collection_name="doctalk_policies",
                embedding_function=self._get_embeddings(),
                persist_directory=persist_path,
            )
        return self._vectorstore

    def ingest_document(self, file_path: str, filename: str) -> int:
        loader = PyPDFLoader(file_path)
        raw_pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        chunks = []
        for page_doc in raw_pages:
            page_num = page_doc.metadata.get("page", 0) + 1
            splits = splitter.split_documents([page_doc])
            for i, chunk in enumerate(splits):
                chunk.metadata.update({"source_filename": filename, "page_number": page_num, "chunk_index": i})
                chunks.append(chunk)
        self._get_vectorstore().add_documents(chunks)
        return len(chunks)

    def query(self, question: str, top_k: int = 4) -> QueryResponse:
        try:
            vs = self._get_vectorstore()
            results = vs.similarity_search_with_score(question, k=top_k)
            
            if not results:
                return self._fallback_response("No relevant documents found.", question)

            context = "\n\n".join([f"[{d.metadata.get('source_filename')} - P{d.metadata.get('page_number')}]\n{d.page_content}" for d, _ in results])
            response = self._get_llm().invoke(STRICT_SYSTEM_PROMPT.format(context=context, question=question))
            
            sources = []
            seen = set()
            for doc, _ in results:
                key = (doc.metadata.get("source_filename"), doc.metadata.get("page_number"))
                if key not in seen:
                    seen.add(key)
                    sources.append(SourceDoc(filename=key[0], page=key[1], excerpt=doc.page_content[:200]))

            return QueryResponse(answer=response.content.strip(), sources=sources, is_fallback=False, contact_email=settings.HR_CONTACT_EMAIL, question=question)
        except Exception as e:
            logger.error(f"RAG Error: {e}")
            return self._fallback_response(f"Error: {str(e)}", question)

    def _fallback_response(self, msg, q):
        return QueryResponse(answer=msg, sources=[], is_fallback=True, contact_email=settings.HR_CONTACT_EMAIL, question=q)

rag_service = RAGService()