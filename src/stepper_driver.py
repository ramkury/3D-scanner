import RPi.GPIO as GPIO
import time

def gpio_startup():
	GPIO.setmode(GPIO.BCM)

def gpio_teardown():
	GPIO.cleanup()

class A0591:
	steps_per_revolution = 512
	halfstep_time = 0.006

	def __init__(self, pins, microstepping = False):
		self.pins = pins
		self.microstepping = microstepping
		for pin in pins:
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, 0)
		
		self.halfstep_seq = [
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
			[0,0,1,1],
			[0,0,0,1],
			[1,0,0,1]
		] if microstepping else [
			[1,0,0,0],
			[0,1,0,0],
			[0,0,1,0],
			[0,0,0,1],
		]
	
	def step(self, n_steps):
		for i in range(abs(n_steps)):
			for halfstep in self.halfstep_seq if n_steps > 0 else reversed(self.halfstep_seq):
				for pin in range(4):
					GPIO.output(self.pins[pin], halfstep[pin])
				time.sleep(A0591.halfstep_time)
		
	def turn(self, degrees):
		steps = round((degrees / 360) * A0591.steps_per_revolution)
		self.step(steps)

class A4988:
	steps_per_revolution = 200
	halfstep_time = 0.00185

	# PIN order = [MS3, MS2, MS1, DIR, STP]
	def __init__(self, pins, microsteps = 1):
		self.microsteps = microsteps
		
		if microsteps == 1:
			ms = [0, 0, 0]
		elif microsteps == 2:
			ms = [0, 0, 1]
		elif microsteps == 4:
			ms = [0, 1, 0]
		elif microsteps == 8:
			ms = [0, 1, 1]
		elif microsteps == 16:
			ms = [1, 1, 1]
		else:
			raise ValueError('Microsteps can only be 1, 2, 4, 8 or 16')

		for pin in pins:
			GPIO.setup(pin, GPIO.OUT)
			GPIO.output(pin, 0)

		for i in range(3):
			GPIO.output(pins[i], ms[i])

		self.P_DIR = pins[3]
		self.P_STP = pins[4]

	def step(self, n_steps):
		GPIO.output(self.P_DIR, n_steps < 0)
		for i in range(abs(n_steps) * self.microsteps):
			GPIO.output(self.P_STP, 1)
			time.sleep(A4988.halfstep_time / self.microsteps)
			GPIO.output(self.P_STP, 0)
			time.sleep(A4988.halfstep_time / self.microsteps)

	def turn(self, degrees):
		steps = round((degrees / 360) * A4988.steps_per_revolution)
		self.step(steps)

if __name__ == '__main__': # Testing / Demo
	try:
		gpio_startup()
		stp = A4988([5, 6, 13, 19, 26], 16)
		# stp = A0591([4,17,27,22], True)
		stp.step(1000)
	finally:
		gpio_teardown()