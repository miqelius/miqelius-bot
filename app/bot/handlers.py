import os
import tempfile
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.document_service import document_service
from app.services.chat_service import chat_service
from app.storage.database import AsyncSessionLocal
from app.storage.document_repository import DocumentRepository
from app.storage.vector_store import vector_store
from app.bot.keyboards import documents_keyboard
from app.bot.states import UserState
from app.core.config import settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📄 Send me a PDF document and I'll answer questions about its content.\n\n"
        "Commands:\n"
        "/documents - list your documents\n"
        "/delete - delete a document"
    )


@router.message(F.document)
async def handle_document(message: Message):
    document = message.document
    if not document.file_name.lower().endswith('.pdf'):
        await message.answer("Please send a PDF file.")
        return
    if document.file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        await message.answer(f"File too large. Max size {settings.MAX_UPLOAD_SIZE_MB}MB.")
        return

    file_info = await message.bot.get_file(document.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        await message.bot.download_file(file_info.file_path, destination=tmp.name)
        tmp_path = tmp.name

    try:
        await document_service.process_document(
            message, tmp_path, document.file_name, message.from_user.id
        )
        await message.answer("✅ Document ready. You can now ask questions!")
    except Exception as e:
        await message.answer(f"❌ Error processing document: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.message(Command("documents"))
async def cmd_documents(message: Message):
    async with AsyncSessionLocal() as session:
        docs = await DocumentRepository.list_documents(session, message.from_user.id)
    if not docs:
        await message.answer("You have no documents.")
        return
    kb = documents_keyboard(docs)
    await message.answer("Your documents:", reply_markup=kb)


@router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        docs = await DocumentRepository.list_documents(session, message.from_user.id)
    if not docs:
        await message.answer("You have no documents.")
        return
    kb = documents_keyboard(docs)
    await message.answer("Choose a document to delete:", reply_markup=kb)
    await state.set_state(UserState.deleting_document)


@router.callback_query(F.data.startswith("doc_"))
async def handle_doc_callback(callback: CallbackQuery, state: FSMContext):
    doc_id = callback.data.split("doc_")[1]
    current_state = await state.get_state()
    
    if current_state == UserState.deleting_document:
        async with AsyncSessionLocal() as session:
            doc = await DocumentRepository.get_document_by_id(session, doc_id)
            if doc and doc.user_id == callback.from_user.id:
                await DocumentRepository.delete_document(session, doc_id, callback.from_user.id)
                vector_store.delete_document(callback.from_user.id, doc_id)
                await callback.answer("✅ Document deleted successfully.")
                await state.clear()
            else:
                await callback.answer("❌ Document not found.")
    else:
        await callback.answer("Document selected.")
    await callback.message.delete()


@router.message(F.text)
async def handle_question(message: Message):
    async with AsyncSessionLocal() as session:
        docs = await DocumentRepository.list_documents(session, message.from_user.id)
    if not docs:
        await message.answer("Please upload a PDF document first.")
        return
    await chat_service.handle_question(message, message.text, message.from_user.id)
