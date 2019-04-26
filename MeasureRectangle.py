from locorobo import LocoRobo
from locorobo import MotorDirection
from locorobo import Data
from locorobo import WaitType
from locorobo import Song
from locorobo import Note
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

	def undo(side2, side1, direction):
		robot.setup_wait(WaitType.DISTANCE, side2 * 1000)
		robot.move(MotorDirection.BACKWARD, MotorDirection.BACKWARD, .9, .9, True)

		direction = 'l' if direction is 'r' else 'r'
		turn(direction)

		robot.setup_wait(WaitType.DISTANCE, side1 * 1000)
		robot.move(MotorDirection.BACKWARD, MotorDirection.BACKWARD, .9, .9, True)

	def turn (direction):
		robot.setup_wait(WaitType.ROTATION, degrees)
		if 'r' in direction:
			robot.move(MotorDirection.FORWARD, MotorDirection.BACKWARD, .7, .7, True)
		else:
			robot.move(MotorDirection.BACKWARD, MotorDirection.FORWARD, .7, .7, True)

	def forward ():
		print('moving forward\n')
		robot.setup_wait(WaitType.DISTANCE, d)
		robot.move(MotorDirection.FORWARD, MotorDirection.FORWARD, .8, .8, True)

	def get_side_length ():
		length = 0
		while True:
			forward()  # move forward
			length += 2  # robot moves forward 2 cm every time, so I add that to the length each iteration
			print('length after adding 2:', length)
			distance = robot.get_sensor_value(Data.ULTRASONIC)  # get distance
			print('distance:', distance)
			if distance <= 6:  # distance from wall, far to be safe
				return length + 6

	def review_info ():
		print('RECTANGLE INFO:')
		print('\n\nFinal sides:', sides)
		if sides[0] > sides[1]:
			length, width = sides[0], sides[1]
		else:
			length, width = sides[1], sides[0]

		print('Length: {}, Width: {}'.format(length, width))
		print('Area:', length * width)
		perim = length * 2 + width * 2
		print('Perimeter:', perim)

	d = 2 * 1000
	degrees = 90 * 1000
	robot_length = 8.5725  # measured
	width_correction = 2  # the width is always off by a little bit because of its turning,
	# so I found that simply adding a correction does the trick

	sides = []
	direction = input('Robot will be going forward and then -- l(eft) or r(ight): ')
	query = 'How many inches are you giving the robot on the {} side? '.format(direction)  # allow gap
	# so that it can turn easily when it gets to end of first side
	starting_gap = int(input(query))  # turn input into int
	pure_sides = []

	for side in range(2):  # get length and width
		length = get_side_length()
		print('final length of side {}: {}'.format(side + 1, length))
		pure_sides.append(length - 6)  # 6 is the distance from wall, we don't want that included in the pure length
		sides.append(length + robot_length)  # add length of side and robot length
		print('sides:', sides)
		if side == 0:
			turn(direction)  # if it is the first side, then turn in the direction inputted earlier
		else:
			sides[1] += starting_gap + width_correction

	# below: unnecessary but why not
	undo(pure_sides[1], pure_sides[0], direction)  # go back to the starting point

	review_info()  # output of rectangle info
	robot.play_song(Song.EyeOfTheTiger, False)  # fun

	robot.deactivate_motors()
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
