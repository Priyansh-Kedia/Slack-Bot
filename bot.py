import logging
logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from threading import Thread

from utils import create_meet_from_text

# export SLACK_SIGNING_SECRET=819fa6c9a00498c631089b016cd5b8ac
# export SLACK_BOT_TOKEN=xoxb-4356365653585-4329303865415-eqZs0ZLkOtecrNx8AI5tjGgW
app = App()

# Add functionality here

@app.event('url_verification')
def verify(event):
    challenge = event["challenge"]
    return challenge, 200

@app.event("app_mention")
def introduce(event, say):
    say("Hello user")

@app.command("/create")
def create(ack, respond, command):
    ack()
    print("command", command)
    text = command['text']
    sender_id = command["user_id"]
    # daemon = Thread(target = create_meet_from_text, args = (text, sender_id, app.client, ), daemon=True)
    # daemon.start()
    respond("test command")

if __name__ == "__main__":
    app.start(3000)  # POST http://localhost:3000/slack/events