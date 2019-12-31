import RPi.GPIO as GPIO
import time
import busio
import board
import adafruit_vl53l0x
import stepper_driver as STP
import threading
from datetime import datetime
import pickle

A0591_PINS = [4,17,27,22]
A4988_PINS = [5, 6, 13, 19, 26]
SWITCH_PIN = 21

BASE_STEPS = 7
BASE_ANGLE = BASE_STEPS * (360 / STP.A0591.steps_per_revolution)
SENSOR_STEPS = 8

TIMING_BUDGET = 200000.0 # NS

vl53 = None
stp_base = None
stp_sensor = None

def save(data):
    filename = "Scan {}.pkl".format(datetime.now())
    with open(filename, 'wb') as file:
        pickle.dump(data, file)

def main():
	# Startup

	# VL53L0x
	i2c = busio.I2C(board.SCL, board.SDA)
	vl53 = adafruit_vl53l0x.VL53L0X(i2c)
	vl53.measurement_timing_budget = TIMING_BUDGET

	# Steppers
	stp_base = STP.A0591(A0591_PINS, True)
	stp_sensor = STP.A4988(A4988_PINS, 16)

	# Limit switch
	GPIO.setup(SWITCH_PIN, GPIO.IN)

	print("Moving towards limit switch")

	# Position distance sensor
	while GPIO.input(SWITCH_PIN) == 0:
		stp_sensor.step(-1)
	while GPIO.input(SWITCH_PIN) == 1:
		stp_sensor.step(1)

	# Find object height
	for height in range(0, 2401, SENSOR_STEPS):
		stp_sensor.step(SENSOR_STEPS)
		rng = vl53.range
		print("Looking for end of object... Height = {}, Range = {}".format(height, rng))
		if rng > 1000:
			break

	# Start measurements (top-down)
	angle = 0
	direction = 1
	measurements = []

	while height > 0 and GPIO.input(SWITCH_PIN) == 0:
		stp_sensor.step(-SENSOR_STEPS)
		height -= SENSOR_STEPS
		angle = 0 if direction > 0 else 360
		while angle <= 360 and angle >= 0:
			dist = vl53.range
			print("Height: {}\t Angle: {}\t Dist: {}".format(height, angle, dist))
			measurements.append({'Height': height, 'Angle': angle, 'Range': dist})
			angle += BASE_ANGLE * direction
			stp_base.step(BASE_STEPS * direction)
		direction *= -1

	print(measurements)
	save(measurements)

if __name__ == '__main__':
	try:
		main()
	finally:
		STP.gpio_teardown()