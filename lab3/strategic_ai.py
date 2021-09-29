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
		self.next_Spot = Spot
		self.previous_state = ""
		self.current_state = ""
		self.resource_pos_dict = {}
		self.resource_pos_dict.setdefault("Tree", [])
		self.resource_pos_dict.setdefault("Iron", [])
		self.discovered_Spots = []
		self.schooling_left = 20


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
	
	def update(self, grid):

		if self.current_state == "Exploring":
			explore_wide(self, grid, self.discovered_Spots)
			if(manhattan_distance(self.get_pos(), self.next_Spot.get_pos()) < 2):
				self.go_to_Spot_instantly(grid, self.next_Spot)

			else:
				path_list = astar(grid, grid[self.row][self.col], self.next_Spot)
				for spot in path_list[::-1]:
					self.path_queue.put(spot)
				self.next_Spot = self.path_queue.get()
				self.go_to_Spot_instantly(grid, self.next_Spot)
				self.current_state = "Moving along path"
				return
		
		if self.current_state == "Moving along path":
			if not self.path_queue.empty():
				self.next_Spot = self.path_queue.get()
				self.discovered_Spots = explore_spots(grid, self, self.resource_pos_dict)
				self.go_to_Spot_instantly(grid, self.next_Spot)
			else:
				if self.previous_state == "Going to school":
					self.change_state("Going to school")

				else:
					self.current_state = "Exploring"

		if self.current_state == "Going to school":
			if self.schooling_left <= 1:
				self.current_state = ""
				print(self.name, "became a", self.job)

				# when character becomes a explorer put the current position in the open queue so breadth first search
				# has something to work with
				if self.job == "Explorer": 
					self.open_queue.put(grid[self.row][self.col])
					self.change_state("Exploring")

			else:
				self.schooling_left -= 1
				print(self.name, "has", self.schooling_left, "study time left")

		elif self.current_state == "":
			#print("not much going on here")
			pass


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




def astar(grid, start = Spot, end = Spot): 
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
def explore_wide(npc, grid, discovered_Spots):
	""" resource_pos_dict = {}
	resource_pos_dict.setdefault("Tree", [])
	resource_pos_dict.setdefault("Iron", []) """
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_b:
				pass
					#return resource_pos_dict, discovered_Spots
	if not npc.open_queue.empty():
		current = npc.open_queue.get()
		npc.next_Spot = current

		
		#else:
		""" npcSpot = grid[npc.row][npc.col]
		pathList = astar(lambda:draw, grid, npcSpot, current)
		npc.path_list = pathList

		for spot in pathList[::-1]:
			npc.path_list = queue.Queue()
			npc.path_list.put(spot)
		
		if npc.path_list:
			next_Spot = npc.path_list.get()
			npc.go_to_Spot_instantly(grid, next_Spot)
			if next_Spot not in discovered_Spots:
				discovered_Spots.append()
				discovered_Spots.append(explore_spots(grid, npc)) """
		
		""" npc.go_to_Spot_instantly(grid, spot)
		if spot not in discovered_Spots:
			discovered_Spots.append(explore_spots(grid, npc))
		draw() """

		discovered_surrounding_Spots = explore_spots(grid, npc, npc.resource_pos_dict)
		for spot in discovered_surrounding_Spots:
			if spot not in discovered_Spots:
				discovered_Spots.append(spot)

		if current not in discovered_Spots:
			discovered_Spots.append(current)

		""" if current.is_resource()[0]:
			resource_type = current.is_resource()[1]
			if current not in resource_pos_dict[resource_type]:
				resource_pos_dict[resource_type].append(current) """



		for neighbor in current.neighbors:
			npc.open_queue.put(neighbor)
			npc.discovered_Spots.append(neighbor)
		
		
	else:
		print("Every Spot is explored")
		#draw()
	#print(resource_pos_dict)
	#return resource_pos_dict


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
			pass

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

	already_discovered_Spots = []

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
				already_discovered_Spots.append(grid[startY][startX])
			
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

		grid[19][20].type = "Tree"
		grid[19][20].color = DARK_GREEN
		grid[19][20].trees_left = 5

		grid[20][20].type = "Iron"
		grid[20][20].color = IRON_GREY


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
	""" for spot in path_list[::-1]:
		npc.go_to_Spot_instantly(grid, spot)
		draw()
	print("I'm becoming a", education_type)
	time.sleep(3)
	npc.change_job(education_type)
	print("I became a", npc.job) """




