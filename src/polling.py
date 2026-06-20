import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
LOCAL_WEBHOOK_URL = "http://127.0.0.1:8080/webhook"

def delete_webhook():
    print("Limpando Webhooks antigos...")
    httpx.get(f"{API_URL}/deleteWebhook")

def poll():
    delete_webhook()
    offset = 0
    print("[OK] Polling ativado! O bot esta escutando suas mensagens no Telegram...")
    while True:
        try:
            res = httpx.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 10}, timeout=15)
            data = res.json()
            if data.get("ok"):
                for update in data["result"]:
                    offset = update["update_id"] + 1
                    # Envia para o nosso FastAPI local
                    try:
                        httpx.post(LOCAL_WEBHOOK_URL, json=update)
                        print(f"Mensagem processada: {update.get('message', {}).get('text')}")
                    except Exception as e:
                        print(f"[ERRO] Erro ao enviar para o FastAPI: {e}")
        except Exception as e:
            print(f"Erro de conexão com o Telegram: {e}")
            time.sleep(2)

if __name__ == "__main__":
    poll()
