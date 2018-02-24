"""
This Connect Four player implements negamax to find best-case moves.
"""
__author__ = "Jasper Raynolds"
__license__ = "MIT"
__date__ = "February 2018"

import copy
import random

### CONVENIENCE OBJECTS ###
# These are here purely to add to readability. I prefer location.x to location[0]

class Point:
	def __init__(self, x, y):
		"""
		Constructor. Takes an X and Y integer.
		"""
		self.x = x
		self.y = y

	def __eq__(self, other):
		"""
		Returns true if the two Points have equal X and Y values.
		"""
		if other == None:
			return False
		return self.x == other.x and self.y == other.y

	def __hash__(self):
		"""
		Hash function. Mashes together X and Y.
		"""
		return hash("%s,%s" % (self.x, self.y))

### GAME-STATE OBJECTS ###

class Rack:
	def __init__(self, array):
		"""
		Constructor. Takes a 2D array, column-major, of 0,1,2 integers.
		Here 0 represents an empty space, 1 a space filled with the
		first player's token, and 2 the second player's.
		"""
		self.array = array
		self.height = len(array[0])
		self.width = len(array)
		self.spaces = self.__array_to_spaces__()
		self.quartets = self.__array_to_quartets__()

		self.value = -float("inf")
		self.column = None

	def to_string(self):
		"""
		Stringifies the rack in an easy-to-read fashion.
		"""
		board = ""
		for y in range(self.height-1, -1, -1):
			for x in range(self.width):
				board += str(self.array[x][y])
				board += " "
			if y > 0:
				board += "\n"
		return board

	def __array_to_spaces__(self):
		"""
		From this object's array, returns a dictionary of Spaces.
		"""
		spaces = {}
		for y in range(self.height):
			for x in range(self.width):
				spaces[(x, y)] = Space(Point(x, y), self.array[x][y])
		return spaces

	def __array_to_quartets__(self):
		"""
		From this object's array, returns a list of Quartets.
		"""
		quartets = []
		# rows
		for y in range(self.height):
			for x in range(self.width - 3):
				quartets.append(self.__get_quartet__(Point(x, y), "horiz"))

		# columns
		for y in range(self.height - 3):
			for x in range(self.width):
				quartets.append(self.__get_quartet__(Point(x, y), "vert"))

		# diagonal down
		for y in range(self.height - 1, 2, -1):
			for x in range(self.width - 3):
				quartets.append(self.__get_quartet__(Point(x, y), "diag_down"))

		# diagonal up
		for y in range(self.height - 3):
			for x in range(self.width - 3):
				quartets.append(self.__get_quartet__(Point(x, y), "diag_up"))

		return quartets

	def __get_quartet__(self, start, direction):
		"""
		Returns a quartet given a valid starting Point with three spaces after it.
		The "direction" parameter takes "horiz", "vert", "diag_up" or "diag_down".
		"""
		spaceList = []
		offsets = {"horiz": Point(1, 0), "vert": Point(0, 1), "diag_up": Point(1, 1), "diag_down": Point(1, -1)}
		offset = offsets[direction]
		for index in range(4):
			x = start.x + (offset.x * index)
			y = start.y + (offset.y * index)
			spaceList.append(self.spaces[(x, y)])
		return Quartet(spaceList)

	def __get_state_value__(self, player):
		"""
		Returns the highest value of all quartets in this rack, for this playerID.
		"""
		value = -float("inf")
		for quartet in self.quartets:
			value = max(quartet.get_value(player), value)
		return value

	def __get_children__(self, playerID):
		"""
		Returns a list of column-rack pairs given the addition of one token.
		"""
		children = []

		for x in range(self.width):
			firstEmpty = None
			for y in range(self.height):
				tempSpace = self.spaces[(x, y)]
				if tempSpace.is_playable(self.spaces):
					firstEmpty = tempSpace
					break
			if firstEmpty == None:
				continue
			# newArray = copy.deepcopy(self.array)
			newArray = list(map(list, self.array))
			newArray[x][y] = playerID
			newRack = Rack(newArray)
			newRack.column = x
			children.append(newRack)
			# children.append((x, newRack))
			# children[x] = newRack

		return children

	def negamax(self, player, depth, a, b, pruningEnabled):
		"""
		Finds the best column for the player to play in.
		Utilizes negamax to the depth passed in.
		Utilizes alpha-beta pruning to discard low-value branches, if pruningEnabled is passed "true."
		Returns a Rack object.
		"""

		# allow for switching between players 1 and 2.
		players = {1: 2, 2: 1}

		# If we've reached the end of our depth or this is a winning state, return the value of this state for the last player.
		self.value = self.__get_state_value__(players[player])
		if depth == 0 or self.value == float("inf"):
			return self

		# Get all possible states, for the player passed, from this state.
		children = self.__get_children__(player)

		# Randomize the children
		random.shuffle(children)

		# Initialize the best option, choosing a random move from those available.
		best = children[0]

		# For each possible play,
		for child in children:
			# negamax iteratively down, switching players and alpha/beta, reducing depth by one, and multiplying alpha/beta by -1.
			bestChild = child.negamax(players[player], depth - 1, -b, -a, pruningEnabled)

			# If the negamax value is better than our best so far recorded, replace our best.
			if best.value > bestChild.value:
				best = bestChild

			# If we've turned on alpha-beta pruning, this discards a branch if it's a worse value.
			if pruningEnabled:
				a = max(a, best.value)
				if a >= b:
					break

		# Multiply the best value by -1.
		best.value *= -1
		return best

