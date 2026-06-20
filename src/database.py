import os
from supabase import create_client, Client
from datetime import datetime

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials not found in environment variables.")
    return create_client(url, key)

def save_transaction(user_id: int, user_name: str, intent: str, amount: float, category: str):
    supabase = get_supabase_client()
    
    # 1. Garante que o usuário existe na base (Upsert)
    supabase.table("users").upsert({
        "telegram_id": user_id,
        "name": user_name
    }).execute()
    
    # 2. Salva a transação
    data = {
        "user_id": user_id,
        "type": intent,
        "amount": amount,
        "category": category,
        "date": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("transactions").insert(data).execute()
    return result.data[0] if result.data else None

def get_monthly_summary(user_id: int):
    supabase = get_supabase_client()
    
    # Para simplificar no protótipo, buscamos todas as transações do usuário
    # Em produção, você faria um filtro por data na query do Supabase
    result = supabase.table("transactions").select("*").eq("user_id", user_id).execute()
    
    transactions = result.data
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income" and t["amount"])
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense" and t["amount"])
    
    return {
        "incomes": total_income,
        "expenses": total_expense,
        "balance": total_income - total_expense
    }
