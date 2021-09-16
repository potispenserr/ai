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