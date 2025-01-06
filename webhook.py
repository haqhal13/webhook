from flask import Flask, request, jsonify
import logging
import requests

app = Flask(__name__)

# Telegram Bot Token and Local Bot Update URL
BOT_TOKEN = "7559019704:AAEgnG14Nkm-x4_9K3m4HXSitCSrd2RdsaE"
LOCAL_BOT_URL = f"http://127.0.0.1:5000/update_invite"

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,  # Use DEBUG level for detailed logs
)
logger = logging.getLogger(__name__)

# In-memory invite link storage for additional debugging
invite_links = {}


@app.route("/", methods=["GET"])
def home():
    """
    Health check endpoint to confirm the webhook server is running.
    """
    logger.info("[INFO] Health check endpoint hit. Webhook is live.")
    return "Webhook is running!", 200


@app.route("/register_invite", methods=["POST"])
def register_invite():
    """
    Endpoint to register invite links sent from external services (e.g., Make/Integromat).
    """
    logger.debug("[DEBUG] Received request on /register_invite endpoint.")
    try:
        # Parse the incoming JSON payload
        data = request.get_json()
        logger.info(f"[INFO] Received data for invite registration: {data}")

        # Extract invite link from the payload
        invite_link = data.get("invite_link")
        if not invite_link or not invite_link.startswith("https://t.me/"):
            logger.warning("[WARNING] Invalid invite link received.")
            return jsonify({"error": "Invalid invite link"}), 400

        # Check if the invite link already exists
        if invite_link in invite_links:
            logger.info(f"[INFO] Invite link already exists: {invite_link}")
            logger.debug(f"[DEBUG] Current invite_links state: {invite_links}")
            return jsonify({"message": "Invite link already registered"}), 200

        # Add the invite link to the in-memory storage for testing
        invite_links[invite_link] = False  # Mark as unused
        logger.info(f"[INFO] Invite link registered: {invite_link}")
        logger.debug(f"[DEBUG] Updated invite_links state: {invite_links}")

        # Notify the local bot to update its library
        notify_local_bot(invite_link)

        return jsonify({"status": "success", "message": "Invite link registered"}), 200

    except Exception as e:
        logger.error(f"[ERROR] Exception occurred during invite registration: {str(e)}")
        return jsonify({"error": str(e)}), 500


def notify_local_bot(invite_link):
    """
    Notify the local bot to update its invite link library.
    """
    logger.debug("[DEBUG] Preparing to notify local bot.")
    try:
        # Prepare payload for the local bot
        payload = {"invite_link": invite_link}
        logger.info(f"[INFO] Sending invite link to local bot: {payload}")

        # Send a POST request to the local bot
        response = requests.post(LOCAL_BOT_URL, json=payload)
        response.raise_for_status()

        # Log the response from the local bot
        logger.info(f"[INFO] Local bot successfully updated. Response: {response.json()}")

    except requests.exceptions.RequestException as req_err:
        logger.error(f"[ERROR] RequestException while notifying local bot: {str(req_err)}")
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error while notifying local bot: {str(e)}")


if __name__ == "__main__":
    # Run the app locally for testing purposes
    app.run(host="0.0.0.0", port=5000, debug=True)
