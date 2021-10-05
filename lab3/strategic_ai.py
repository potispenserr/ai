#from typing import Counter
import pygame
import math
import os
import queue
import time
import random

WIDTH = 700
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dumb AI tries to make 5D chess moves")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
DARK_GREEN = (9, 51, 0)
LIGHT_BLUE = (124, 185, 232)
ACID_GREEN = (176, 191, 26)
BROWN = (179, 89, 0)
IRON_GREY = (60, 60, 60)




class NPC:
	def __init__(self, row, col, width, name):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.width = width
		self.color = YELLOW
		self.name = name
		self.job = "Worker"
		self.path_queue = queue.Queue()
		self.open_queue = queue.Queue()
		self.task_queue = queue.Queue()
		self.next_Spot = Spot
		self.previous_state = ""
		self.current_state = ""
		self.resource_pos_dict = {}
		self.resource_pos_dict.setdefault("Tree", [])
		self.resource_pos_dict.setdefault("Iron", [])
		self.discovered_Spots = {}
		self.previous_Spots = []
		self.schooling_left = 20
		self.resource_gathering_timer = 10
		self.crafting_timer = 0
		self.inventory = ""
		self.build_timer = 0


	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def go_to_Spot_instantly(self, grid, spot):
		reset_Spot(grid[self.row][self.col])

		self.row = spot.row
		self.col = spot.col
		time.sleep(0.07)

		grid[self.row][self.col].color = YELLOW

	def move_to_Spot(self, grid, spot):
		pass
		
		
	def get_pos(self):
		return self.row, self.col
	
	def change_job(self, new_job):
		self.job = new_job

	def change_state(self, new_state):
		self.previous_state = self.current_state
		self.current_state = new_state
	
	def update(self, grid, interest_Spots_dict, storage_dict):

		if self.current_state == "Exploring": # Exploring
			explore_wide(self, grid)
			if(manhattan_distance(self.get_pos(), self.next_Spot.get_pos()) < 2):
				self.go_to_Spot_instantly(grid, self.next_Spot)
				self.previous_Spots.append(self.next_Spot)

			else:
				path_list = astar(grid, grid[self.row][self.col], self.next_Spot)
				for spot in path_list[::-1]:
					self.path_queue.put(spot)
				self.next_Spot = self.path_queue.get()
				self.go_to_Spot_instantly(grid, self.next_Spot)
				self.previous_Spots.append(self.next_Spot)
				self.previous_state = "Exploring"
				self.current_state = "Moving along path"
				return
		
		elif self.current_state == "Moving along path": #Move along path
			if not self.path_queue.empty():
				self.next_Spot = self.path_queue.get()
				explore_spots(grid, self, self.resource_pos_dict)
				self.go_to_Spot_instantly(grid, self.next_Spot)
				self.previous_Spots.append(self.next_Spot)
			else:

				self.change_state(self.previous_state)

		
		elif self.current_state == "":
			#print("not much going on here")
			pass


		elif self.current_state == "Going to school":
			if self.schooling_left <= 1:
				self.current_state = ""
				print(self.name, "became a", self.job)

				# when character becomes a explorer put the current position in the open queue so breadth first search
				# has something to work with
				if self.job == "Explorer": 
					self.open_queue.put(grid[self.row][self.col])
					self.discovered_Spots.setdefault(grid[self.row][self.col], 1)
					self.change_state("Exploring")
					self.previous_Spots.append(grid[self.row][self.col])

			else:
				self.schooling_left -= 1
				print(self.name, "has", self.schooling_left, "study time left")


		
		elif self.current_state == "Cutting down a tree": # Tree cutting
			if self.resource_gathering_timer > 0:
				self.resource_gathering_timer -= 1
				print("Tree timer:", self.resource_gathering_timer)
			else:
				tree_Spot = grid[self.row][self.col]
				tree_Spot.trees_left -= 1
				self.inventory = "Wood"
				self.resource_gathering_timer = 30

				if(tree_Spot.trees_left <= 0):
					grid[tree_Spot.row][tree_Spot.col].type = "Ground"
					grid[tree_Spot.row][tree_Spot.col].color = BROWN
					for spot in interest_Spots_dict["Tree"]:
						if tree_Spot == spot:
							interest_Spots_dict["Tree"].remove(spot)
							print("removed tree")
							print("Spot is now:", tree_Spot.type)
				path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)

				self.previous_state = "Taking resource to storage"
				self.current_state = "Moving along path"



		elif self.current_state == "Mining iron": # Iron mining
			if self.resource_gathering_timer > 0:
				self.resource_gathering_timer -= 1
				print("Iron timer:", self.resource_gathering_timer)
			else:
				iron_Spot = grid[self.row][self.col]
				self.inventory = "Iron"
				self.resource_gathering_timer = 30

				grid[iron_Spot.row][iron_Spot.col].type = "Ground"
				grid[iron_Spot.row][iron_Spot.col].color = BROWN
				for spot in interest_Spots_dict["Iron"]:
					if iron_Spot == spot:
						interest_Spots_dict["Iron"].remove(spot)
						print("removed iron")
						print("Spot is now:", iron_Spot.type)
				path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)

				self.previous_state = "Taking resource to storage"
				self.current_state = "Moving along path"


		elif self.current_state == "Producing charcoal": # Produce charcoal
			if grid[self.row][self.col].materials_here["Wood"] == 0: # When worker first arrives at the charcoal kiln
				grid[self.row][self.col].materials_here = {
					"Wood": 1
				}
				print("Laying down wood to get some more for the kiln")
				self.inventory = ""
				path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)
				
				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put(["Producing charcoal", grid[self.row][self.col]])
				self.crafting_timer = 10

			
			elif grid[self.row][self.col].materials_here["Wood"] >= 2: # When kiln has the required amount of wood
				if self.crafting_timer <= 0:
					print("The charcoal is now done")
					self.inventory = "Charcoal"
					for key in grid[self.row][self.col].materials_here:
						grid[self.row][self.col].materials_here[key] = 0

					path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
					for spot in path_list[::-1]:
						self.path_queue.put(spot)

					self.previous_state = "Taking resource to storage"
					self.current_state = "Moving along path"

				else:
					print("Charcoal timer", self.crafting_timer)
					self.crafting_timer -= 1

			
			else: # When the worker has to get more wood
				grid[self.row][self.col].materials_here["Wood"] += 1
				self.inventory = ""
				if grid[self.row][self.col].materials_here["Wood"] >= 2:
					return

				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)

				self.task_queue.put(["Producing charcoal", grid[self.row][self.col]])
				print("might need to get more wood for the kiln")
		
		elif self.current_state == "Building kiln": # Kiln building
			self.build_tier_1_building(grid, interest_Spots_dict, self.current_state, "Kiln")

		elif self.current_state == "Building forge": # Build forge
			self.build_tier_1_building(grid, interest_Spots_dict, self.current_state, "Forge")
		
		elif self.current_state == "Building training camp": # Build training camp
			self.build_tier_1_building(grid, interest_Spots_dict, self.current_state, "Training camp")
	
		elif self.current_state == "Building smithy": # Build smithy aka the only "tier 2" building
			if not grid[self.row][self.col].materials_here:
				grid[self.row][self.col].materials_here = {
					"Wood": 1,
					"Iron bar": 0
				}
				print("Laying down wood to get some more")
				path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)
				
				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put(["Building smithy", grid[self.row][self.col]])
				self.build_timer = 20

			
			elif grid[self.row][self.col].materials_here["Wood"] >= 2:
				if grid[self.row][self.col].materials_here["Iron bar"] >= 2:
					if self.build_timer <= 0:
						interest_Spots_dict["Smithy"].append(grid[self.row][self.col])
						grid[self.row][self.col].type = "Building"
						print("Finally built smithy")
						for key in grid[self.row][self.col].materials_here:
							grid[self.row][self.col].materials_here[key] = 0
						self.change_state("")
					else:
						print("smithy build timer", self.build_timer)
						self.build_timer -= 1
				else:
					if self.inventory == "Iron bar":
						print("adding an iron bar into the mix")
						grid[self.row][self.col].materials_here["Iron bar"] += 1
						self.inventory = ""
					else:
						path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
						for spot in path_list[::-1]:
							self.path_queue.put(spot)
						
						self.previous_state = "Getting iron bar"
						self.current_state = "Moving along path"
						self.task_queue.put(["Building smithy", grid[self.row][self.col]])
			
			else:
				grid[self.row][self.col].materials_here["Wood"] += 1
				self.inventory = ""
				print("might need to get more wood")
			



		elif self.current_state == "Getting wood": # Getting wood
			if(storage_dict["Wood"] <= 0):
				print("No wood in storage")
				self.change_state("")
			else:
				self.inventory = "Wood"
				current_task = self.task_queue.get()
				self.previous_state = current_task[0]
				path_list = astar(grid, grid[self.row][self.col], current_task[1])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)
				self.current_state = "Moving along path"

		elif self.current_state == "Getting iron bar": # Getting iron bar
			if(storage_dict["Iron bar"] <= 0):
				print("No iron bars in storage")
				self.change_state("")
			else:
				self.inventory = "Iron bar"
				current_task = self.task_queue.get()
				self.previous_state = current_task[0]
				path_list = astar(grid, grid[self.row][self.col], current_task[1])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)
				self.current_state = "Moving along path"
				
		
		elif self.current_state == "Taking resource to storage": # Taking resource to storage
			storage_dict[self.inventory] += 1
			self.inventory = ""
			self.change_state("")

		else:
			print(self.name, "has a unimplemented state", self.current_state)


	def build_tier_1_building(self, grid, interest_Spots_dict, building_state_string, building_type):
			if not grid[self.row][self.col].materials_here: # When worker first arrives at the build spot
				grid[self.row][self.col].materials_here = {
					"Wood": 1
				}
				print("Laying down wood to get some more")
				self.inventory = ""
				path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
				for spot in path_list[::-1]:
					self.path_queue.put(spot)
				
				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put([building_state_string, grid[self.row][self.col]])
				self.build_timer = 10

			
			elif grid[self.row][self.col].materials_here["Wood"] >= 2:
				if self.build_timer <= 0:
					interest_Spots_dict[building_type].append(grid[self.row][self.col])
					grid[self.row][self.col].type = "Building"
					print("Finally built", building_type)
					for key in grid[self.row][self.col].materials_here:
						grid[self.row][self.col].materials_here[key] = 0
					self.change_state("")
				else:
					print(building_type, " build timer", self.build_timer)
					self.build_timer -= 1

			
			else:
				grid[self.row][self.col].materials_here["Wood"] += 1
				self.inventory = ""
				if grid[self.row][self.col].materials_here["Wood"] >= 2:
					return

				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put([building_state_string, grid[self.row][self.col]])
				print("might need to get more wood")

	def produce_tier_2_items(self, grid, interest_Spots_dict, building_state_string, building_type):
		#WORK IN PROGRESS
		if not grid[self.row][self.col].materials_here: # When worker first arrives at the build spot
			grid[self.row][self.col].materials_here = {
				"Wood": 1
			}
			print("Laying down wood to get some more")
			self.inventory = ""
			path_list = astar(grid, grid[self.row][self.col], interest_Spots_dict["Storage"])
			for spot in path_list[::-1]:
				self.path_queue.put(spot)
			
			self.previous_state = "Getting wood"
			self.current_state = "Moving along path"
			self.task_queue.put([building_state_string, grid[self.row][self.col]])
			self.build_timer = 10

		
		elif grid[self.row][self.col].materials_here["Wood"] >= 2:
			if self.build_timer <= 0:
				interest_Spots_dict[building_type].append(grid[self.row][self.col])
				grid[self.row][self.col].type = "Building"
				print("Finally built", building_type)
				for key in grid[self.row][self.col].materials_here:
					grid[self.row][self.col].materials_here[key] = 0
				self.change_state("")
			else:
				print(building_type, " build timer", self.build_timer)
				self.build_timer -= 1

		
		else:
			grid[self.row][self.col].materials_here["Wood"] += 1
			self.inventory = ""
			if grid[self.row][self.col].materials_here["Wood"] >= 2:
				return

			self.previous_state = "Getting wood"
			self.current_state = "Moving along path"
			self.task_queue.put([building_state_string, grid[self.row][self.col]])
			print("might need to get more wood")



