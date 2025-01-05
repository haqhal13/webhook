from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Invite bot token
INVITE_BOT_TOKEN = "7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE"

# Telegram API URL for sending messages
TELEGRAM_API_URL = f"https://api.telegram.org/bot7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE/sendMessage"

@app.route("/register_invite", methods=["POST"])
def register_invite():
    """
    Endpoint to receive /register_invite commands and forward them to the invite bot.
    """
    try:
        # Parse JSON payload
        data = request.json
        invite_link = data.get("invite_link")
        chat_id = data.get("chat_id")  # The invite bot's chat ID

        # Validate input
        if not invite_link or not chat_id:
            return jsonify({"error": "Missing invite_link or chat_id"}), 400

        # Prepare payload to send to the invite bot
        payload = {
            "chat_id": chat_id,
            "text": f"/register_invite {invite_link}"
        }

        # Send the /register_invite command to the invite bot
        response = requests.post(TELEGRAM_API_URL, json=payload)

        # Check for errors
        if response.status_code != 200:
            return jsonify({"error": "Failed to send message to invite bot", "details": response.json()}), 500

        return jsonify({"message": "Command forwarded successfully", "response": response.json()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)