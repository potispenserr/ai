import pygame
import queue
import time
import random
import json

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
		self.tree_list = []
		self.tree_width = None
		self.materials_here = None

	def get_pos(self):
		return self.row, self.col
	
	def get_grid_Spot_here(self, grid):
		return grid[self.row][self.col]

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

	def add_trees(self, trees, tree_width):
		self.trees_left = trees
		self.tree_width = tree_width
		for _ in range(trees):
			random_x = random.randint(self.x, self.x + self.width)
			random_y = random.randint(self.y, self.y + self.width)
			self.tree_list.append((random_x, random_y))


		#pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

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
		if self.type == "Tree" and not self.color == GREY:
			for tree in self.tree_list:
				pygame.draw.rect(win, DARK_GREEN, (tree[0], tree[1], self.tree_width, self.tree_width))

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
		self.open_stack = queue.LifoQueue()
		self.task_queue = queue.Queue()
		self.next_Spot = Spot
		self.previous_state = ""
		self.current_state = ""
		self.resource_pos_dict = {}
		self.resource_pos_dict.setdefault("Tree", [])
		self.resource_pos_dict.setdefault("Iron", [])
		self.discovered_Spots = {}
		self.previous_Spots = []
		self.schooling_left = 5
		self.resource_gathering_timer = 30
		self.crafting_timer = 0
		self.inventory = ""
		self.build_timer = 0
		self.swamp_timer = 0
		self.reverse_deep = 0
		self.crating_building_Spot = None


	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def go_to_Spot_instantly(self, grid, spot):
		reset_Spot(grid[self.row][self.col])

		self.row = spot.row
		self.col = spot.col
		#time.sleep(0.1)
		
	

		grid[self.row][self.col].color = self.color

	def move_to_Spot(self, grid, spot):
		pass
		
	def get_grid_Spot_here(self, grid):
		return grid[self.row][self.col]

	def get_pos(self):
		return self.row, self.col
	
	def change_job(self, new_job):
		self.job = new_job

	def change_state(self, new_state):
		self.previous_state = self.current_state
		self.current_state = new_state
	
	def update(self, grid, interest_Spots_dict, storage_dict, master_task_list: list, design_doc_dict):
		if self.current_state == "Exploring": # Exploring
			if self.swamp_timer > 0:
				#print("Ugh i'm stuck in the swamp")
				self.swamp_timer -= 1
				return
			if(self.job == "Explorer"):
				explore_wide(self, grid)

			elif(self.job == "Deep_Explorer"):
				explore_deep(self, grid, self.reverse_deep)

			if(h(self.get_pos(), self.next_Spot.get_pos()) < 1):
				#print("Distance to next spot is", h(self.get_pos(), self.next_Spot.get_pos()))
				self.go_to_Spot_instantly(grid, self.next_Spot)
				self.previous_Spots.append(self.next_Spot)
				if grid[self.row][self.col].type == "Swamp":
					self.swamp_timer = 2

			else:
				self.pathfind_to(grid, self.next_Spot)

				self.next_Spot = self.path_queue.get()
				self.go_to_Spot_instantly(grid, self.next_Spot)
				self.previous_Spots.append(self.next_Spot)
				self.previous_state = "Exploring"
				self.current_state = "Moving along path"
				if grid[self.row][self.col].type == "Swamp":
					self.swamp_timer = 2
				return

		
		elif self.current_state == "Moving along path": #Move along path
			if self.swamp_timer > 0:
				#print("still stuck in the swamp")
				self.swamp_timer -= 1
				return
			
			if grid[self.row][self.col].type == "Swamp":
				self.swamp_timer = 2
				#print("ugh i'm stuck in the swamp")
			
			if not self.path_queue.empty():
				self.next_Spot = self.path_queue.get()
				if self.job == "Explorer" or self.job == "Deep_Explorer":
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
				if len(master_task_list) > 0:
					if master_task_list[0][1] == self:
						print("i'm done with this shit")
						master_task_list.pop(0)
				
				if self.job == "Builder":
					self.color = ORANGE
				
				if self.job == "Kiln operator":
					self.color = WHITE

				# when character becomes a explorer put the current position in the open queue so breadth first search
				# has something to work with
				if self.job == "Explorer": 
					self.open_queue.put(grid[self.row][self.col])
					self.discovered_Spots.setdefault(grid[self.row][self.col], 1)
					self.change_state("Exploring")
					self.previous_Spots.append(grid[self.row][self.col])
					self.color = BLUE
				
				if self.job == "Deep_Explorer":
					min_pos_range = 20
					max_pos_range = 70
					random_row = random.randint(self.row - min_pos_range, self.row + max_pos_range)
					random_col = random.randint(self.col - min_pos_range, self.col + max_pos_range)
					random_starter_spot = grid[random_row][random_col]
					self.reverse_deep = random.randint(1,2)
					self.open_stack.put(random_starter_spot)
					self.color = RED

					if(h(self.get_pos(), self.next_Spot.get_pos()) < 2):
						#print("Distance to next spot is", h(self.get_pos(), self.next_Spot.get_pos()))
						self.go_to_Spot_instantly(grid, self.next_Spot)
						self.previous_Spots.append(self.next_Spot)
						if grid[self.row][self.col].type == "Swamp":
							self.swamp_timer = 2
						self.change_state("Exploring")

					else:
						self.pathfind_to(grid, random_starter_spot)
						self.previous_state = "Exploring"
						self.current_state = "Moving along path"

					self.discovered_Spots.setdefault(grid[self.row][self.col], 1)
					self.previous_Spots.append(grid[self.row][self.col])


			else:
				self.schooling_left -= 1


		
		elif self.current_state == "Cutting down a tree": # Tree cutting
			if self.resource_gathering_timer > 0:
				self.resource_gathering_timer -= 1
				if grid[self.row][self.col].trees_left <= 0:
					print(self.name, ": Oh, there's not any trees left. what a waste going here then")
					for tree in interest_Spots_dict["Tree"]:
						if tree.get_grid_Spot_here(grid) == self.get_grid_Spot_here(grid):
							interest_Spots_dict["Tree"].remove(tree)
							print("removed tree at Row:", tree.row, "Col:", tree.col)
					self.change_state("")
					self.resource_gathering_timer = design_doc_dict["gathering_timers"]["Tree"]
					return
			else:
				tree_Spot = grid[self.row][self.col]
				if grid[self.row][self.col].trees_left <= 0:
					print(self.name, ": Oh, there's not any trees left. what a waste going here then")
					self.change_state("")
					self.resource_gathering_timer = design_doc_dict["gathering_timers"]["Tree"]
					for tree in interest_Spots_dict["Tree"]:
						if tree.get_grid_Spot_here(grid) == self.get_grid_Spot_here(grid):
							interest_Spots_dict["Tree"].remove(tree)
							print("removed tree at Row:", tree.row, "Col:", tree.col)
					return
				tree_Spot.trees_left -= 1
				tree_Spot.tree_list.pop()

				if(tree_Spot.trees_left == 0):
					self.inventory = "Wood"
					self.resource_gathering_timer = design_doc_dict["gathering_timers"]["Tree"]

					#tree_Spot.tree_list.pop()
					#grid[tree_Spot.row][tree_Spot.col].type = "Ground"
					for spot in interest_Spots_dict["Tree"]:
						if tree_Spot == spot:
							interest_Spots_dict["Tree"].remove(spot)
							print("removed tree")
							print("Spot is now:", tree_Spot.type, "with", tree_Spot.trees_left, "trees left")

					self.pathfind_to(grid, interest_Spots_dict["Storage"])

					self.previous_state = "Taking resource to storage"
					self.current_state = "Moving along path"

				elif(tree_Spot.trees_left > 0):
					self.inventory = "Wood"
					self.resource_gathering_timer = design_doc_dict["gathering_timers"]["Tree"]

					self.pathfind_to(grid, interest_Spots_dict["Storage"])

					self.previous_state = "Taking resource to storage"
					self.current_state = "Moving along path"

				elif(tree_Spot.trees_left < 0):
					print(self.name, ":There is no tree left, oh well")
					self.change_state("")



		


		elif self.current_state == "Producing charcoal": # Produce charcoal
			if grid[self.row][self.col].materials_here["Wood"] == 0:
				grid[self.row][self.col].materials_here = {
					"Wood": 1
				}
				print("Laying down wood to get some more for the kiln")
				self.inventory = ""
				self.pathfind_to(grid, interest_Spots_dict["Storage"])
				
				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put(["Producing charcoal", grid[self.row][self.col]])
				self.resource_gathering_timer = design_doc_dict["crafting_timers"]["Charcoal"]

			
			elif grid[self.row][self.col].materials_here["Wood"] >= design_doc_dict["item_recipies"]["Charcoal"]["Wood"]:
				if self.crafting_timer <= 0:
					print("The charcoal is now done")
					self.inventory = "Charcoal"
					for key in grid[self.row][self.col].materials_here:
						grid[self.row][self.col].materials_here[key] = 0

					self.pathfind_to(grid, interest_Spots_dict["Storage"])
					if master_task_list[0] == "Producing charcoal":
						master_task_list.pop(0)

					self.previous_state = "Taking resource to storage"
					self.current_state = "Moving along path"

				else:
					self.crafting_timer -= 1

			
			else:
				grid[self.row][self.col].materials_here["Wood"] += 1
				self.inventory = ""
				if grid[self.row][self.col].materials_here["Wood"] >= design_doc_dict["item_recipies"]["Charcoal"]["Wood"]:
					return

				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.pathfind_to(grid, interest_Spots_dict["Storage"])

				self.task_queue.put(["Producing charcoal", grid[self.row][self.col]])
				print("might need to get more wood for the kiln")
		
		elif self.current_state == "Producing iron bar":
			self.produce_tier_2_items(grid, interest_Spots_dict, self.current_state, "Iron bar", design_doc_dict)
		
		elif self.current_state == "Producing sword":
			self.produce_tier_2_items(grid, interest_Spots_dict, self.current_state, "Sword", design_doc_dict)

		
		elif self.current_state == "Building kiln": # Kiln building
			self.build_tier_1_building(grid, interest_Spots_dict, self.current_state, "Kiln", master_task_list, design_doc_dict)

		elif self.current_state == "Building forge": # Build forge
			self.build_tier_1_building(grid, interest_Spots_dict, self.current_state, "Forge", master_task_list, design_doc_dict)
		
		elif self.current_state == "Building training camp": # Build training camp
			self.build_tier_1_building(grid, interest_Spots_dict, self.current_state, "Training camp", master_task_list, design_doc_dict)
	
		elif self.current_state == "Building smithy": # Build smithy aka the only "tier 2" building
			if not grid[self.row][self.col].materials_here:
				grid[self.row][self.col].materials_here = {
					"Wood": 1,
					"Iron bar": 0
				}
				print("Laying down wood to get some more")
				self.pathfind_to(grid, interest_Spots_dict["Storage"])
				
				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put(["Building smithy", grid[self.row][self.col]])
				self.build_timer = design_doc_dict["building_timers"]["Smithy"]

			
			elif grid[self.row][self.col].materials_here["Wood"] >= design_doc_dict["building_recipies"]["Smithy"]["Wood"]:
				if grid[self.row][self.col].materials_here["Iron bar"] >= design_doc_dict["building_recipies"]["Smithy"]["Iron bar"]:
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
						self.pathfind_to(grid, interest_Spots_dict["Storage"])
						
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
				storage_dict["Wood"] -= 1
				current_task = self.task_queue.get()
				self.previous_state = current_task[0]
				self.pathfind_to(grid, current_task[1])

				self.current_state = "Moving along path"

		elif self.current_state == "Getting iron bar": # Getting iron bar
			if(storage_dict["Iron bar"] <= 0):
				print("No iron bars in storage")
				self.change_state("")
			else:
				self.inventory = "Iron bar"
				storage_dict["Iron bar"] -= 1
				current_task = self.task_queue.get()
				self.previous_state = current_task[0]
				self.pathfind_to(grid, current_task[1])

				self.current_state = "Moving along path"
		
		elif self.current_state == "Mining iron": # Iron mining
			if self.resource_gathering_timer > 0:
				self.resource_gathering_timer -= 1
				print("Iron timer:", self.resource_gathering_timer)
			else:
				iron_Spot = grid[self.row][self.col]
				self.inventory = "Iron"
				self.resource_gathering_timer = design_doc_dict["gathering_timers"]["Tree"]

				grid[iron_Spot.row][iron_Spot.col].type = "Ground"
				grid[iron_Spot.row][iron_Spot.col].color = BROWN
				for spot in interest_Spots_dict["Iron"]:
					if iron_Spot == spot:
						interest_Spots_dict["Iron"].remove(spot)
						print("removed iron")
						print("Spot is now:", iron_Spot.type)
				self.pathfind_to(grid, interest_Spots_dict["Storage"])

				self.previous_state = "Taking resource to storage"
				self.current_state = "Moving along path"
		
		elif self.current_state == "Getting iron": # Getting iron ore
			if(storage_dict["Iron"] <= 0):
				print("No iron ore in storage")
				self.change_state("")
			else:
				self.inventory = "Iron"
				storage_dict["Iron"] -= 1
				current_task = self.task_queue.get()
				self.previous_state = current_task[0]
				self.pathfind_to(grid, current_task[1])

				self.current_state = "Moving along path"
		
		elif self.current_state == "Taking resource to storage": # Taking resource to storage
			storage_dict[self.inventory] += 1
			self.inventory = ""
			self.change_state("")

		else:
			print(self.name, "has a unimplemented state", self.current_state)


	def build_tier_1_building(self, grid, interest_Spots_dict, building_state_string, building_type, master_task_list, design_doc_dict): # Build tier one building
			if not grid[self.row][self.col].materials_here: # When worker first arrives at the build spot
				grid[self.row][self.col].materials_here = {
					"Wood": 1
				}
				print("Laying down wood to get some more")
				self.inventory = ""
				self.pathfind_to(grid, interest_Spots_dict["Storage"])
				
				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put([building_state_string, grid[self.row][self.col]])

				self.build_timer = design_doc_dict["building_timers"][building_type]

			
			elif grid[self.row][self.col].materials_here["Wood"] >= design_doc_dict["building_recipies"][building_type]["Wood"]:
				if self.build_timer <= 0:
					
					interest_Spots_dict[building_type].append(grid[self.row][self.col])
					grid[self.row][self.col].type = "Building"
					print("Finally built", building_type)
					for key in grid[self.row][self.col].materials_here:
						grid[self.row][self.col].materials_here[key] = 0
					self.change_state("")
					if master_task_list[0][0] == "Building " + building_type.lower() and master_task_list[0][1][0]:
						print("removing this task from the task list")
						master_task_list.pop(0)
						print(master_task_list)


				else:
					self.build_timer -= 1

			
			else:
				grid[self.row][self.col].materials_here["Wood"] += 1
				self.inventory = ""
				if grid[self.row][self.col].materials_here["Wood"] >= design_doc_dict["building_recipies"][building_type]["Wood"]:
					return

				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put([building_state_string, grid[self.row][self.col]])
				print("might need to get more wood")



	def produce_tier_2_items(self, grid, interest_Spots_dict, crafting_state_string, item_type, design_doc_dict):
		if grid[self.row][self.col].materials_here["Wood"] == 0:
				if(item_type == "Iron bar"):
					grid[self.row][self.col].materials_here = {
						"Wood": 1,
						"Iron": 0
					}
				else:
					grid[self.row][self.col].materials_here = {
						"Wood": 1,
						"Iron bar": 0
					}

				print("Laying down wood to get some more")
				self.pathfind_to(grid, interest_Spots_dict["Storage"])
				
				self.previous_state = "Getting wood"
				self.current_state = "Moving along path"
				self.task_queue.put([crafting_state_string, grid[self.row][self.col]])
				self.crafting_timer = design_doc_dict["crafting_timers"][item_type]

			
		elif grid[self.row][self.col].materials_here["Wood"] >= design_doc_dict["item_recipies"][item_type]["Wood"]:
			try:
				if grid[self.row][self.col].materials_here["Iron bar"] >= design_doc_dict["item_recipies"][item_type]["Iron bar"]:
					if self.crafting_timer <= 0:
						print("The", item_type, "is now done")
						self.inventory = item_type
						for key in grid[self.row][self.col].materials_here:
							grid[self.row][self.col].materials_here[key] = 0

						self.pathfind_to(grid, interest_Spots_dict["Storage"])
						
						self.previous_state = "Taking resource to storage"
						self.current_state = "Moving along path"
					else:
						print(item_type, "build timer", self.crafting_timer)
						self.crafting_timer -= 1
				else:
					if self.inventory == "Iron bar":
						print("adding an iron bar into the mix")
						grid[self.row][self.col].materials_here["Iron bar"] += 1
						self.inventory = ""

					else:
						self.pathfind_to(grid, interest_Spots_dict["Storage"])
						
						self.previous_state = "Getting iron bar"
						self.current_state = "Moving along path"
						self.task_queue.put([crafting_state_string, grid[self.row][self.col]])

			except:	
				pass
			try:
				# If iron ore is on the Spot instead of iron bars
				if grid[self.row][self.col].materials_here["Iron"] >= design_doc_dict["item_recipies"][item_type]["Iron"]:
					if self.crafting_timer <= 0:
						print("The", item_type, "is now done")
						self.inventory = item_type
						for key in grid[self.row][self.col].materials_here:
							grid[self.row][self.col].materials_here[key] = 0

						self.pathfind_to(grid, interest_Spots_dict["Storage"])

						self.previous_state = "Taking resource to storage"
						self.current_state = "Moving along path"

					else:
						print(item_type, "build timer", self.crafting_timer)
						self.crafting_timer -= 1
				else:
					if self.inventory == "Iron":
						print("adding iron ore into the mix")
						grid[self.row][self.col].materials_here["Iron"] += 1
						self.inventory = ""

					else:
						self.pathfind_to(grid, interest_Spots_dict["Storage"])
						
						self.previous_state = "Getting iron"
						self.current_state = "Moving along path"
						self.task_queue.put([crafting_state_string, grid[self.row][self.col]])
			except:
				pass
		
		else:
			grid[self.row][self.col].materials_here["Wood"] += 1
			self.inventory = ""
			if grid[self.row][self.col].materials_here["Wood"] >= design_doc_dict["item_recipies"][item_type]["Wood"]:
					return

			self.pathfind_to(grid, interest_Spots_dict["Storage"])
			self.previous_state = "Getting wood"
			self.current_state = "Moving along path"
			self.task_queue.put([crafting_state_string, grid[self.row][self.col]])
			print("might need to get more wood")
	
	def pathfind_to(self, grid, destination_Spot):
		path_list = astar(grid, grid[self.row][self.col], destination_Spot, self)
		for spot in path_list[::-1]:
			self.path_queue.put(spot)