class Spot:
	def __init__(self, row, col, width, total_rows, type, trees_left = None):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
		self.type = type
		self.trees_left = trees_left
		self.materials_here = None

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.type == "Wall" or self.type == "Mountain" or self.type == "Water"

	def is_resource(self):
		if self.type == "Tree":
			return True, self.type
		
		elif self.type == "Iron":
			return True, self.type

		else:
			return False, self.type

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def add_trees(self, trees):
		self.trees_left = trees

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE
	
	def make_tree(self):
		self.color = DARK_GREEN

	def make_water(self):
		self.color = LIGHT_BLUE
	
	def make_swamp(self):
		self.color = ACID_GREEN
	
	def make_ground(self):
		self.color = BROWN
	
	def make_mountain(self):
		self.color = BLACK

	def draw(self, win): # draws the spot on the pygame window
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	# adds walkable neighbors diagonally, up, down, left and right
	# if a wall is next to a diagonal neighbor, the neighbor doesn't get added
	def update_neighbors(self, grid):
		self.neighbors = []

		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # right
			self.neighbors.append(grid[self.row + 1][self.col])


		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # left
			self.neighbors.append(grid[self.row - 1][self.col])


	
		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # down
			self.neighbors.append(grid[self.row][self.col + 1])

			if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier() and not grid[self.row + 1][self.col].is_barrier(): # checks if down right is a wall and right is a wall
				self.neighbors.append(grid[self.row + 1][self.col + 1])

			if self.row > 0 and not grid[self.row - 1][self.col + 1].is_barrier() and not grid[self.row - 1][self.col].is_barrier(): # checks if down left is a wall and if left is a wall
				self.neighbors.append(grid[self.row - 1][self.col + 1])

					

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # up
			self.neighbors.append(grid[self.row][self.col - 1])

			if self.row > 0 and not grid[self.row - 1][self.col - 1].is_barrier() and not grid[self.row - 1][self.col].is_barrier(): # checks if up left is a wall and if left is a wall
				self.neighbors.append(grid[self.row - 1][self.col - 1])
			
			if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col - 1].is_barrier() and not grid[self.row + 1][self.col].is_barrier(): # checks if up right is a wall and if right is a wall
				self.neighbors.append(grid[self.row + 1][self.col - 1])
				

	def __lt__(self, other):
		return False




