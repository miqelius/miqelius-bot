import logging
from typing import List, Dict, Any
from app.services.llm_client import llm_client
from app.services.context_builder import ContextBuilder
from app.core.exceptions import NoAnswerFoundError

logger = logging.getLogger(__name__)


class AnswerGenerator:
    def __init__(self):
        self.llm_client = llm_client
        self.context_builder = ContextBuilder()

    async def generate_answer(
        self,
        question: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not chunks:
            raise NoAnswerFoundError("No relevant documents found")
        
        # Build context from chunks
        context = self.context_builder.build_context(chunks)
        prompt = self.context_builder.build_prompt(question, context)
        
        # Generate answer
        answer = await self.llm_client.generate(prompt)
        
        # Extract sources
        sources = [
            {
                "filename": chunk.get("metadata", {}).get("filename", "Unknown"),
                "page": chunk.get("metadata", {}).get("chunk_idx", 0) + 1,
                "snippet": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
            }
            for chunk in chunks[:3]  # Top 3 sources
        ]
        
        return {
            "answer": answer,
            "sources": sources
        }


answer_generator = AnswerGenerator()