def h(p1, p2): # returns diagonal distance
	""" x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2) """

	x1, y1 = p1
	x2, y2 = p2
	dx = abs(x1 - x2)
	dy = abs(y1 - y2)
	d = 1 # distance between spots
	d2 = 1 # diagonal distance between spots

	h = d * (dx + dy) + (d2 - 2 * d) * min(dx, dy)
	return h

def manhattan_distance(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current: Spot, npc: NPC):	
	list_to_path = []
	while current in came_from:
		list_to_path.append(current)
		current = came_from[current]
		if current.get_pos() == npc.get_pos(): # stop at npc
			return list_to_path
		#current.make_path()
		#draw()
	return list_to_path




def astar(grid, start: Spot, end: Spot, npc: NPC): 
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
			list_to_path = reconstruct_path(came_from, end, npc)
			return list_to_path

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if npc.job == "Explorer" or npc.job == "Deep_Explorer":
					open_pq.put((f_score[neighbor], neighbor))
					previous_spots.add(neighbor)

				elif npc.job != "Explorer" or npc.job != "Deep_Explorer":
					if neighbor not in previous_spots and neighbor.color != GREY:
						open_pq.put((f_score[neighbor], neighbor))
						previous_spots.add(neighbor)
						


		if current != start:
			#current.make_closed()
			pass
	print("no path found for", npc.name)
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
def explore_deep(npc, grid, reverse_neighbors):
	if not npc.open_stack.empty():

		current = npc.open_stack.get()
		npc.next_Spot = current

		
		explore_spots(grid, npc, npc.resource_pos_dict)
		
		if not current in npc.discovered_Spots:
			npc.discovered_Spots.setdefault(current, 1)

		if reverse_neighbors == 1:
			for neighbor in current.neighbors:
				if neighbor not in npc.previous_Spots:
					npc.open_stack.put(neighbor)
					npc.previous_Spots.append(neighbor)

				if not neighbor in npc.discovered_Spots:
					npc.discovered_Spots.setdefault(neighbor, 1)
		
		else:
			for neighbor in current.neighbors[::-1]:
				if neighbor not in npc.previous_Spots:
					npc.open_stack.put(neighbor)
					npc.previous_Spots.append(neighbor)

				if not neighbor in npc.discovered_Spots:
					npc.discovered_Spots.setdefault(neighbor, 1)

	else:
		print("Every spot is explored")	

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
				grid[startY][startX].add_trees(5, 2)
			
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
					randomint = random.randint(1, ironprobability + 60)
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

		""" grid[21][22].type = "Tree"
		grid[21][22].color = DARK_GREEN
		grid[21][22].trees_left = 5

		grid[20][22].type = "Iron"
		grid[20][22].color = IRON_GREY """


	f.close()
	return start, end, already_discovered_Spots