def h(p1, p2): # returns diagonal distance
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

	""" x1, y1 = p1
	x2, y2 = p2
	dx = abs(x1 - x2)
	dy = abs(y1 - y2)
	d = 1 # distance between spots
	d2 = 1 # diagonal distance between spots

	h = d * (dx + dy) + (d2 - 2 * d) * min(dx, dy)
	return h """

def manhattan_distance(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):	
	list_to_path = []
	while current in came_from:
		list_to_path.append(current)
		current = came_from[current]
		if current.color == YELLOW: # stop at npc
			return list_to_path
		#current.make_path()
		#draw()
	return list_to_path




def astar(grid, start, end): 
	open_pq = queue.PriorityQueue()
	open_pq.put((0, start))
	came_from = {}

	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0

	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	previous_spots = {start}

	while not open_pq.empty():

		current = open_pq.get()[1]

		if current == end:
			list_to_path = reconstruct_path(came_from, end, draw)
			return list_to_path

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

				if neighbor not in previous_spots:
					open_pq.put((f_score[neighbor], neighbor))
					previous_spots.add(neighbor)

					if(neighbor != end):
						#neighbor.make_open()
						pass

		if current != start:
			#current.make_closed()
			pass

	return False # no path found


def custom_greedy(draw, grid, start, end):
	open_pq = queue.PriorityQueue()
	open_pq.put((0, start))
	previous_spots = {start}
	h_score = {spot: float("inf") for row in grid for spot in row}
	came_from = {}
	while not open_pq.empty():

		current = open_pq.get()[1]

		if current == end:
			list_to_path = reconstruct_path(came_from, end, draw)
			return list_to_path

		for neighbor in current.neighbors:
			temp_h_score = h(neighbor.get_pos(), end.get_pos())

			if temp_h_score < h_score[neighbor]:
				came_from[neighbor] = current
				h_score[neighbor] = temp_h_score

				if neighbor not in previous_spots:
					open_pq.put((h_score[neighbor], neighbor))
					previous_spots.add(neighbor)

					if(neighbor != end):
						neighbor.make_open()
		
		draw()

		if current != start:
			current.make_closed()
	
	return False # no path found


	#breadth first traversal
