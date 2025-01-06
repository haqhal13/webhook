from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE"

@app.route("/")
def home():
    """
    Health check endpoint to confirm the server is running.
    """
    return "Webhook is running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    """
    Telegram webhook endpoint to process updates.
    """
    try:
        # Parse the incoming request from Telegram
        data = request.get_json()

        # Log the data for debugging
        print("[DEBUG] Incoming Telegram update:", data)

        # Process the update (you can expand this to handle commands, messages, etc.)
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            # Respond to the user (optional)
            if text:
                send_message(chat_id, f"You said: {text}")

        return "OK", 200
    except Exception as e:
        print("[ERROR] An error occurred:", str(e))
        return jsonify({"error": str(e)}), 500

def send_message(chat_id, text):
    """
    Helper function to send a message via Telegram API.
    """
    TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        print("[DEBUG] Telegram API response:", response.json())
    except Exception as e:
        print("[ERROR] Failed to send message:", str(e))

if __name__ == "__main__":
    # Run the app locally for development
    app.run(host="0.0.0.0", port=5000)
