import json
import threading
from donation_alert import DA_Alert

with open('server.secret', 'r') as file:
	data = json.load(file)

alert = DA_Alert(data["user_token"])

@alert.event()
def handler(event):
	print(f'{event.username} {event.amount_formatted} {event.currency}, --> {event.message}')