def explore_wide(npc, grid):
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_b:
				pass
					#return resource_pos_dict, discovered_Spots
	if not npc.open_queue.empty():
		current = npc.open_queue.get()
		npc.next_Spot = current

		

		explore_spots(grid, npc, npc.resource_pos_dict)

		if not current in npc.discovered_Spots:
			npc.discovered_Spots.setdefault(current, 1)

		for neighbor in current.neighbors:
			if neighbor not in npc.previous_Spots:
				npc.open_queue.put(neighbor)
				npc.previous_Spots.append(neighbor)
			if not neighbor in npc.discovered_Spots:
				npc.discovered_Spots.setdefault(neighbor, 1)
		
	else:
		print("Every Spot is explored")


	#depth first traversal
def explore_deep(draw, start, npc, visitedSpots, grid):
	open_stack = queue.LifoQueue()
	open_stack.put(start)
	previous_spots = {start}
	while not open_stack.empty():

		current = open_stack.get()
		npc.go_to_Spot_instantly(grid, current)

		
		reset_Spot(grid[npc.row + 1][npc.col]) # check right
		reset_Spot(grid[npc.row - 1][npc.col]) # check left
		reset_Spot(grid[npc.row][npc.col + 1]) # check down
		reset_Spot(grid[npc.row][npc.col - 1]) # check up

		reset_Spot(grid[npc.row + 1][npc.col + 1]) # check down right
		reset_Spot(grid[npc.row - 1][npc.col + 1]) # check down left
		reset_Spot(grid[npc.row - 1][npc.col - 1]) # check up left
		reset_Spot(grid[npc.row + 1][npc.col - 1]) # check up right

				
		for neighbor in current.neighbors[::-1]:
			if neighbor not in previous_spots:
				
				open_stack.put(neighbor)
				previous_spots.add(neighbor)
		
		draw()

		if current != start:
			current.make_closed()
		
	
	return False # no path found

