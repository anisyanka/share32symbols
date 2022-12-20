import json
import time
import queue
from donation_alert import DA_Alert
from dataclasses import dataclass

DEFAULT_LIFETIME_SEC = 10 # A message will be displayed on OLED during these seconds
MIN_DONATE_IN_RUB_TO_INCREASE_TIME = 10

# The queue of OLED messages
q = queue.Queue()

@dataclass
class OLED_Message:

	line1: str # 16 symbols for line 1
	line2: str # 16 symbols for line 2
	lifetime: int # time in sec in during which the lines will ber displayed

# Get secret token
with open('server.secret', 'r') as file:
	data = json.load(file)

alert = DA_Alert(data["user_token"])
@alert.event()
def handler(event):
	print(f'[NEW DONATION]\nUser:{event.username}\nValue:{event.amount_formatted}\nCurrency:{event.currency}\nMessage:{event.message}\n')

	if event.currency != 'RUB':
		pass # convert currency to RUB

	line1 = event.message[:16]
	line2 = event.message[16:32]

	if int(event.amount_formatted) < MIN_DONATE_IN_RUB_TO_INCREASE_TIME:
		lifetime = DEFAULT_LIFETIME_SEC
	else:
		lifetime = int(event.amount_formatted) # so many rubles, so many seconds

	q.put(OLED_Message(line1, line2, lifetime))

# Dispatcher OLED messages
while True:
	item = q.get()
	print(f'Working on: {item}')

	# write new lines to OLED

	time.sleep(item.lifetime)

	if q.empty() == True:
		print("QUEUE IS EMPTY") # clear OLED with default lines
	else:
		print("QUEUE IS NOT EMPTY")
	q.task_done()
