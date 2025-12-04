import json
from datetime import datetime, timedelta
from twilio.rest import Client

# Twilio recovery code: 63P38GKCYBZMWLAX6XKYQ7PC
# Twilio sandbox info
FROM_WHATSAPP = "whatsapp:+14155238886"  # Twilio sandbox
TO_NUMBERS_FILE = "whatsapp_sent.json"
TWILIO_SID = "ACe38061247f815c5f3e067972cd102ee8"
TWILIO_AUTH_TOKEN = "0f4acb356d0035f08f02ba632cbcc1dc"
WHATSAPP_NUMBERS = ["+447572467885", "+447841744029", "+447949729434"]  # add in here, must register on twilio me, Lockers, Daphne

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(message_body):
    """
    Sends WhatsApp message to a list of numbers if not sent in last 24h.
    """

    # Load last sent timestamps
    try:
        with open(TO_NUMBERS_FILE, "r") as f:
            sent_data = json.load(f)
    except FileNotFoundError:
        sent_data = {}

    now = datetime.utcnow()

    for number in WHATSAPP_NUMBERS:
        last_sent_str = sent_data.get(number)
        last_sent = datetime.fromisoformat(last_sent_str) if last_sent_str else None

        if not last_sent or (now - last_sent) > timedelta(hours=24):
            # Send message
            msg = client.messages.create(
                from_=FROM_WHATSAPP,
                to=f"whatsapp:{number}",
                body=message_body
            )
            print(f"Message sent to {number}: {msg.sid}")

            # Update timestamp
            sent_data[number] = now.isoformat()

    # Save updated timestamps
    with open(TO_NUMBERS_FILE, "w") as f:
        json.dump(sent_data, f, indent=2)