# creates a bunch of spots to append them to the grid list and returns the list after it's done
def make_grid(rows, width, grid):
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows , "Floor")
			grid[i].append(spot)



def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width, npclist = None):
	win.fill(WHITE)


	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)

	if(npclist != None):
		for npc in npclist:
			grid[npc.row][npc.col].color = npc.color

	pygame.display.update()
	#time.sleep(0.3)


	# returns clicked position with row and col coordinates
def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col

	# creates the map from a file and then returns the start and end point
def load_map(grid, mapnum):
	if mapnum == 1:
		f = open("Map1.txt", "r")
	
	f = open("Map4.txt", "r")
	
	startX = 0
	startY = 0

	already_discovered_Spots = {}

	ironprobability = 60
	start = None
	end = None
	# reads the file and makes a character a specific object
	for line in f:
		for char in line:
			if char == "X":
				grid[startY][startX].make_barrier()
				grid[startY][startX].type = "Wall"

			if char == "S": # Starting area
				grid[startY][startX].type = "Ground"
				grid[startY][startX].color = BROWN
				already_discovered_Spots.setdefault(grid[startY][startX], 1)
			
			if char == "H":
				grid[startY][startX].type = "Building"
				grid[startY][startX].color = PURPLE

			if char == "K":
				grid[startY][startX].make_end()
				end = grid[startY][startX]

			if char == "T":
				grid[startY][startX].type = "Tree"
				grid[startY][startX].color = GREY
				grid[startY][startX].add_trees(5)
			
			if char == "V":
				grid[startY][startX].type = "Water"
				grid[startY][startX].color = GREY
			
			if char == "G":
				grid[startY][startX].type = "Swamp"
				grid[startY][startX].color = GREY
			
			if char == "B":
				grid[startY][startX].type = "Mountain"
				grid[startY][startX].color = GREY
			
			if char == "M":
				if(ironprobability >= 1):
					randomint = random.randint(1, ironprobability)
					if randomint == ironprobability:
						grid[startY][startX].type = "Iron"
						grid[startY][startX].color = GREY
						ironprobability -= 1
					else:
						grid[startY][startX].type = "Ground"
						grid[startY][startX].color = GREY

				else:
					grid[startY][startX].type = "Ground"
					grid[startY][startX].color = GREY

			startY += 1
			
		startY = 0
		startX +=1

		grid[20][21].type = "Tree"
		grid[20][21].color = DARK_GREEN
		grid[20][21].trees_left = 5

		grid[21][21].type = "Iron"
		grid[21][21].color = IRON_GREY


	f.close()
	return start, end, already_discovered_Spots

def reset_Spot(spot):
	if spot.type == "Tree":
		spot.color = DARK_GREEN

	if spot.type == "Swamp":
		spot.color = ACID_GREEN

	if spot.type == "Mountain":
		spot.color = BLACK

	if spot.type == "Water":
		spot.color = LIGHT_BLUE

	if spot.type == "Ground":
		spot.color = BROWN
	
	if spot.type == "Building":
		spot.color = PURPLE
	
	if spot.type == "Iron":
		spot.color = IRON_GREY


def reset_map(grid):
	for row in grid:
		for spot in row:
			reset_Spot(spot)

def go_to_school(npc, school_Spot, grid, education_type):
	npcSpot = grid[npc.row][npc.col]
	path_list = astar(grid, npcSpot, school_Spot)
	for spot in path_list[::-1]:
		npc.path_queue.put(spot)

	npc.previous_state = "Going to school"
	npc.current_state = "Moving along path"
	npc.change_job(education_type)


