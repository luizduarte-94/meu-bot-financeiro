import os
import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import date

class TransactionAction(BaseModel):
    intent: Literal["expense", "income", "summary", "unknown"] = Field(
        ..., description="The type of action the user wants to perform."
    )
    amount: Optional[float] = Field(
        None, description="The monetary value of the transaction, if applicable. Always positive."
    )
    category: Optional[str] = Field(
        None, description="The category of the expense or income (e.g., 'mercado', 'salário', 'farmácia')."
    )
    description: Optional[str] = Field(
        None, description="A brief description of the transaction."
    )

async def parse_message(text: str) -> TransactionAction:
    """
    Analyzes the user's message and returns a structured TransactionAction object usando OpenAI.
    """
    client = instructor.from_openai(AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY")))
    
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=TransactionAction,
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro pessoal que lê mensagens informais e extrai intenções financeiras."},
            {"role": "user", "content": text}
        ],
    )
