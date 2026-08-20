from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from app.models.document import Document


def documents_keyboard(documents: List[Document]) -> InlineKeyboardMarkup:
    buttons = []
    for doc in documents:
        buttons.append([
            InlineKeyboardButton(
                text=doc.file_name, 
                callback_data=f"doc_{doc.doc_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
