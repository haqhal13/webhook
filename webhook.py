from flask import Flask, request, jsonify
import logging
import requests

# ---- Configuration ----
BOT_TOKEN = "7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE"  # Replace with your bot token
LOCAL_BOT_URL = "https://membership-bot-f4eq.onrender.com/register_invite"  # Replace with your bot's local URL
TIMEOUT = 30  # Timeout duration for requests to the bot

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,  # Set to DEBUG for detailed logging
)
logger = logging.getLogger("webhook")

# Flask app
app = Flask(__name__)

# ---- Flask Route: Health Check ----
@app.route("/")
def health_check():
    """
    Health check endpoint to confirm the webhook server is running.
    """
    logger.info("[INFO] Health check received.")
    return "Webhook is running!", 200


# ---- Flask Route: Webhook for Telegram ----
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """
    Handles incoming webhook updates from Telegram.
    """
    try:
        data = request.get_json()
        logger.info(f"Received update: {data}")
        # Process the update here (e.g., forward to the bot or log it)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return "Internal Server Error", 500


# ---- Flask Route: Register Invite Link ----
@app.route("/register_invite", methods=["POST"])
def register_invite():
    """
    Webhook endpoint to register invite links and notify the bot.
    """
    logger.debug("[DEBUG] Received request on /register_invite endpoint.")
    try:
        # Parse the incoming data
        data = request.get_json()
        logger.info(f"[INFO] Received data for invite registration: {data}")

        # Validate the invite link
        invite_link = data.get("invite_link")
        if not invite_link or not invite_link.startswith("https://t.me/"):
            logger.warning("[WARNING] Invalid invite link received.")
            return jsonify({"error": "Invalid invite link"}), 400

        # Log invite link processing
        logger.info(f"[INFO] Processing invite link: {invite_link}")

        # Prepare payload for the bot
        payload = {"invite_link": invite_link}
        logger.debug(f"[DEBUG] Payload to notify bot: {payload}")

        # Notify the bot
        response = notify_local_bot(payload)
        if response.status_code == 200:
            logger.info(f"[INFO] Successfully notified bot about invite link: {invite_link}")
            return jsonify({"status": "success", "message": "Invite link registered and bot notified"}), 200
        else:
            logger.error(f"[ERROR] Failed to notify bot. Status: {response.status_code}, Response: {response.text}")
            return jsonify({"error": "Failed to notify bot"}), 500

    except Exception as e:
        logger.error(f"[ERROR] Exception occurred in /register_invite: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def notify_local_bot(payload):
    """
    Notify the local bot about the new invite link.
    """
    logger.info("[INFO] Sending invite link to local bot.")
    try:
        # Send POST request to the local bot
        response = requests.post(LOCAL_BOT_URL, json=payload, timeout=TIMEOUT)
        logger.debug(f"[DEBUG] Response from local bot: {response.status_code}, {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"[ERROR] Failed to send invite link to local bot: {str(e)}", exc_info=True)
        raise


# ---- Flask Error Handlers ----
@app.errorhandler(404)
def not_found(error):
    logger.warning("[WARNING] 404 - Endpoint Not Found")
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error("[ERROR] 500 - Internal Server Error", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500


# ---- Run the Flask App ----
if __name__ == "__main__":
    logger.info("[INFO] Starting the webhook server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
