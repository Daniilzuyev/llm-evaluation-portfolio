from app.corpus import load_chunks
from langchain_core.tools import tool

CHUNKS = load_chunks()

@tool
def get_card_fee(card_type: str) -> str:
    """Return the monthly maintenance fee and waiver conditions for an Imagine Bank card. card_type must be 'credit' or 'debit'. Use it when the user asks about card fees."""
    for chunk in CHUNKS:
        if chunk.doc_title == "Card Fees" and card_type.lower() in chunk.text.lower():
            return chunk.text
    return f"No fee information for card type: {card_type}"

@tool
def get_transfer_limit(transfer_type: str) -> str:
    """Return the transfer limit for an Imagine Bank transfer type. transfer_type must be 'internal', 'external' or 'international'. Use it when the user asks about transfer limits."""
    for chunk in CHUNKS:
        if chunk.doc_title == "Transfer Limits" and transfer_type.lower() in chunk.text.lower():
            return chunk.text
    return f"No limit information for transfer type: {transfer_type}"