def reset_Spot(spot):
	if spot.type == "Tree":
		spot.color = BROWN

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

def go_to_school(npc: NPC, grid, education_type, design_doc_dict, school_Spot = None, interest_Spots_list = None, storage_dict = None):
	if education_type == "Soldier":
		if not interest_Spots_list:
			print("No training camp has been built")
			return
		if storage_dict["Sword"] <= 0:
			print("There is no swords in storage")
			return
		npcSpot = grid[npc.row][npc.col]
		closest_training_camp_Spot = interest_Spots_list[0]
		for spot in interest_Spots_list:
				if(h(npc.get_pos(), spot.get_pos()) < h(npc.get_pos(), closest_training_camp_Spot.get_pos())):
					closest_training_camp_Spot = spot

		path_list = astar(grid, npcSpot, closest_training_camp_Spot, npc)
		for spot in path_list[::-1]:
			npc.path_queue.put(spot)

		npc.previous_state = "Going to school"
		npc.current_state = "Moving along path"
		npc.change_job(education_type)
	else:	
		path_list = astar(grid, grid[npc.row][npc.col], school_Spot, npc)
		for spot in path_list[::-1]:
			npc.path_queue.put(spot)
		
		npc.schooling_left = design_doc_dict["education_timers"][education_type]
		
		""" if(education_type == "Builder"):
			npc.schooling_left = 120
		elif(education_type == "Charcoal kiln operator"):
			npc.schooling_left = 120
		elif(education_type == "Explorer" or education_type == "Deep_Explorer"):
			npc.schooling_left = 60 """

		npc.previous_state = "Going to school"
		npc.current_state = "Moving along path"
		npc.change_job(education_type)