def craft_item(item_type, resource_storage_dict, interest_Spots_dict, grid, npc_List):
	if item_type == "Charcoal":
		if not interest_Spots_dict["Kiln"]:
			print("No charcoal kiln has been built")
			return
		elif resource_storage_dict["Wood"] < 2:
			print("There's not enough wood to make charcoal")
			return

		first_available_npc = None
		for npc in npc_List:
			if npc.job == "Worker":
				if npc.current_state == "":
					first_available_npc = npc
		print("going to charcoal kiln")
		closest_kiln = interest_Spots_dict["Kiln"][0]
		for spot in interest_Spots_dict["Kiln"]:
				if(h(first_available_npc.get_pos(), spot.get_pos()) < h(first_available_npc.get_pos(), closest_kiln.get_pos())):
					closest_kiln = spot

		first_available_npc.task_queue.put(["Producing charcoal", closest_kiln])

		path_list = astar(grid, grid[first_available_npc.row][first_available_npc.col], interest_Spots_dict["Storage"])
		for spot in path_list[::-1]:
			first_available_npc.path_queue.put(spot)

		first_available_npc.previous_state = "Getting wood"
		first_available_npc.current_state = "Moving along path"
		




def gather_resource(resource_type, interest_spots_dict, npc_List, grid):
	first_best_npc = None
	for npc in npc_List:
		if npc.job == "Worker":
			if npc.current_state == "":
				first_best_npc = npc
	if (first_best_npc == None):
		print("No available workers to gather", resource_type)
		return

	closest_resource_Spot = interest_spots_dict[resource_type][0]
	for spot in interest_spots_dict[resource_type]:
			if(h(first_best_npc.get_pos(), spot.get_pos()) < h(first_best_npc.get_pos(), closest_resource_Spot.get_pos())):
				closest_resource_Spot = spot

	first_best_npc_Spot = grid[first_best_npc.row][first_best_npc.col]
	path_list = astar(grid, first_best_npc_Spot, closest_resource_Spot)
	for spot in path_list[::-1]:
		first_best_npc.path_queue.put(spot)

	if(resource_type == "Tree"):
		first_best_npc.previous_state = "Cutting down a tree"
		first_best_npc.current_state = "Moving along path"

	if(resource_type == "Iron"):
		first_best_npc.previous_state = "Mining iron"
		first_best_npc.current_state = "Moving along path"



def build_building(building_type, resource_storage_dict, interest_Spots_dict, discovered_Spots, grid, npc_List):
	first_available_npc = None
	for npc in npc_List:
		if npc.current_state == "":
			first_available_npc = npc
			break

	if resource_storage_dict["Wood"] >= 2:
		if building_type == "smithy":
			if resource_storage_dict["Iron bar"] >= 2:
				print("starting to build", building_type)
				build_Spot = None
				for spot in discovered_Spots:
					if(h(spot.get_pos(), interest_Spots_dict["Storage"].get_pos()) < 30 and grid[spot.row][spot.col].type == "Ground"):
						build_Spot = spot
						break
			else:
				print("not enough iron in storage")
		else:
			print("starting to build", building_type)
			build_Spot = None
			for spot in discovered_Spots:
				if(h(spot.get_pos(), interest_Spots_dict["Storage"].get_pos()) < 30 and grid[spot.row][spot.col].type == "Ground"):
					build_Spot = spot
					break
		
		first_available_npc.task_queue.put(["Building " + building_type, build_Spot])

		path_list = astar(grid, grid[first_available_npc.row][first_available_npc.col], interest_Spots_dict["Storage"])
		for spot in path_list[::-1]:
			first_available_npc.path_queue.put(spot)
		
		first_available_npc.previous_state = "Getting wood"
		first_available_npc.current_state = "Moving along path"
	else:
		print("not enough wood in storage")


