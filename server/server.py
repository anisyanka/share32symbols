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

# The queue of OLED messages
q = queue.Queue()

@dataclass
class OLED_Message:

	username: str # author of a donation
	text: str # text to show on OLED
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

	username = event.username
	text = event.message
	currency = event.currency
	lifetime = DEFAULT_LIFETIME_SEC
	rubles = event.amount

	q.put(OLED_Message(username, text, lifetime, currency, rubles))

def put_msg_to_errfile(oled_msg):
	# save failed_donations.json
	failed_donate = {
		"user": oled_msg.username,
		"text": oled_msg.text,
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
			# omit space symbols
			to_oled = oled_msg.text.rstrip().replace("\r", "").replace("\t", "").replace("\f", "").replace("\v", "")
			first_line, sep , second_line = to_oled.partition('\n')
			print(f"LINE-1: <{first_line.encode('UTF-8')}>\nSEP: <{sep.encode('UTF-8')}>\nLINE-2: <{second_line.encode('UTF-8')}>\nDATA-LEN: {len(to_oled.encode('utf-8'))}")

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

def print_default_text():
	def_text = "Share 32 symbols" + "\n" + "     (^-^)/     "
	send_oled_data(OLED_Message("no", def_text, 1, "no", "no"))

print_default_text()

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
			print(f'[ERROR]: can not send these data to OLED:\n{item.text}\nAttempts №{i + 1}')
			if i + 1 == WRITE_ATTEMPTS:
				is_sleep_need = False
				put_msg_to_errfile(item)

	if is_sleep_need == True:
		time.sleep(item.lifetime)
		print("Lifetime exceeded")

	q.task_done()
