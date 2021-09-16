#from typing import Counter
import pygame
import math
import os
import queue
import time

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Dumb AI tries to find the right way")

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

class NPC:
	def __init__(self, row, col, width, name):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.width = width
		self.color = BLUE
		self.name = name


	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def move_to_pos(self, grid, spot):
		if(grid[self.row][self.col].type == "Floor"):
			grid[self.row][self.col].color = WHITE

		self.row = spot.row
		self.col = spot.col
		time.sleep(0.07)

		grid[self.row][self.col].color = BLUE
		pass
		


class Spot:
	def __init__(self, row, col, width, total_rows, type):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
		self.type = type

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

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
	""" x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2) """

	x1, y1 = p1
	x2, y2 = p2
	dx = abs(x1 - x2)
	dy = abs(y1 - y2)
	d = 1 # distance between spots
	d2 = math.sqrt(2) # diagonal distance between spots

	h = d * (dx + dy) + (d2 - 2 * d) * min(dx, dy)
	return h



def reconstruct_path(came_from, current, draw):
	counter = 0
	
	list_to_path = []
	while current in came_from:
		list_to_path.append(current)
		current = came_from[current]
		if current.color == BLUE: # stop at start
			return list_to_path
		current.make_path()
		counter += 1
		draw()
	return list_to_path


def astar(draw, grid, start, end): 
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
						neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

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

	#depth first traversal
def explore_deep(draw, start, npcList, visitedSpots):
	open_stack = queue.LifoQueue()
	open_stack.put(start)
	previous_spots = {start}
	came_from = {}
	while not open_stack.empty():

		current = open_stack.get()
		npcList[0].move_to_pos()

				
		for neighbor in current.neighbors[::-1]:
			if neighbor not in previous_spots:
				open_stack.put(neighbor)
				came_from[neighbor] = current
				previous_spots.add(neighbor)
		
		draw()

		if current != start:
			current.make_closed()
		
	
	return False # no path found

# creates a bunch of spots to append them to the grid list and returns the list after it's done
def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows , "Floor")
			grid[i].append(spot)

	return grid


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
	elif mapnum == 2:
		f = open("Map2.txt", "r")
	elif mapnum == 3:
		f = open("Map3.txt", "r")
	
	if mapnum == 1 or mapnum == 2:	
		startX = 12
		startY = 12
	
	else:
		startX = 7
		startY = 7

	start = None
	end = None
	
	# reads the file and makes a character a specific object
	for line in f:
		for char in line:
			if char == "X":
				grid[startY][startX].make_barrier()
				grid[startY][startX].type = "Wall"

			if char == "S":
				grid[startY][startX].make_start()
				start = grid[startY][startX]

			if char == "G":
				grid[startY][startX].make_end()
				end = grid[startY][startX]
			
			startY += 1
		if mapnum == 1 or mapnum == 2:
			startY = 12
		else:
			startY = 7
		startX +=1
	f.close()
	return start, end



		


def main(win, width):
	ROWS = 40
	grid = make_grid(ROWS, width)
	start = None
	end = None
	start, end = load_map(grid, 3)
	oblivionNPCs = [NPC(23,23,width, "Imperial Guard")]
	visitedSpots = []

	run = True
	while run:
		draw(win, grid, ROWS, width, oblivionNPCs)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			
			if pygame.mouse.get_pressed()[0]: # left click
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
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
					end = None



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

					startTime = time.perf_counter()
					astar(lambda: draw(win, grid, ROWS, width), grid, start, end)
					endTime = time.perf_counter()
					print("Elapsed A* time:", (endTime-startTime))
					print("\n ---------------")

				elif event.key == pygame.K_b and start and end: # Breadth first
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					
					for spot in pathList[::-1]:
						oblivionNPCs[0].move_to_pos(grid, spot)
						draw(win, grid, ROWS, width, oblivionNPCs)
					end = None

				elif event.key == pygame.K_d and start and end: # Explore Deep
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = explore_deep(lambda: draw(win, grid, ROWS, width), oblivionNPCs[0], visitedSpots)

					
				
				elif event.key == pygame.K_g and start and end: # Custom Greedy
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = custom_greedy(lambda: draw(win, grid, ROWS, width), grid, npcPosition, end)
					
					for spot in pathList[::-1]:
						oblivionNPCs[0].move_to_pos(grid, spot)
						draw(win, grid, ROWS, width, oblivionNPCs)
					end = None
				

				elif event.key == pygame.K_h and start and end: # Custom bullshit
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					
					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = astar(lambda: draw(win, grid, ROWS, width), grid, npcPosition, end)

					for spot in pathList[::-1]:
						oblivionNPCs[0].move_to_pos(grid, spot)
						draw(win, grid, ROWS, width, oblivionNPCs)
					end = None

				elif event.key == pygame.K_c: # clear
					start = None
					end = None
					grid = make_grid(ROWS, width)


	pygame.quit()

if __name__ == "__main__":
	main(WIN, WIDTH)

