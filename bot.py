import logging
logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App
from threading import Thread

from utils import create_meet_from_text

# export SLACK_SIGNING_SECRET=819fa6c9a00498c631089b016cd5b8ac
# export SLACK_BOT_TOKEN=xoxb-4356365653585-4329303865415-6B33dNrEZiJJ03pNMYOmf50N
app = App()

# Add functionality here

@app.event('url_verification')
def verify(event):
    challenge = event["challenge"]
    return challenge, 200

@app.event("app_mention")
def introduce(event, say):
    text = """
        You can use /create to create a new calendar event.
        You can tag users in the workspace to add them to the invite list.
        Standard format /create @user1 @user2 d=10112022 (or 101122 for 10 Nov 2022) t=1045 l=45 (length of meeting in minutes) s="Your meeting title".
        In case no date and time is specified, todays' date and time after 1 hour is taken into account.
        In case length is not specified, it is assumed to be 60 minutes.
        In case no title is specified, a default title is assumed
    """
    say(text)

@app.command("/create")
def create(ack, respond, command):
    ack()
    print("command", command)
    text = command['text']
    sender_id = command["user_id"]
    daemon = Thread(target = create_meet_from_text, args = (text, sender_id, app.client, ), daemon=True)
    daemon.start()
    respond("test command")

if __name__ == "__main__":
    app.start(3000)  # POST http://localhost:3000/slack/events