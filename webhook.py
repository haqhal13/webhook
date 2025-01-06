from flask import Flask, request, jsonify
import requests
import logging

# Flask app for the webhook
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE"

# Endpoint to notify the bot of new invite links
BOT_UPDATE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ---- Home Route ----
@app.route("/")
def home():
    """
    Health check endpoint to confirm the server is running.
    """
    return "Webhook is running!"

# ---- Register Invite Link ----
@app.route("/register_invite", methods=["POST"])
def register_invite():
    """
    Endpoint to register invite links received from an external source (e.g., Make, Zapier).
    """
    try:
        # Get the JSON payload
        data = request.get_json()
        logging.info(f"[INFO] Received data for invite registration: {data}")

        # Validate the payload
        invite_link = data.get("invite_link")
        if not invite_link or not invite_link.startswith("https://t.me/"):
            logging.warning("[WARNING] Invalid invite link received.")
            return jsonify({"error": "Invalid invite link"}), 400

        # Notify the bot of the new invite link
        notify_bot(invite_link)

        # Return success response
        return jsonify({"status": "success", "message": "Invite link registered"}), 200
    except Exception as e:
        logging.error(f"[ERROR] Failed to register invite link: {str(e)}")
        return jsonify({"error": str(e)}), 500

def notify_bot(invite_link):
    """
    Notify the bot to update its invite links storage.
    """
    try:
        # Prepare the payload
        payload = {
            "chat_id": ADMIN_ID,
            "text": f"New invite link registered: {invite_link}",
        }

        # Send the request to the bot
        response = requests.post(BOT_UPDATE_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        logging.info(f"[INFO] Successfully notified bot about new invite link: {invite_link}")
    except Exception as e:
        logging.error(f"[ERROR] Failed to notify bot about invite link: {str(e)}")

if __name__ == "__main__":
    # Run the app locally for development
    app.run(host="0.0.0.0", port=5000, debug=True)
