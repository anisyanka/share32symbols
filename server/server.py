import sys
import json
import time
import queue
import serial
from serial import SerialException
from donation_alert import DA_Alert
from dataclasses import dataclass

SERIAL_PORT = '/dev/tty.usbmodem48F256B635381'
DEFAULT_LIFETIME_SEC = 10 # A message will be displayed on OLED during these seconds
MIN_DONATE_IN_RUB_TO_INCREASE_TIME = 10
OLED_DEVICE_MAX_ANS_BYTES = 2
WRITE_ATTEMPTS = 5
DELIMITER_SYMBOL = '\0'

# The queue of OLED messages
q = queue.Queue()

@dataclass
class OLED_Message:

	username: str # author of a donation
	line1: str # 16 symbols for line 1
	line2: str # 16 symbols for line 2
	lifetime: int # time in sec in during which the lines will be displayed
	currency: str # currency of a donation
	rubles: str # used to save failed donation

# Get secret token
with open('server.secret', 'r') as file:
	data = json.load(file)

# Acync handler of events from donationalerts alerts Centrifugo server
alert = DA_Alert(data["user_token"])
@alert.event()
def handler(event):
	print(f'\n\n[NEW DONATION]\nUser:{event.username}\nValue:{event.amount}\nCurrency:{event.currency}\nMessage:{event.message}')

	if event.currency != 'RUB':
		pass # convert currency to RUB

	username = event.username
	line1 = event.message[:16]
	line2 = event.message[16:32]
	currency = event.currency
	rubles = event.amount

	try:
		if int(event.amount_main) < MIN_DONATE_IN_RUB_TO_INCREASE_TIME:
			lifetime = DEFAULT_LIFETIME_SEC
		else:
			# so many rubles, so many seconds on OLED
			lifetime = int(event.amount_main)
	except ValueError:
		print("[ERROR]: can't convert received string to int value")
		put_msg_to_errfile(OLED_Message(username, line1, line2, 0, currency, rubles))
		return

	q.put(OLED_Message(username, line1, line2, lifetime, currency, rubles))

def put_msg_to_errfile(oled_msg):
	# save failed_donations.json
	failed_donate = {
		"user": oled_msg.username,
		"line1": oled_msg.line1,
		"line2": oled_msg.line2,
		"currency": oled_msg.currency,
		"lifetime": oled_msg.lifetime,
		"rubles": oled_msg.rubles
	}

	with open("failed_donations.json", "a") as file:
		json.dump(failed_donate, file)
		file.write('\n')


def send_oled_data(oled_msg):
	ans = "FAIL"

	try:
		s = serial.Serial(SERIAL_PORT, timeout = 1)

		if s.is_open == True:
			to_oled = oled_msg.line1 + DELIMITER_SYMBOL + oled_msg.line2
			print(f"Sending data <{to_oled}> to port named: {s.name}")
			s.write(bytes(to_oled,'UTF-8'))
			s.flush()
			ans = s.read(OLED_DEVICE_MAX_ANS_BYTES)
			print(f'OLED device ans: {ans}')
		s.close()

	except SerialException as sererr:
		print("[ERROR]: ", sererr)
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
		if (send_oled_data(item) == b'OK'):
			is_sleep_need = True
			print("SUCCESS")
			break
		else:
			print(f'[ERROR]: can not send these data to OLED:\n1: {item.line1}\n2: {item.line2}\nAttempts №{i + 1}')
			if i + 1 == WRITE_ATTEMPTS:
				is_sleep_need = False
				put_msg_to_errfile(item)

	if is_sleep_need == True:
		time.sleep(item.lifetime)
		print("Lifetime exceeded")

	q.task_done()
