"""
This Connect Four player implements negamax to find the best move for a given depth.
"""
__author__ = "Jasper Raynolds"
__license__ = "MIT"
__date__ = "March 2018"

import random

class Connect_Four:
	"""
	A state object for the board game Connect Four.

	Attributes:
		board: A 2D list of integers describing tiles placed and empty spaces.
	"""

	def __init__(self, board):
		"""
		Constructor. Takes a 2D list, row-major, top-down,
		of integers.
		"""
		self.board = board

		WINNING_LENGTH = 4
		self.pieces = self._get_pieces(WINNING_LENGTH)

	def _get_pieces(self, piece_width):
		"""
		Divides the board up into a list of pieces of length n, where n is the
		minimum length of a winning line.
		In connect-4, that number is 4.
		"""
		pieces = []

		WIDTH = len(self.board[0])
		HEIGHT = len(board)

		for row in range(HEIGHT):
			x_has_space = True
			y_has_space = True
			for col in range(WIDTH):
				# Do we have room horizontally and vertically from this cell?
				if col + piece_width > WIDTH:
					x_has_space = False
				if row + piece_width > HEIGHT:
					y_has_space = False

				if x_has_space and y_has_space:
					# If both, do diagonals
					piece = []
					for i in range(piece_width):
						piece.append(self.board[row+i][col+i])
					pieces.append(piece)

					piece = []
					for i in range(piece_width):
						piece.append(self.board[row+piece_width-1-i][col+i])
					pieces.append(piece)

				if x_has_space:
					# If horizontally, do horizontal
					piece = []
					for i in range(piece_width):
						piece.append(self.board[row][col+i])
					pieces.append(piece)

				if y_has_space:
					# If vertically, do vertical
					piece = []
					for i in range(piece_width):
						piece.append(self.board[row+i][col])
					pieces.append(piece)
			
		return pieces

	def to_string(self):
		"""
		Returns a stringified version of the board
		for easy reading.
		"""
		string = ""

		for row in self.board:
			for cell in row:
				string += str(cell)
				string += " "
			string = string[:-1]
			string += "\n"

		return string[:-1]

	def get_value(self, player_ID):
		"""
		Gets the highest value present in all pieces
		in this state, where pieces are judged by number
		of the passed player ID's number within the piece.
		"""
		SCORES = {4: float("inf"), 3: 100, 2: 10, 1: 10, 0: 0}
		best = 0

		for piece in self.pieces:
			if 1 in piece and 2 in piece:
				# If both players have played in this piece, neither can win it.
				continue

			matches = 0
			for p in piece:
				if p == player_ID:
					matches += 1
			best = max(best, SCORES[matches])

		return best

	def get_children(self, player_ID):
		"""
		Returns a list of all possible board states
		reachable from this one with a single move by the
		player passed.
		"""
		children = []

		for column in range(len(self.board[0])):
			if self.board[0][column] == 0:
				# If we've found a column with an empty cell at the top...
				emptyRow = 0
				for row in range(1, len(self.board), 1):
					# ...iterate down and find the row of the last empty cell.
					if self.board[row][column] == 0:
						emptyRow = row
					else :
						break

				child_board = [x[:] for x in self.board]
				child_board[emptyRow][column] = player_ID
				child = Connect_Four(child_board)
				children.append(child)

		return children

	def find_differing_column(self, other):
		"""
		Interprets another Connect_Four object from this one.
		Returns the column in which the first difference appears.
		"""
		HEIGHT = len(self.board)
		WIDTH = len(self.board[0])

		for row in range(HEIGHT):
			for column in range(WIDTH):
				if self.board[row][column] != other.board[row][column]:
					return column
		return None

	def negamax(self, player_ID, depth, a, b, isPruning):
		"""
		Negamax function. Compares state point values recursively.
		"""
		players = {1:2, 2:1}

		game_is_over = self.get_value(player_ID) == float("inf") or self.get_value(players[player_ID]) == float("inf")
		if depth == 0 or game_is_over:
			return self.get_value(player_ID)

		best = -float("inf")

		children = self.get_children(players[player_ID])
		random.shuffle(children)

		for child in children:
			value = child.negamax(players[player_ID], depth-1, -b, -a, isPruning)
			best = max(best, value)

			# Prunes low-value children. Alpha-beta.
			if isPruning:
				a = max(a, value)
				if a >= b:
					break

		return -best
		
class ComputerPlayer:
	"""
	A computer player object to be called upon in order to pick ideal game moves.

	Attributes:
		player_ID: the number corresponding to the tiles this player lays.
		difficulty_level: the number of plies this computer player will look ahead
			during its search. Defaults to 1, which only evaluates all immediate moves.
	"""

	def __init__(self, player_ID, difficulty_level):
		"""
		Constructor, takes a difficulty level (the # of plies to look
		ahead), and a player ID, either 1 or 2.
		"""
		self.player_ID = player_ID
		self.difficulty_level = difficulty_level

		assert (self.player_ID == 1 or self.player_ID == 2), "The player must be set to 1 or 2!"

		if self.difficulty_level == None or self.difficulty_level < 1:
			print("Difficulty level has been raised to its minimum of 1.")
			self.difficulty_level = 1

	def pick_move(self, array):
		"""
		Returns the best column for the player to play in, given
		the state passed.
		"""
		# Convert to 2D list array, rotate counter-clockwise 90 degrees
		state = []
		for x in range(len(array[0])-1, -1, -1):
			row = []
			for y in range(len(array)):
				row.append(array[y][x])
			state.append(row)
		connect = Connect_Four(state)

		# Get all possible moves, then randomly order them.
		children = connect.get_children(self.player_ID)
		random.shuffle(children)

		bestValue = -float("inf")
		bestChild = children[0]
		for child in children:
			# We may pass "False" to the final parameter here in order to disable alpha-beta pruning.
			value = child.negamax(self.player_ID, self.difficulty_level - 1, -float("inf"), float("inf"), True)
			if value > bestValue:
				bestValue = value
				bestChild = child
		# Return the int value of the best move's column choice.
		return connect.find_differing_column(bestChild)