def gather_resource(resource_type, interest_spots_dict, npc, grid, resource_storage_dict, draw):
	closest_resource_Spot = interest_spots_dict[resource_type][0]
	for spot in interest_spots_dict[resource_type]:
			if(h(npc.get_pos(), spot.get_pos()) < h(npc.get_pos(), closest_resource_Spot.get_pos())):
				closest_resource_Spot = spot

	npcPosition = grid[npc.row][npc.col]
	path_list = astar(lambda: draw, grid, npcPosition, closest_resource_Spot)
	for spot in path_list[::-1]:
		npc.go_to_Spot_instantly(grid, spot)
		draw()

	if(resource_type == "Tree"):
		print("cutting down tree")
	if(resource_type == "Iron"):
		print("mining iron")
	time.sleep(3)
	
	if(resource_type == "Tree"):
		closest_resource_Spot.trees_left -= 1
		if(closest_resource_Spot.trees_left <= 0):
			grid[closest_resource_Spot.row][closest_resource_Spot.col].type = "Ground"
			grid[closest_resource_Spot.row][closest_resource_Spot.col].color = BROWN
			for spot in interest_spots_dict["Tree"]:
				if closest_resource_Spot == spot:
					interest_spots_dict["Tree"].remove(spot)
					print("removed tree")
	elif(resource_type == "Iron"):
		grid[closest_resource_Spot.row][closest_resource_Spot.col].type = "Ground"
		grid[closest_resource_Spot.row][closest_resource_Spot.col].color = BROWN
		for spot in interest_spots_dict["Iron"]:
			if closest_resource_Spot == spot:
				interest_spots_dict["Iron"].remove(spot)
				print("removed iron vein")


	print("done")

	print("moving this shit to storage")
	npcPosition = grid[npc.row][npc.col]
	storage_location = interest_spots_dict["Storage"]
	path_list = astar(lambda: draw, grid, npcPosition, storage_location)
	for spot in path_list[::-1]:
		npc.go_to_Spot_instantly(grid, spot)
		draw()
	if(resource_type == "Tree"):
		resource_storage_dict["Wood"] += 1

	elif(resource_type == "Iron"):
		resource_storage_dict["Iron"] += 1




