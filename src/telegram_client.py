import os
import httpx

def get_telegram_url():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    return f"https://api.telegram.org/bot{token}"

async def send_message(chat_id: int, text: str):
    """Envia uma mensagem de texto para o usuário via Telegram."""
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        print("Aviso: TELEGRAM_BOT_TOKEN não está definido.")
        return
        
    url = f"{get_telegram_url()}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao enviar mensagem para o Telegram: {e}")
            return None