def explore_spots(grid, npc, resource_pos_dict):
	if grid[npc.row + 1][npc.col].is_resource()[0]:
		resource_type = grid[npc.row + 1][npc.col].is_resource()[1]
		if grid[npc.row + 1][npc.col] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row + 1][npc.col])

	elif grid[npc.row - 1][npc.col].is_resource()[0]:
		resource_type = grid[npc.row - 1][npc.col].is_resource()[1]
		if grid[npc.row - 1][npc.col] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row - 1][npc.col])

	elif grid[npc.row][npc.col + 1].is_resource()[0]:
		resource_type = grid[npc.row][npc.col + 1].is_resource()[1]
		if grid[npc.row][npc.col + 1] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row][npc.col + 1])
			

	elif grid[npc.row][npc.col - 1].is_resource()[0]:
		resource_type = grid[npc.row][npc.col - 1].is_resource()[1]
		if grid[npc.row][npc.col - 1] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row][npc.col - 1])


	if grid[npc.row + 1][npc.col + 1].is_resource()[0]:
		resource_type = grid[npc.row + 1][npc.col + 1].is_resource()[1]
		if grid[npc.row + 1][npc.col + 1] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row + 1][npc.col + 1])

	elif grid[npc.row - 1][npc.col + 1].is_resource()[0]:
		resource_type = grid[npc.row - 1][npc.col + 1].is_resource()[1]
		if grid[npc.row - 1][npc.col + 1] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row - 1][npc.col + 1])

	elif grid[npc.row - 1][npc.col - 1].is_resource()[0]:
		resource_type = grid[npc.row - 1][npc.col - 1].is_resource()[1]
		if grid[npc.row - 1][npc.col - 1] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row - 1][npc.col - 1])

	elif grid[npc.row + 1][npc.col - 1].is_resource()[0]:
		resource_type = grid[npc.row + 1][npc.col - 1].is_resource()[1]
		if grid[npc.row + 1][npc.col - 1] not in resource_pos_dict[resource_type]:
			print(resource_type)
			resource_pos_dict[resource_type].append(grid[npc.row + 1][npc.col - 1])

	for neighbor in grid[npc.row][npc.col].neighbors:
		if not neighbor in npc.discovered_Spots:
			npc.discovered_Spots.setdefault(neighbor, 1)


	if not grid[npc.row + 1][npc.col].color == YELLOW:
		reset_Spot(grid[npc.row + 1][npc.col]) # check right
	
	if not grid[npc.row - 1][npc.col] == YELLOW:
		reset_Spot(grid[npc.row - 1][npc.col]) # check left
	
	if not grid[npc.row][npc.col + 1] == YELLOW:
		reset_Spot(grid[npc.row][npc.col + 1]) # check down

	if not grid[npc.row][npc.col - 1] == YELLOW:
		reset_Spot(grid[npc.row][npc.col - 1]) # check up

	if not grid[npc.row + 1][npc.col + 1] == YELLOW:
		reset_Spot(grid[npc.row + 1][npc.col + 1]) # check down right
	
	if not grid[npc.row - 1][npc.col + 1] == YELLOW:
		reset_Spot(grid[npc.row - 1][npc.col + 1]) # check down left
	
	if not grid[npc.row - 1][npc.col - 1] == YELLOW:
		reset_Spot(grid[npc.row - 1][npc.col - 1]) # check up left
	
	if not grid[npc.row + 1][npc.col - 1] == YELLOW:
		reset_Spot(grid[npc.row + 1][npc.col - 1]) # check up right

	return


def update_dicts(main_interest_Spots_dict, npc, main_discovered_Spots):
	for key in npc.resource_pos_dict.keys():
		if len(npc.resource_pos_dict[key]) > len(main_interest_Spots_dict[key]): # efficiency
			for val in npc.resource_pos_dict[key]:
				if val not in main_interest_Spots_dict[key]:
					main_interest_Spots_dict[key].append(val)
		else:
			break
	for key in npc.discovered_Spots.keys():
		if len(npc.discovered_Spots.keys()) > len(main_discovered_Spots.keys()):
			if key not in main_discovered_Spots:
				main_discovered_Spots.setdefault(key, 1)
		else:
			break


		