def build_building(building_type, resource_storage_dict, interest_Spots_dict, discovered_Spots, grid, npc, draw):
	if(building_type == "Kiln"): # Kiln
		if resource_storage_dict["Wood"] >= 2:
			print("starting to build kiln")
			build_Spot = None
			for spot in discovered_Spots:
				if(h(spot.get_pos(), interest_Spots_dict["Storage"].get_pos()) < 30 and grid[spot.row][spot.col].type == "Ground"):
					build_Spot = spot
					break
			
			interest_Spots_dict["Kiln"].append(build_Spot)
			find_walk_path(grid, draw, npc, build_Spot)
			grid[build_Spot.row][build_Spot.col].type = "Building"
			resource_storage_dict["Wood"] -= 2
			time.sleep(2)
			print("Kiln as been built at Row:", build_Spot.row, "Col: ", build_Spot.col)
		else:
			print("not enough wood to build kiln")



	elif(building_type == "Smithy"): # Smithy
		if resource_storage_dict["Wood"] >= 2 and resource_storage_dict["Iron bars"] >= 1:
			print("starting to build smithy")
			build_Spot = None
			for spot in discovered_Spots:
				if(h(spot.get_pos(), interest_Spots_dict["Storage"].get_pos()) < 30 and grid[spot.row][spot.col].type == "Ground"):
					build_Spot = spot
					break
			
			interest_Spots_dict["Smithy"].append(build_Spot)
			find_walk_path(grid, draw, npc, build_Spot)
			grid[build_Spot.row][build_Spot.col].type = "Building"
			resource_storage_dict["Wood"] -= 2
			time.sleep(2)
			print("Smithy as been built at Row:", build_Spot.row, "Col: ", build_Spot.col)
		else:
			print("not enough wood to build smithy")



	elif(building_type == "Forge"): # Forge
		if resource_storage_dict["Wood"] >= 2:
			print("starting to build forge")
			build_Spot = None
			for spot in discovered_Spots:
				if(h(spot.get_pos(), interest_Spots_dict["Storage"].get_pos()) < 30 and grid[spot.row][spot.col].type == "Ground"):
					build_Spot = spot
					break
			
			interest_Spots_dict["Forge"].append(build_Spot)
			find_walk_path(grid, draw, npc, build_Spot)
			grid[build_Spot.row][build_Spot.col].type = "Building"
			resource_storage_dict["Wood"] -= 2
			time.sleep(2)
			print("Forge as been built at Row:", build_Spot.row, "Col: ", build_Spot.col)
		else:
			print("not enough wood to build forge")

	elif(building_type == "Training Camp"): # Training Camp
		if resource_storage_dict["Wood"] >= 2:
			print("starting to build training camp")
			build_Spot = None
			for spot in discovered_Spots:
				if(h(spot.get_pos(), interest_Spots_dict["Storage"].get_pos()) < 30 and grid[spot.row][spot.col].type == "Ground"):
					build_Spot = spot
					break
			
			interest_Spots_dict["Training Camp"].append(build_Spot)
			find_walk_path(grid, draw, npc, build_Spot)
			grid[build_Spot.row][build_Spot.col].type = "Building"
			resource_storage_dict["Wood"] -= 2
			time.sleep(2)
			print("Training Camp as been built at Row:", build_Spot.row, "Col: ", build_Spot.col)
		else:
			print("not enough wood to build training camp")


def explore_spots(grid, npc, resource_pos_dict):
	discovered_Spots = []
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

	discovered_Spots.append(grid[npc.row + 1][npc.col])
	discovered_Spots.append(grid[npc.row - 1][npc.col])
	discovered_Spots.append(grid[npc.row][npc.col + 1])
	discovered_Spots.append(grid[npc.row][npc.col - 1])

	discovered_Spots.append(grid[npc.row + 1][npc.col + 1])
	discovered_Spots.append(grid[npc.row - 1][npc.col + 1])
	discovered_Spots.append(grid[npc.row - 1][npc.col - 1])
	discovered_Spots.append(grid[npc.row + 1][npc.col - 1])

	reset_Spot(grid[npc.row + 1][npc.col]) # check right
	reset_Spot(grid[npc.row - 1][npc.col]) # check left
	reset_Spot(grid[npc.row][npc.col + 1]) # check down
	reset_Spot(grid[npc.row][npc.col - 1]) # check up

	reset_Spot(grid[npc.row + 1][npc.col + 1]) # check down right
	reset_Spot(grid[npc.row - 1][npc.col + 1]) # check down left
	reset_Spot(grid[npc.row - 1][npc.col - 1]) # check up left
	reset_Spot(grid[npc.row + 1][npc.col - 1]) # check up right
	return discovered_Spots



def find_walk_path(grid, draw, npc, end_Spot):
	npcPosition = grid[npc.row][npc.col]
	path_list = astar(lambda: draw, grid, npcPosition, end_Spot)
	for spot in path_list[::-1]:
		npc.go_to_Spot_instantly(grid, spot)
		draw()