def craft_item(item_type: str, resource_storage_dict: dict, interest_Spots_dict: dict, grid: list, npc_List: list, design_doc_dict):
	crafting_building = None
	first_available_npc = None
	if item_type == "Charcoal":
		if resource_storage_dict["Wood"] < design_doc_dict["item_recipies"]["Charcoal"]["Wood"]:
			print("There's not enough wood to make charcoal")
			return "No wood"

		job_exists = False
		for npc in npc_List:
			if npc.job == "Kiln operator":
				job_exists = True
				if npc.current_state == "":
					first_available_npc = npc
					break

		if not interest_Spots_dict["Kiln"]:
			print("No charcoal kiln has been built")
			return "No kiln"
		
		crafting_building = "Kiln"
		
		if job_exists == False:
			print("No kiln operator has been trained")
			return "No kiln operator"
		if first_available_npc == None:
			print("No kiln operator available")
			return "No available kiln operator"
	
	elif item_type == "Iron bar":
		if not interest_Spots_dict["Forge"]:
			print("No forge has been built")
			return
		elif resource_storage_dict["Charcoal"] < design_doc_dict["item_recipies"]["Iron bar"]["Charcoal"]:
			print("There's not enough charcoal to make iron bars")
			return
		elif resource_storage_dict["Iron"] < design_doc_dict["item_recipies"]["Iron bar"]["Iron"]:
			print("There's not enough iron ore to make iron bars")
			return
		crafting_building = "Forge"
		job_exists = False
		for npc in npc_List:
			if npc.job == "Forge worker":
				job_exists = True
				if npc.current_state == "":
					first_available_npc = npc
		if job_exists == False:
			print("No forge worker has been trained")
			return
		if npc == None:
			print("No forge worker available")
			return
	
	elif item_type == "Sword":
		if not interest_Spots_dict["Smithy"]:
			print("No smithy has been built")
			return
		elif resource_storage_dict["Charcoal"] < design_doc_dict["item_recipies"]["Sword"]["Charcoal"]:
			print("There's not enough charcoal to make sword")
			return
		elif resource_storage_dict["Iron bar"] < design_doc_dict["item_recipies"]["Sword"]["Iron bar"]:
			print("There's not enough iron bars to make sword")
			return
		crafting_building = "Smithy"
		job_exists = False
		for npc in npc_List:
			if npc.job == "Smith":
				job_exists = True
				if npc.current_state == "":
					first_available_npc = npc
		if job_exists == False:
			print("No smith has been trained")
			return
		if npc == None:
			print("No smith available")
			return
	
	if first_available_npc == None:
		print("crafting failed, no available npc")
		return
	print(first_available_npc.name, "going to", crafting_building)
	random_index = random.randint(0, len(interest_Spots_dict[crafting_building]) - 1)
	closest_crafting_building = interest_Spots_dict[crafting_building][random_index]
	""" for spot in interest_Spots_dict[crafting_building]:
			if(h(first_available_npc.get_pos(), spot.get_pos()) < h(first_available_npc.get_pos(), closest_crafting_building.get_pos())):
				closest_crafting_building = spot """


	if(item_type == "Charcoal"):
		first_available_npc.task_queue.put(["Producing charcoal", closest_crafting_building])
	
	elif(item_type == "Iron bar"):
		first_available_npc.task_queue.put(["Producing iron bar", closest_crafting_building])
	
	elif(item_type == "Sword"):
		first_available_npc.task_queue.put(["Producing sword", closest_crafting_building])

	path_list = astar(grid, grid[first_available_npc.row][first_available_npc.col], interest_Spots_dict["Storage"], npc)
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
				break
	if (first_best_npc == None):
		print("No available workers to gather", resource_type)
		return
	if len(interest_spots_dict[resource_type]) <= 0:
		print("there is nowhere to gather", resource_type)
		return

	closest_resource_Spot = interest_spots_dict[resource_type][0]
	closest_path_list = []
	for spot in interest_spots_dict[resource_type]:
			closest_resource_length = h(first_best_npc.get_pos(), closest_resource_Spot.get_pos())
			spot_length = h(first_best_npc.get_pos(), spot.get_pos())
			if closest_resource_length > spot_length:
				closest_resource_Spot = spot

	closest_path_list = astar(grid, first_best_npc.get_grid_Spot_here(grid), closest_resource_Spot.get_grid_Spot_here(grid), first_best_npc)
	for spot in closest_path_list[::-1]:
		first_best_npc.path_queue.put(spot)
	
	print(first_best_npc.name, ": I'm going to cut down a tree at Row:", closest_resource_Spot.row, "Col:", closest_resource_Spot.col)

	if(resource_type == "Tree"):
		first_best_npc.previous_state = "Cutting down a tree"
		first_best_npc.current_state = "Moving along path"

	elif(resource_type == "Iron"):
		first_best_npc.previous_state = "Mining iron"
		first_best_npc.current_state = "Moving along path"