def main(win, width):
	ROWS = 100
	grid = []
	make_grid(ROWS, width, grid)
	start = Spot
	end = Spot
	discovered_Spots = {}
	start, end, discovered_Spots = load_map(grid, 4)
	oblivionNPCs = [NPC(24,24,width, "Steffe")]
	oblivionNPCs.append(NPC(22,22,width, "Sven"))
	#resource_pos_list = []
	resource_storage_dict = {
		"Wood": 10,
		"Iron": 0,
		"Charcoal": 0,
		"Iron bar": 10,
		"Swords": 0
	}


	interest_spots_dict = {}
	interest_spots_dict.setdefault("Storage", grid[23][24])
	interest_spots_dict.setdefault("School", grid[22][24])
	interest_spots_dict.setdefault("Tree", [])
	interest_spots_dict.setdefault("Iron", [])
	interest_spots_dict.setdefault("Kiln", [])
	interest_spots_dict.setdefault("Forge", [])
	interest_spots_dict.setdefault("Smithy", [])
	interest_spots_dict.setdefault("Training camp", [])

	for row in grid:
		for spot in row:
			spot.update_neighbors(grid)

	
	run = True
	update = 0
	while run:
		draw(win, grid, ROWS, width, oblivionNPCs)

		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		
			if event.type == pygame.KEYDOWN: 
				if event.key == pygame.K_1:
					start, end = load_map(grid, 1)
				
				if event.key == pygame.K_2:
					start, end = load_map(grid, 2)
				
				if event.key == pygame.K_3:
					start, end = load_map(grid, 3)

				if event.key == pygame.K_SPACE and start and end: # A*
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					startTime = time.perf_counter()
					astar(lambda: draw(win, grid, ROWS, width), grid, npcPosition, end)
					endTime = time.perf_counter()
					print("Elapsed A* time:", (endTime-startTime))
					print("\n ---------------")


				elif event.key == pygame.K_t: # Find and cut down trees test
					gather_resource("Tree", interest_spots_dict, oblivionNPCs, grid)

				elif event.key == pygame.K_i: # Find and mine iron
					gather_resource("Iron", interest_spots_dict, oblivionNPCs, grid)

				elif event.key == pygame.K_k: # Build charcoal kiln
					build_building("kiln", resource_storage_dict, interest_spots_dict, discovered_Spots, grid, oblivionNPCs)
				
				elif event.key == pygame.K_f: # Build building test
					build_building("training camp", resource_storage_dict, interest_spots_dict, discovered_Spots, grid, oblivionNPCs)

				elif event.key == pygame.K_l: # Produce charcoal
					craft_item("Charcoal", resource_storage_dict, interest_spots_dict, grid, oblivionNPCs)
					
					


				elif event.key == pygame.K_b and start and end: # Explore Wide
					for npc in oblivionNPCs:
						for row in grid:
							for spot in row:
								spot.update_neighbors(grid)

						npcSpot = grid[npc.row][npc.col]
						discovered_resource_spots_dict, discovered_Spots = explore_wide(lambda: draw(win, grid, ROWS, width), npcSpot, oblivionNPCs, grid, discovered_Spots)
						for key in discovered_resource_spots_dict.keys():
							for val in discovered_resource_spots_dict[key]:
								interest_spots_dict[key].append(val)
				
				elif event.key == pygame.K_g: # multi character testing
					for shit in range(100):
						for npc in oblivionNPCs:
							npc.update(grid, interest_spots_dict, resource_storage_dict)
							draw(win, grid, ROWS, width, oblivionNPCs)
							if npc.job == "Explorer":
								update_dicts(interest_spots_dict, npc, discovered_Spots)
				
				elif event.key == pygame.K_u: # singlestepping update
					for npc in oblivionNPCs:
						npc.update(grid, interest_spots_dict, resource_storage_dict)
						draw(win, grid, ROWS, width, oblivionNPCs)
						if npc.job == "Explorer":
							update_dicts(interest_spots_dict, npc, discovered_Spots)
					update +=1
					#print("Update:", update)



				elif event.key == pygame.K_s: # Go to school
					go_to_school(oblivionNPCs[0], interest_spots_dict["School"], grid, "Explorer")

				elif event.key == pygame.K_a:
					go_to_school(oblivionNPCs[1], interest_spots_dict["School"], grid, "Builder")


				elif event.key == pygame.K_d and start and end: # Explore Deep
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = explore_deep(lambda: draw(win, grid, ROWS, width), npcPosition, oblivionNPCs[0], discovered_Spots, grid)
				
				elif event.key == pygame.K_g and start and end: # Custom Greedy
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = custom_greedy(lambda: draw(win, grid, ROWS, width), grid, npcPosition, end)
					
					for spot in pathList[::-1]:
						oblivionNPCs[0].go_to_Spot_instantly(grid, spot)
						draw(win, grid, ROWS, width, oblivionNPCs)
					end = None
				

				elif event.key == pygame.K_h and start and end: # Custom bullshit
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					
					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = astar(lambda: draw(win, grid, ROWS, width), grid, npcPosition, end)

					for spot in pathList[::-1]:
						oblivionNPCs[0].go_to_Spot_instantly(grid, spot)
						draw(win, grid, ROWS, width, oblivionNPCs)
					end = None
					reset_map(grid)

				elif event.key == pygame.K_c: # clear
					""" start = None
					end = None
					grid = make_grid(ROWS, width) """
					end = None
					reset_map(grid)

			


	pygame.quit()

if __name__ == "__main__":
	main(WIN, WIDTH)

