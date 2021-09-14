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
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

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
	while current in came_from:
		current = came_from[current]
		if current.color == ORANGE: # stop at start
			return counter
		current.make_path()
		counter += 1
		draw()


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
			path_steps_count = reconstruct_path(came_from, end, draw)
			print("\n")
			print("A* path took", path_steps_count, "steps")
			return True

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
			path_steps_count = reconstruct_path(came_from, end, draw)
			print("\n")
			print("Custom greedy path took", path_steps_count, "steps")
			return True

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



def bfs(draw, start, end):
	open_queue = queue.Queue()
	open_queue.put(start)
	previous_spots = {start}
	came_from = {}
	while not open_queue.empty():

		current = open_queue.get()

		if current == end:
			path_steps_count = reconstruct_path(came_from, end, draw)
			end.make_end()
			print("\n")
			print("BFS path took", path_steps_count, "steps")
			return True
		
		for neighbor in current.neighbors:
			if neighbor not in previous_spots:
				open_queue.put(neighbor)
				came_from[neighbor] = current
				if(neighbor != end):
					neighbor.make_open()
				previous_spots.add(neighbor)
		
		draw()

		if current != start:
			current.make_closed()
	
	return False # no path found





def dfs(draw, start, end):
	open_stack = queue.LifoQueue()
	open_stack.put(start)
	previous_spots = {start}
	came_from = {}
	while not open_stack.empty():

		current = open_stack.get()

		if current == end:
			path_steps_count = reconstruct_path(came_from, end, draw)
			end.make_end()
			print("\n")
			print("DFS path took", path_steps_count, "steps")
			return True
				
		for neighbor in current.neighbors[::-1]:
			if neighbor not in previous_spots:
				open_stack.put(neighbor)
				came_from[neighbor] = current
				if(neighbor != end):
					neighbor.make_open()
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
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
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




	run = True
	while run:
		draw(win, grid, ROWS, width)
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

					startTime = time.perf_counter()
					bfs(lambda: draw(win, grid, ROWS, width), start, end)
					endTime = time.perf_counter()
					print("Elapsed BFS time:", (endTime-startTime))
					print("\n ---------------")

				elif event.key == pygame.K_d and start and end: # Depth first
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					startTime = time.perf_counter()
					dfs(lambda: draw(win, grid, ROWS, width), start, end)
					endTime = time.perf_counter()
					print("Elapsed DFS time map 1:", (endTime-startTime))
					print("\n ---------------")
				
				elif event.key == pygame.K_g and start and end: # Custom Greedy
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					startTime = time.perf_counter()
					custom_greedy(lambda: draw(win, grid, ROWS, width), grid, start, end)
					endTime = time.perf_counter()
					print("Elapsed Custom Greedy time:", (endTime-startTime))
					print("\n ---------------")

				elif event.key == pygame.K_c: # clear
					start = None
					end = None
					grid = make_grid(ROWS, width)


	pygame.quit()

if __name__ == "__main__":
	main(WIN, WIDTH)