class Quartet:
	def __init__(self, spaces):
		"""
		Constructor, takes a list of four spaces.
		"""
		self.tokenList = {0: 0, 1: 0, 2: 0}
		for space in spaces:
			self.tokenList[space.value] += 1
		self.spaces = spaces

	def get_value(self, player):
		"""
		Evaluates this quartet and returns the computed value of the state for the player passed.
		"""
		values = {4: float("inf"), 3: 100, 2: 10, 1: 1, 0: .1}
		
		if self.tokenList[1] > 0 and self.tokenList[2] > 0:
			# This quart is unwinnable.
			return 0

		return values[self.tokenList[player]]

class Space:
	def __init__(self, location, value):
		"""
		Constructor, takes a Point and a value: 1 or 2 if it's filled
		with the appropriate player's token and 0 for no token at all.
		"""
		self.location = location
		self.value = value

	def is_playable(self, spaces):
		"""
		Returns true if this space is empty and something is below it.
		That means a token is directly below or this is row 0.
		"""
		if self.value == 0:
			below = spaces.get((self.location.x, self.location.y-1))
			if below == None or below.value != 0:
				return True
		return False

### AI CLASS ###

class ComputerPlayer:
	def __init__(self, playerID, difficulty_level):
		"""
		Constructor, takes a difficulty level (the # of plies to look
		ahead), and a player ID, either 1 or 2.
		"""
		self.playerID = playerID
		self.difficulty_level = difficulty_level

	def pick_move(self, array):
		"""
		Pick the move to make. It will be passed an array with the current 
		layout, column-major. A 0 indicates no token is there, and 1 or 2
		indicate discs from the two players. Column 0 is on the left, and row 0 
		is on the bottom. It must return an int indicating in which column to 
		drop a disc.
		"""

		rack = Rack([list(i) for i in array])
		# Note that we increment the difficulty level by one to match the number of plies we should be looking ahead:
		# That means a difficulty level of "0" will appropriately examine the immediate moves, instead of breaking. 
		# We may pass "False" to the final parameter here in order to disable alpha-beta pruning.
		best = rack.negamax(self.playerID, self.difficulty_level + 1, -float("inf"), float("inf"), True)
		column = best.column
		return column

### CODE FOR TESTING ###

# computer = ComputerPlayer(2, 4)
# print("best column=",computer.pick_move(((2,0,0,0),(0,0,0,0),(0,0,0,0),(1,0,0,0),(1,0,0,0),(0,0,0,0))))
# print("best column=",computer.pick_move(((2,0,0,0),(0,0,0,0),(0,0,0,0),(1,0,0,0))))