def build_building(building_type, resource_storage_dict, interest_Spots_dict, discovered_Spots, grid, npc_List: list[NPC], design_doc_dict):
	first_available_npc = None
	job_exists = False
	for npc in npc_List:
		if npc.job == "Builder":
			job_exists = True
			if npc.current_state == "":
				first_available_npc = npc
				break
	if job_exists == False:
		print("No builder has been trained")
		return
	elif first_available_npc == None:
		print("no available npcs")
		return

	if resource_storage_dict["Wood"] >= design_doc_dict["building_recipies"]["Kiln"]["Wood"]:
		if building_type == "smithy":
			if resource_storage_dict["Iron bar"] >= design_doc_dict["building_recipies"]["Smithy"]["Iron bar"]:
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

		path_list = astar(grid, grid[first_available_npc.row][first_available_npc.col], interest_Spots_dict["Storage"], npc)
		for spot in path_list[::-1]:
			first_available_npc.path_queue.put(spot)
		
		first_available_npc.previous_state = "Getting wood"
		first_available_npc.current_state = "Moving along path"

		return first_available_npc, build_Spot
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


def update_dicts(main_interest_Spots_dict: dict, npc: NPC, main_discovered_Spots: dict):
	for key in npc.resource_pos_dict.keys():
		for val in npc.resource_pos_dict[key]:
			if val not in main_interest_Spots_dict[key] and npc.discovered_Spots[val] == 1:
				if val.type == key:
					main_interest_Spots_dict[key].append(val)
					print("Added", val.type, "at Row:", val.row, "Col: ", val.col)
					npc.discovered_Spots[val] = 2

	for key in npc.discovered_Spots.keys():
		if key not in main_discovered_Spots:
			main_discovered_Spots.setdefault(key, 1)


