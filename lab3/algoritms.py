""" def dfs(draw, start, end):
	open_stack = queue.LifoQueue()
	open_stack.put(start)
	previous_spots = {start}
	came_from = {}
	while not open_stack.empty():

		current = open_stack.get()

		if current == end:
			list_to_path = reconstruct_path(came_from, end, draw)
			return list_to_path
				
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

def bfs(draw, start, end):
	open_queue = queue.Queue()
	open_queue.put(start)
	previous_spots = {start}
	came_from = {}
	while not open_queue.empty():

		current = open_queue.get()

		if current == end:
			list_to_path = reconstruct_path(came_from, end, draw)
			return list_to_path
		
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
	
	return False # no path found """


""" def explore_wide(draw, start, npc, grid, discovered_Spots):
resource_pos_dict = {}
resource_pos_dict.setdefault("Tree", [])
resource_pos_dict.setdefault("Iron", [])
while not npc.open_queue.empty():
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_b:
				return resource_pos_dict, discovered_Spots

	current = npc.open_queue.get()
	if(manhattan_distance(npc.get_pos(), current.get_pos()) < 4):
		npc.go_to_Spot(grid, current)
	
	else:
		npcSpot = grid[npc.row][npc.col]
		pathList = astar(lambda:draw, grid, npcSpot, current)
		npc.path_list = pathList

		for spot in pathList[::-1]:
			npc.path_list = queue.Queue()
			npc.path_list.put(spot)
		
		if npc.path_list:
			next_Spot = npc.path_list.get()
			npc.go_to_Spot(grid, next_Spot)
			if next_Spot not in discovered_Spots:
				discovered_Spots.append()
				discovered_Spots.append(explore_spots(grid, npc))
		

	discovered_surrounding_Spots = explore_spots(grid, npc, resource_pos_dict)
	for spot in discovered_surrounding_Spots:
		if spot not in discovered_Spots:
			discovered_Spots.append(spot)

	if current not in discovered_Spots:
		discovered_Spots.append(current)

	if current.is_resource()[0]:
		resource_type = current.is_resource()[1]
		if current not in resource_pos_dict[resource_type]:
			resource_pos_dict[resource_type].append(current)



	for neighbor in current.neighbors:
		if neighbor not in discovered_Spots:
			npc.open_queue.put(neighbor)
			discovered_Spots.add(neighbor)
	
	draw()
print(resource_pos_dict)
return resource_pos_dict """