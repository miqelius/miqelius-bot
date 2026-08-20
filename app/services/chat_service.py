import logging
from aiogram.types import Message
from app.storage.database import AsyncSessionLocal
from app.core.exceptions import NoAnswerFoundError
from app.storage.document_repository import DocumentRepository
from app.storage.vector_store import vector_store
from app.retrieval.relevance_filter import RelevanceFilter
from app.llm.answer_generator import answer_generator

logger = logging.getLogger(__name__)


class StatusReporter:
    @staticmethod
    async def update_status(status_msg: Message, new_text: str):
        try:
            await status_msg.edit_text(new_text)
        except Exception as e:
            logger.warning(f"Could not update status message: {e}")


class ChatService:
    def __init__(self):
        self.vector_store = vector_store
        self.generator = answer_generator

    async def handle_question(self, message: Message, question: str, user_id: int):
        status_msg = await message.answer("⏳ Processing your question...")
        
        try:
            async with AsyncSessionLocal() as session:
                docs = await DocumentRepository.list_documents(session, user_id)
            
            if not docs:
                await StatusReporter.update_status(status_msg, "Please upload a PDF document first.")
                return
            
            await StatusReporter.update_status(status_msg, "◦ Searching documents...")
            chunks = self.vector_store.search_chunks(user_id, question)
            
            if not chunks:
                await StatusReporter.update_status(status_msg, "No relevant information found in documents.")
                return
            
            await StatusReporter.update_status(status_msg, "◦ Verifying sources...")
            filtered_chunks = RelevanceFilter.filter(chunks)
            
            await StatusReporter.update_status(status_msg, "◦ Generating response...")
            answer_data = await self.generator.generate_answer(question, filtered_chunks)
            
            answer_text = answer_data["answer"]
            sources = answer_data["sources"]
            
            response = answer_text + "\n\n📄 Sources:\n"
            for src in sources:
                response += f"`{src['filename']} — Page {src['page']}`\n\"{src['snippet']}\"\n"
            
            await StatusReporter.update_status(status_msg, response)
        except NoAnswerFoundError:
            await StatusReporter.update_status(
                status_msg,
                "I couldn't find enough information in the uploaded documents to answer this question."
            )
        except Exception as e:
            await StatusReporter.update_status(status_msg, f"❌ Error: {str(e)}")
            logger.error(f"Chat error: {e}")


chat_service = ChatService()
