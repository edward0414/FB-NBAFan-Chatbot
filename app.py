import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    
                    if 'sticker_id' in messaging_event["message"]:
                        sticker_id = messaging_event["message"]["sticker_id"]
                        url_sticker = messaging_event["message"]["attachments"][0]["payload"]["url"]
                        log("RECEIVING sticker message from {recipient}: {sticker_id}".format(recipient=recipient_id, sticker_id=sticker_id))
                        send_sticker(sender_id, sticker_id, url_sticker)

                        if sticker_id == 369239383222810 or sticker_id == 369239263222822 or sticker_id == 369239343222814:
                            send_message(sender_id, "Don't give me that Jimmy Sama thumb up.")

                    if 'text' in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"]  # the message's text
                        log("RECEIVING message from {recipient}: {text}".format(recipient=recipient_id, text=message_text))
                        message_text = ' ' + message_text + ' '

                    
                        if 'create' in message_text:
                            message_text = message_text.replace('create', ' ')
                            message_text = message_text.replace('light', ' ')
                            light_name = message_text.strip()
                            light_name = light_name.replace(' ', '_')
                            url = "http://celilsemi.erkiner.com/facebook/index.html#{}{}".format(sender_id, light_name)
                            
                            response = requests.get(url)
                            send_message(sender_id, url)
                        
                        elif ' on ' in message_text:
                            message_text = message_text.replace(' on ', ' ')
                            message_text = message_text.replace('turn', ' ')
                            message_text = message_text.replace('light', ' ')
                            light_name = message_text.strip()
                            light_name = light_name.replace(' ', '_')
                            url = "http://celilsemi.erkiner.com/facebook/api/on.php?b={}{}".format(sender_id, light_name)
                            
                            send_message(sender_id, "roger that!")
                            response = requests.get(url)
                            #send_message(url)
                        
                        elif ' off ' in message_text:
                            message_text = message_text.replace(' off ', ' ')
                            message_text = message_text.replace('turn', ' ')
                            message_text = message_text.replace('light', ' ')
                            light_name = message_text.strip()
                            light_name = light_name.replace(' ', '_')
                            url = "http://celilsemi.erkiner.com/facebook/api/off.php?b={}{}".format(sender_id, light_name)
                            
                            send_message(sender_id, "roger that!")
                            response = requests.get(url)
                            #send_message(sender_id, url)

                        elif ' hello ' in message_text or ' hi ' in message_text or ' hey ' in message_text:
                            send_message(sender_id, "Hi, who do you think it is the best NBA player ever?")

                        elif ' lebron ' in message_text or ' Lebron ' in message_text:
                            send_message(sender_id, "LeBron sucks. Crying baby always crying for help. Gimme another name.")

                        elif 'curry' in message_text or 'Curry' in message_text:
                            send_message(sender_id, "Pfff, Curry is just a shooter. Durant carried his ass. Gimme another name.")

                        elif 'kobe' in message_text or 'Kobe' in message_text:
                            send_message(sender_id, "Man, he is really good. You know basketball! Gimme another name.")

                        elif 'lavar' in message_text or 'Lavar' in message_text:
                            send_message(sender_id, "Talking about Ball control eh?")

                        elif 'jimmy' in message_text or 'Jimmy' in message_text:
                            send_message(sender_id, "Jimmy Lin is a beast.")

                        elif 'Durant' in message_text or 'durant' in message_text:
                            send_message(sender_id, "Smh... he joined the most stacked team in the league in order to win. Gimme another name.")

                        elif 'jordan' in message_text or 'Jordan' in message_text:
                            send_message(sender_id, "The GOAT. Right answer!")

                        elif 'fuck' in message_text or 'shit' in message_text or 'dick' in message_text or 'ass' in message_text:
                            send_message(sender_id, "Cursing? You are very rude. Must be a typical Warriors bandwagon.")

                        else:
                            send_message(sender_id, "lol")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_sticker(recipient_id, sticker_id, url_sticker):

    log("SENDING message to {recipient}: {sticker_id}".format(recipient=recipient_id, sticker_id=sticker_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": url_sticker}
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)