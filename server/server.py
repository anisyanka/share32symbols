import sys
import json
import time
import queue
import serial
from donation_alert import DA_Alert
from dataclasses import dataclass

SERIAL_PORT = '/dev/tty.usbmodem48F256B635381'
DEFAULT_LIFETIME_SEC = 10 # A message will be displayed on OLED during these seconds
MIN_DONATE_IN_RUB_TO_INCREASE_TIME = 10
OLED_DEVICE_MAX_ANS_BYTES = 4
WRITE_ATTEMPTS = 5

# The queue of OLED messages
q = queue.Queue()

@dataclass
class OLED_Message:

	username: str # author of a donation
	line1: str # 16 symbols for line 1
	line2: str # 16 symbols for line 2
	lifetime: int # time in sec in during which the lines will be displayed
	currency: str

# Get secret token
with open('server.secret', 'r') as file:
	data = json.load(file)

# Acync handler of events from donationalerts alerts Centrifugo server
alert = DA_Alert(data["user_token"])
@alert.event()
def handler(event):
	print(f'[NEW DONATION]\nUser:{event.username}\nValue:{event.amount_formatted}\nCurrency:{event.currency}\nMessage:{event.message}\n')

	if event.currency != 'RUB':
		pass # convert currency to RUB

	username = event.username
	line1 = event.message[:16]
	line2 = event.message[16:32]
	currency = event.currency

	if int(event.amount_formatted) < MIN_DONATE_IN_RUB_TO_INCREASE_TIME:
		lifetime = DEFAULT_LIFETIME_SEC
	else:
		# so many rubles, so many seconds on OLED
		lifetime = int(event.amount_formatted)

	q.put(OLED_Message(username, line1, line2, lifetime, currency))

def put_msg_to_errfile(oled_msg):
	# save failed_donations.json
	failed_donate = {
		"user": oled_msg.username,
		"line1": oled_msg.line1,
		"line2": oled_msg.line2,
		"currency": oled_msg.currency,
		"lifetime": oled_msg.lifetime
	}

	with open("failed_donations.json", "a") as file:
		json.dump(failed_donate, file)
		file.write('\n')


def send_oled_data(oled_msg):
	ans = "FAIL"

	try:
		s = serial.Serial(SERIAL_PORT, timeout = 1)
		print("Sending data to port named: " + s.name)

		if s.is_open == True:
			s.write("1." + oled_msg.line1 + "2." + oled_msg.line2)
			s.flush()
			ans = s.read(OLED_DEVICE_MAX_ANS_BYTES)
		s.close()

	except OSError as oserr:
		print("[ERROR]: ", oserr)
	except ValueError as valerr:
		print("[ERROR]: ", valerr)

	return ans

# Dispatcher OLED messages
while True:
	is_sleep_need = True

	item = q.get()
	print(f'Working on: {item}')

	for i in range(0, WRITE_ATTEMPTS):
		if (send_oled_data(item) == "OK"):
			is_sleep_need = True
			break
		else:
			print(f'[ERROR]: can not send these data to OLED:\n1: {item.line1}\n2: {item.line2}\nAttempts №{i + 1}')
			if i + 1 == WRITE_ATTEMPTS:
				is_sleep_need = False
				put_msg_to_errfile(item)

	if is_sleep_need == True:
		time.sleep(item.lifetime)

	if q.empty() == True:
		print("QUEUE IS EMPTY") # clear OLED with default lines
	else:
		print("QUEUE IS NOT EMPTY")
	q.task_done()