def update_dicts(main_interest_Spots_dict, npcList):
	for npc in npcList:
		for key in npc.resource_pos_dict.keys():
			if len(npc.resource_pos_dict[key]) > len(main_interest_Spots_dict[key]): # efficiency
				for val in npc.resource_pos_dict[key]:
					if val not in main_interest_Spots_dict[key]:
						main_interest_Spots_dict[key].append(val)
	pass


def main(win, width):
	ROWS = 100
	grid = []
	make_grid(ROWS, width, grid)
	start = Spot
	end = Spot
	discovered_Spots = []
	start, end, discovered_Spots = load_map(grid, 4)
	oblivionNPCs = [NPC(24,24,width, "Imperial Guard")]
	oblivionNPCs.append(NPC(22,22,width, "Just Guard"))
	#resource_pos_list = []
	resource_storage_dict = {
		"Wood": 0,
		"Iron": 0,
		"Charcoals": 0,
		"Iron bars": 0,
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
	interest_spots_dict.setdefault("Training Camp", [])

	for row in grid:
		for spot in row:
			spot.update_neighbors(grid)

	
	run = True
	while run:
		draw(win, grid, ROWS, width, oblivionNPCs)

		""" for npc in oblivionNPCs:
			npc.update(grid)
			draw(win, grid, ROWS, width, oblivionNPCs) """
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			
			""" if pygame.mouse.get_pressed()[0]: # left click
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				print("Row:", row, "Col:", col)
				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()

				elif not end and spot != start:
					end = spot
					end.make_end()

				elif spot != end and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]: # right click
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None """



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


				elif event.key == pygame.K_t and start and end: # Find and cut down trees test
					gather_resource("Tree", interest_spots_dict, oblivionNPCs[0], grid, resource_storage_dict, lambda: draw(win, grid, ROWS, width))

				elif event.key == pygame.K_i and start and end: # Find and mine iron
					gather_resource("Iron", interest_spots_dict, oblivionNPCs[0], grid, resource_storage_dict, lambda: draw(win, grid, ROWS, width))

				elif event.key == pygame.K_k and start and end: # Build charcoal kiln
					build_building("Kiln", resource_storage_dict, interest_spots_dict, discovered_Spots, grid, oblivionNPCs[0], lambda: draw(win, grid, ROWS, width))

				elif event.key == pygame.K_l and start and end: # Produce charcoal
					if not interest_spots_dict["Kiln"]:
						print("No charcoal kiln has been built")
					elif resource_storage_dict["Wood"] < 1:
						print("There's not enough wood to make charcoal")

					else:
						print("going to charcoal kiln")
						closest_kiln = interest_spots_dict["Kiln"][0]
						for spot in interest_spots_dict["Kiln"]:
								if(h(oblivionNPCs[0].get_pos(), spot.get_pos()) < h(oblivionNPCs[0].get_pos(), closest_kiln.get_pos())):
									closest_kiln = spot
						find_walk_path(grid, lambda: draw(win, grid, ROWS, width), oblivionNPCs[0], closest_kiln)
						print("Putting wood in the kiln")
						time.sleep(3)
						print("The charcoal is now done roasting")
						resource_storage_dict["Wood"] -= 1
						resource_storage_dict["Charcoals"] += 1
					
					


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
							npc.update(grid)
							draw(win, grid, ROWS, width, oblivionNPCs)
							if npc.job == "Explorer":
								update_dicts(interest_spots_dict, oblivionNPCs)
				
				elif event.key == pygame.K_u: # singlestepping update
					for npc in oblivionNPCs:
						npc.update(grid)
						draw(win, grid, ROWS, width, oblivionNPCs)
						if npc.job == "Explorer":
							update_dicts(interest_spots_dict, oblivionNPCs)



				elif event.key == pygame.K_s: # Go to school
					go_to_school(oblivionNPCs[0], interest_spots_dict["School"], grid, "Explorer")


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

