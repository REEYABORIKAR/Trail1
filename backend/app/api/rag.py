import logging
import os
from pathlib import Path
from typing import List, Tuple

from fastapi import APIRouter, File, UploadFile, HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.schema import Document
from pydantic import BaseModel

from app.core.config import settings
from app.models.schemas import QueryResponse, SourceDoc, IngestResponse

logger = logging.getLogger(__name__)

# --- Router Definition ---
router = APIRouter(prefix="/api/rag", tags=["RAG"])

STRICT_SYSTEM_PROMPT = """You are DocTalk AI, a precise internal policy assistant.
CRITICAL RULES:
1. Answer ONLY using provided context.
2. If not found, say: FALLBACK: I could not find relevant information about this in company documents.
Context: {context}
Question: {question}
Answer:"""

class RAGService:
    def __init__(self):
        self._embeddings = None
        self._vectorstore = None
        self._llm = None

    def _get_clean_api_key(self) -> str:
        """Extracts plain string to bypass SecretStr issues that cause gRPC crashes."""
        key = os.environ.get("GOOGLE_API_KEY", "")
        if hasattr(key, "get_secret_value"):
            return key.get_secret_value()
        return str(key)

    def _get_embeddings(self):
        if not self._embeddings:
            # Explicit key + 120s timeout to prevent 504 errors
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self._get_clean_api_key(),
                request_options={"timeout": 120} 
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

    def query(self, question: str, top_k: int = 4) -> QueryResponse:
        try:
            vs = self._get_vectorstore()
            results = vs.similarity_search_with_score(question, k=top_k)
            
            if not results:
                return self._fallback_response("No relevant documents found.", question)

            context = "\n\n".join([f"[{d.metadata.get('source_filename')} - P{d.metadata.get('page_number')}]\n{d.page_content}" for d, _ in results])
            response = self._get_llm().invoke(STRICT_SYSTEM_PROMPT.format(context=context, question=question))
            
            sources = [SourceDoc(filename=d.metadata.get("source_filename"), 
                                 page=d.metadata.get("page_number"), 
                                 excerpt=d.page_content[:200]) for d, _ in results]

            return QueryResponse(answer=response.content.strip(), sources=sources, is_fallback=False, 
                                 contact_email=settings.HR_CONTACT_EMAIL, question=question)
        except Exception as e:
            logger.error(f"RAG Error: {e}")
            return self._fallback_response(f"API Error: {str(e)}", question)

    def _fallback_response(self, msg, q):
        return QueryResponse(answer=msg, sources=[], is_fallback=True, contact_email=settings.HR_CONTACT_EMAIL, question=q)

rag_service = RAGService()

# --- API Endpoints ---
class QueryRequest(BaseModel):
    question: str
    top_k: int = 4

@router.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    return rag_service.query(request.question, request.top_k)