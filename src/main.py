import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# Carrega as variáveis do .env no início do app
load_dotenv()

from src.ai_parser import parse_message
from src.database import save_transaction, get_monthly_summary
from src.telegram_client import send_message
import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-configura o Webhook se estiver rodando na Render
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if render_url and bot_token:
        webhook_url = f"{render_url}/webhook"
        api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        async with httpx.AsyncClient() as client:
            resp = await client.post(api_url, json={"url": webhook_url})
            print(f"Webhook set: {resp.json()}")
    yield

app = FastAPI(title="Telegram Finance Bot", lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Endpoint que o Telegram chama a cada nova mensagem.
    """
    data = await request.json()
    
    # Verifica se a request contém uma mensagem normal
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_name = message["from"].get("first_name", "Usuário")
        text = message.get("text", "")
        
        if not text:
            return {"status": "ok"}
            
        try:
            # 1. Usa OpenAI para interpretar a linguagem natural
            parsed = await parse_message(text)
            
            # 2. Executa a ação baseada na intenção
            if parsed.intent in ["expense", "income"]:
                if parsed.amount is None:
                    await send_message(chat_id, "Não consegui identificar o valor. Pode repetir de outra forma? Ex: 'gastei 50 no posto'")
                    return {"status": "ok"}
                    
                # Salva no Supabase
                save_transaction(
                    user_id=chat_id,
                    user_name=user_name,
                    intent=parsed.intent,
                    amount=parsed.amount,
                    category=parsed.category or "Geral"
                )
                
                # Responde confirmando
                tipo_str = "Gasto" if parsed.intent == "expense" else "Ganho"
                msg = f"✅ *{tipo_str} Registrado!*\n"
                msg += f"• Valor: R$ {parsed.amount:.2f}\n"
                msg += f"• Categoria: {parsed.category or 'Geral'}\n"
                msg += f"• Pessoa: {user_name}"
                await send_message(chat_id, msg)
                
            elif parsed.intent == "summary":
                summary = get_monthly_summary(user_id=chat_id)
                msg = f"📊 *Resumo Financeiro*\n\n"
                msg += f"• Entradas: R$ {summary['incomes']:.2f}\n"
                msg += f"• Saídas: R$ {summary['expenses']:.2f}\n"
                msg += f"• Saldo Atual: *R$ {summary['balance']:.2f}*"
                await send_message(chat_id, msg)
                
            else:
                await send_message(chat_id, "Desculpe, não entendi. Tente algo como 'gastei 50 no mercado' ou 'resumo do mês'.")
                
        except Exception as e:
            print(f"Erro processando a mensagem: {e}")
            await send_message(chat_id, "Ops, ocorreu um erro interno ao processar sua mensagem. Verifique os logs.")

    return {"status": "ok"}

@app.get("/")
def health_check():
    return {"status": "Bot is running. Configure o Webhook do Telegram para o endpoint /webhook"}
