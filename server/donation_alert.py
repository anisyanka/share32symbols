import json
import socketio
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import Any

@dataclass
class DA_DonationEvent:

	username: str
	amount_formatted: str
	currency: str
	message: str

sio = socketio.Client()

class DA_Alert:

	def __init__(self, token):
		self.token = token

	def event(self):
		def wrapper(function):

			@sio.on("connect")
			def on_connect():
				sio.emit("add-user", {"token": self.token, "type": "alert_widget"})

			@sio.on("donation")
			def on_message(data):
				data = json.loads(data)
				function(
					DA_DonationEvent(
						data["username"],
						data["amount_formatted"],
						data["currency"],
						data["message"]
					)
				)

			sio.connect("wss://socket.donationalerts.ru:443", transports="websocket")

		return wrapper