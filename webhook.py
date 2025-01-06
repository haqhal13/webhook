from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE"
BOT_UPDATE_URL = f"http://localhost:5000/add_invite"  # Adjust if your bot runs on a different URL/port

# In-memory invite link storage
invite_links = {}

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
        data = request.get_json()

        # Log the data for debugging
        print("[DEBUG] Incoming Telegram update:", data)

        # Process Telegram messages
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            # Handle commands
            if text == "/start":
                send_message(chat_id, "✅ Welcome! The bot is running.")
            elif text == "/list_invites":
                if not invite_links:
                    send_message(chat_id, "ℹ️ No invite links registered.")
                else:
                    links = "\n".join(invite_links.keys())
                    send_message(chat_id, f"📜 Registered Invite Links:\n{links}")

        return "OK", 200
    except Exception as e:
        print("[ERROR] An error occurred:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/register_invite", methods=["POST"])
def register_invite():
    """
    Custom route to register invite links sent via external service (e.g., Make).
    """
    try:
        data = request.get_json()
        invite_link = data.get("invite_link")

        # Validate invite link
        if not invite_link or not invite_link.startswith("https://t.me/"):
            return jsonify({"error": "Invalid invite link"}), 400

        # Save the invite link
        if invite_link in invite_links:
            return jsonify({"error": "Invite link already registered"}), 400

        invite_links[invite_link] = False  # Mark as unused
        print(f"[INFO] Invite link registered: {invite_link}")

        # Notify the bot to update its in-memory invite links
        notify_bot(invite_link)

        return jsonify({"status": "success", "message": "Invite link registered"}), 200
    except Exception as e:
        print("[ERROR] Failed to register invite link:", str(e))
        return jsonify({"error": str(e)}), 500

def notify_bot(invite_link):
    """
    Notify the bot about the new invite link registration.
    """
    payload = {"invite_link": invite_link}
    try:
        response = requests.post(BOT_UPDATE_URL, json=payload)
        if response.status_code == 200:
            print(f"[INFO] Successfully notified bot about new invite link: {invite_link}")
        else:
            print(f"[WARNING] Failed to notify bot. Status Code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Could not notify bot: {e}")

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
