from locorobo import LocoRobo
from locorobo import MotorDirection
from locorobo import Data
from locorobo import WaitType
from locorobo import Song
from locorobo import Note
import random  # added by me
import time


def get_robot (robots, name):
	robot = None

	# Search through robots found during the scan for
	# the one we want
	for r in robots.values():
		if r.name == name:
			robot = r

			# We found the robot, so stop the for loop
			break

	# If we did not find the robot during the scan, stop the program
	if not robot:
		raise Exception('Could not find robot with specified name')

	return robot


def main ():
	# Tell LocoRobo what serial port to use
	LocoRobo.setup("/dev/tty.usbmodem11")

	# Scan for robots
	robots = LocoRobo.scan(2000)

	# Use get_robots to find robot with name lr 00:07 in the scan result
	robot = get_robot(robots, "lr d2:90")

	robot.connect()
	robot.activate_motors()
	robot.enable_sensor(Data.ULTRASONIC, True)
	robot.enable_sensor(Data.ACCELEROMETER, True)

	def check_tilt (tilt):
		print('tilt dict:', tilt)
		message = ''
		if tilt['y'] <= -.5:
			message += 'fell on left side'
		elif tilt['y'] >= .5:
			message += 'fell on right side'
		elif tilt['x'] <= -.5:
			# tilt[x]: 0.224917888641
			message += 'fell forward'
		elif tilt['x'] >= .5:
			message += 'fell backward'
		return message  # if message remains empty string, the boolean value of it

	# will be false

	def do_lights ():
		robot.set_light(0, 255, 0, 255)
		robot.sync_lights()
		robot.set_light(1, 200, 0, 255)
		robot.sync_lights()
		robot.set_light(2, 180, 0, 255)
		robot.sync_lights()
		robot.set_light(3, 20, 0, 255)
		robot.sync_lights()

	def up_ramp():
		while True:
			robot.setup_wait(WaitType.DISTANCE, 4 * 1000)
			robot.move(MotorDirection.FORWARD, MotorDirection.FORWARD, .7, .7, True)
			tilt = robot.get_sensor_value(Data.ACCELEROMETER)
			fell = check_tilt(tilt)
			if fell:
				robot.deactivate_motors()
				print(fell)
				do_lights()
				break

	up_ramp()

	robot.disconnect()


# If we are on the main thread, run the program
if __name__ == "__main__":

	try:
		main()
	except:
		LocoRobo.stop()
		raise

	LocoRobo.stop()

# For compatibility with webapp's python, we can't use finally.
# If you are using local python, you can do the following
#
# try:
#     main()
# finally:
#     LocoRobo.stop()
