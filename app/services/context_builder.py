from typing import List, Dict, Any


class ContextBuilder:
    @staticmethod
    def build_context(chunks: List[Dict[str, Any]], max_tokens: int = 2000) -> str:
        context = ""
        token_count = 0
        
        for chunk in chunks:
            # Rough token estimate (1 token ≈ 4 chars)
            chunk_tokens = len(chunk["text"]) // 4
            
            if token_count + chunk_tokens > max_tokens:
                break
            
            context += chunk["text"] + "\n\n"
            token_count += chunk_tokens
        
        return context.strip()

    @staticmethod
    def build_prompt(question: str, context: str) -> str:
        return f"""You are a helpful assistant that answers questions based on the provided document context.

Question: {question}

Context from documents:
{context}

Please provide a clear, accurate answer based on the context. If the context doesn't contain information to answer the question, say so."""