def main(win, width):
	ROWS = 100
	grid = []
	make_grid(ROWS, width, grid)
	start = Spot
	end = Spot
	discovered_Spots = {}
	start, end, discovered_Spots = load_map(grid, 4)
	oblivionNPCs = [NPC(24, 24, width, "0. Steffe")]
	oblivionNPCs.append(NPC(22, 22, width, "1. Sven"))
	oblivionNPCs.append(NPC(22, 22, width, "2. Georg"))
	oblivionNPCs.append(NPC(22, 22, width, "3. Roffe"))
	oblivionNPCs.append(NPC(22, 22, width, "4. SvetsarN"))
	oblivionNPCs.append(NPC(22, 22, width, "5. Svets"))

	for i in range(45):
		oblivionNPCs.append(NPC(22, 22, width, str(i) + ". Nånting"))

	master_task_list = []
	resource_storage_dict = {
		"Wood": 0,
		"Iron": 0,
		"Charcoal": 0,
		"Iron bar": 0,
		"Sword": 0
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

	design_doc_dict = {}

	for row in grid:
		for spot in row:
			spot.update_neighbors(grid)

	crafting_error = ""
	run = True
	    
	ai_master_timer = 0
	avaiable_workers_count = 0

	print("Started Reading JSON file")
	with open("variables.json", "r") as read_file:
		print("Starting to convert json decoding")
		design_doc_dict = json.load(read_file)

		print("Decoded JSON Data From File")
		for key, value in design_doc_dict.items():
			print(key, ":", value)
		print("Done reading json file")

	for key in design_doc_dict["item_recipies"]["Iron bar"]:
		print(key, ":", design_doc_dict["item_recipies"]["Iron bar"][key])

	go_to_school(oblivionNPCs[0], grid, "Builder", design_doc_dict, interest_spots_dict["School"])
	go_to_school(oblivionNPCs[1], grid, "Explorer", design_doc_dict, interest_spots_dict["School"])
	go_to_school(oblivionNPCs[2], grid, "Deep_Explorer", design_doc_dict, interest_spots_dict["School"])
	go_to_school(oblivionNPCs[3], grid, "Deep_Explorer", design_doc_dict, interest_spots_dict["School"])


	startTime = time.perf_counter()
	while run:
		draw(win, grid, ROWS, width, oblivionNPCs)

		if resource_storage_dict["Charcoal"] > 200:
			print("we did it guys")
			print("Charcoal:", resource_storage_dict["Charcoal"])
			break

		if ai_master_timer <= 0:
			ai_master_timer = 2
			if len(master_task_list) > 0:
				if crafting_error == "No kiln":
					if master_task_list[0][0] == "Building kiln":
						#working_on_it = True
						print("working on building a kiln from crafting error")
				elif crafting_error == "No kiln operator":
					if master_task_list[0][0] == "Training kiln operator":
						#working_on_it = True
						print("working on training kiln operator")
				elif crafting_error == "" or crafting_error == None:
					if master_task_list[0] == "Producing charcoal":
						#working_on_it = True
						print("Working on producing charcoal")
				elif master_task_list[0][0] == "Building kiln":
					#working_on_it = True
					print("just working on a kiln")

					
					
			else:
				#working_on_it = False
				crafting_error = ""
			
			for npc in oblivionNPCs:
				if npc.job == "Worker" and npc.current_state == "":
					avaiable_workers_count += 1


			#if working_on_it == False:
			if avaiable_workers_count > 2:
				if(resource_storage_dict["Wood"] > design_doc_dict["building_recipies"]["Kiln"]["Wood"]):
					if len(interest_spots_dict["Kiln"]) < 5:
						worker_to_become_kiln_operator = None
						first_available_builder = None
						for npc in oblivionNPCs:
							if npc.job == "Worker" and npc.current_state == "" and worker_to_become_kiln_operator == None:
								worker_to_become_kiln_operator = npc
							elif npc.job == "Builder" and npc.current_state == "" and first_available_builder == None:
								first_available_builder = npc

						if worker_to_become_kiln_operator != None and first_available_builder != None:
							master_task_list.append(("Building kiln", build_building("kiln", resource_storage_dict, interest_spots_dict, discovered_Spots, grid, oblivionNPCs, design_doc_dict)))
							go_to_school(worker_to_become_kiln_operator, grid, "Kiln operator", design_doc_dict, interest_spots_dict["School"])
						else:
							print("no available builders or workers")
						continue
							

					crafting_error = craft_item("Charcoal", resource_storage_dict, interest_spots_dict, grid, oblivionNPCs, design_doc_dict)
					if crafting_error:
						if crafting_error == "No kiln":
							master_task_list.append(("Building kiln", build_building("kiln", resource_storage_dict, interest_spots_dict, discovered_Spots, grid, oblivionNPCs)))
						elif crafting_error == "No kiln operator":
							for npc in oblivionNPCs:
								if npc.job == "Worker":
									if npc.current_state == "":
										go_to_school(npc, grid, "Kiln operator", design_doc_dict, interest_spots_dict["School"])
										break
							master_task_list.append(("Training kiln operator", npc))
						elif crafting_error == "No available kiln operator":
							print("woah chill out man")
					else:
						master_task_list.append(("Producing charcoal"))
					
				else:
					if len(interest_spots_dict["Tree"]) > 0:
						print("going to gather wood")
						gather_resource("Tree", interest_spots_dict, oblivionNPCs, grid)
		else:
			ai_master_timer -= 1

		for npc in oblivionNPCs:
			npc.update(grid, interest_spots_dict, resource_storage_dict, master_task_list, design_doc_dict)
			if npc.job == "Explorer" or npc.job == "Deep_Explorer":
				update_dicts(interest_spots_dict, npc, discovered_Spots)

		# keybindings not used anymore
		""" for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			
			if pygame.mouse.get_pressed()[0]: # left click
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				print("Row:", row, "Col:", col)
				try:
					grid[row][col].tree_list.pop()
				except:
					print("not a tree anymore or at all")
				
				

			elif pygame.mouse.get_pressed()[2]: # right click
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				path_list = astar(grid, grid[oblivionNPCs[4].row][oblivionNPCs[4].col], grid[row][col], oblivionNPCs[4])
				if path_list == False:
					print("Nope")
				else:
					for spot in path_list[::-1]:
						oblivionNPCs[4].path_queue.put(spot)
						oblivionNPCs[4].current_state = "Moving along path"
					print("yep")

		
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

				elif event.key == pygame.K_l: # Produce stuff test
					craft_item("Sword", resource_storage_dict, interest_spots_dict, grid, oblivionNPCs)
					
					


				elif event.key == pygame.K_b and start and end: # Explore Wide test
					for npc in oblivionNPCs:
						for row in grid:
							for spot in row:
								spot.update_neighbors(grid)

						npcSpot = grid[npc.row][npc.col]
						discovered_resource_spots_dict, discovered_Spots = explore_wide(lambda: draw(win, grid, ROWS, width), npcSpot, oblivionNPCs, grid, discovered_Spots)
						for key in discovered_resource_spots_dict.keys():
							for val in discovered_resource_spots_dict[key]:
								interest_spots_dict[key].append(val)
				
				elif event.key == pygame.K_g: # multi character testing test DEPRECATED
					pass
			
				if event.key == pygame.K_u: # singlestepping update DEPRECATED
					pass



				if event.key == pygame.K_s: # Go to school test
					#go_to_school(oblivionNPCs[0], grid, "Deep_Explorer", interest_spots_dict["School"])
					pass

				elif event.key == pygame.K_a:
					go_to_school(oblivionNPCs[1], interest_spots_dict["School"], grid, "Builder")


				elif event.key == pygame.K_d and start and end: # Explore Deep test
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = explore_deep(lambda: draw(win, grid, ROWS, width), npcPosition, oblivionNPCs[0], discovered_Spots, grid)
				
				elif event.key == pygame.K_g and start and end: # Custom Greedy test
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					npcPosition = grid[oblivionNPCs[0].row][oblivionNPCs[0].col]
					pathList = custom_greedy(lambda: draw(win, grid, ROWS, width), grid, npcPosition, end)
					
					for spot in pathList[::-1]:
						oblivionNPCs[0].go_to_Spot_instantly(grid, spot)
						draw(win, grid, ROWS, width, oblivionNPCs)
					end = None
				

				elif event.key == pygame.K_h: # Custom test
					resource_storage_dict["Wood"] += 20
					print("adding wood")

				elif event.key == pygame.K_c: # clear
					start = None
					end = None
					grid = make_grid(ROWS, width) 
					reset_map(grid)

		# on hold y update DEPRECATED
		if pygame.key.get_pressed()[pygame.K_y]: 
			pass """

			

	endTime = time.perf_counter()
	print("Elapsed game time:", (endTime-startTime) / 60, "minutes")

	pygame.quit()

if __name__ == "__main__":
	main(WIN, WIDTH)

