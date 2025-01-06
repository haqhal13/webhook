from flask import Flask, request, jsonify
import requests

# Flask app
app = Flask(__name__)

# Telegram Bot Token for Invite Bot
INVITE_BOT_TOKEN = "7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE"

# Telegram Bot API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{INVITE_BOT_TOKEN}/sendMessage"

@app.route("/")
def home():
    """
    Health check endpoint to confirm the server is running.
    """
    return "Webhook is running!"

@app.route("/register_invite", methods=["POST"])
def register_invite():
    """
    Endpoint to receive invite link registration commands
    and forward them to the invite bot.
    """
    try:
        # Parse JSON payload
        data = request.json
        invite_link = data.get("invite_link")
        chat_id = data.get("chat_id")  # The chat ID of the invite bot

        # Validate the required fields
        if not invite_link or not chat_id:
            return jsonify({"error": "Missing invite_link or chat_id"}), 400

        # Prepare payload for Telegram API
        payload = {
            "chat_id": chat_id,
            "text": f"/register_invite {invite_link}"
        }

        # Send the command to the invite bot
        response = requests.post(TELEGRAM_API_URL, json=payload)

        # Check response status
        if response.status_code == 200:
            return jsonify({
                "message": "Command forwarded successfully",
                "response": response.json()
            }), 200
        else:
            return jsonify({
                "error": "Failed to send message to invite bot",
                "details": response.json()
            }), 500

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run the app locally for development
    app.run(host="0.0.0.0", port=5000)
