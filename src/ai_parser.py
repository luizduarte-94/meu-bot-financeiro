import os
import google.generativeai as genai
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
    Analyzes the user's message and returns a structured TransactionAction object usando Gemini.
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "Você é um assistente financeiro pessoal que lê mensagens informais e extrai intenções financeiras.\n"
            "Retorne EXATAMENTE um objeto JSON (sem formatação Markdown) com as seguintes chaves rigorosamente:\n"
            "1. 'intent': Apenas os valores 'expense', 'income', 'summary', ou 'unknown'.\n"
            "2. 'amount': Número float positivo ou null.\n"
            "3. 'category': Categoria curta ou null.\n"
            "4. 'description': Descrição curta ou null."
        )
    )
    
    response = await model.generate_content_async(
        text,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        ),
    )
    
    return TransactionAction.model_validate_json(response.text)
