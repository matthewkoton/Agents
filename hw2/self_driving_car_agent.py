from collections import deque
import heapq


def expand(problem, node):
    actions = problem['actions']
    environment = problem['environment']

    next_states = []
    for action in actions:
        next_state = (node[0] + action[0], node[1] + action[1])
        
        # Check if the neighbor is valid and not yet visited
        if (0 <= next_state[0] < len(environment) and 0 <= next_state[1] < len(environment[0]) and environment[next_state[0]][next_state[1]] == 0):
            next_states.append(next_state)
    return next_states

def self_driving_car_BFS_DFS(problem, BFS=True, depth_limit=None):
    '''
    A function for a self-driving car agent which finds the shortest drivable path between the start point and destination.
    Includes depth checking. If depth_limit is provided, the search will not go deeper than this limit.
    
    BFS: If True, uses BFS; otherwise, uses DFS.
    '''

    start = problem['start']
    destination = problem['destination']

    # Setup the frontier based on BFS or DFS
    if BFS:
        frontier = deque([(start, [start], 0)])  # Queue stores (current position, path, depth)
    else:
        frontier = [(start, [start], 0)]  # Stack stores (current position, path, depth)

    visited = set()  # Track visited nodes
    visited.add(start)

    if start == destination:
        return [start]

    while frontier:
        if BFS:
            current_node, path_to_current_node, current_depth = frontier.popleft()
        else:
            current_node, path_to_current_node, current_depth = frontier.pop()

        # Check depth limit
        if depth_limit is not None and current_depth > depth_limit and BFS != True:
            continue  # Skip if depth limit exceeded

        for child in expand(problem, current_node):
            if child == destination:
                return path_to_current_node + [child]
            if child not in visited:
                visited.add(child)
                frontier.append((child, path_to_current_node + [child], current_depth + 1))  # Increment depth

    return None

def self_driving_car_IDS(problem):
    environment = problem["environment"]
    depth = 0
    flattened_length = sum(len(row) for row in environment)

    while depth <= flattened_length:
        result = self_driving_car_BFS_DFS(problem, False, depth)
        if result:
            return result, depth
        depth += 1

def A_star(problem, heuristic):
    start = problem['start']
    goal = problem['destination']

    frontier = []
    heapq.heappush(frontier, (0, start, [start], 0))  # (priority, node, path, g(n))
    reached = {}
    reached[start] = 0

    while frontier:
        _, current_node, path_to_current_node, g = heapq.heappop(frontier)

        if current_node == goal:
            return path_to_current_node
        
        children = expand(problem, current_node)
        children = [(child, 1) for child in children] # every node has 1 cost between it
        for child, cost in children:
            g_new = g + cost 
            f = g_new + heuristic(child)
                
            if child not in reached or g_new < reached[child]:
                reached[child] = g_new
                heapq.heappush(frontier, (f, child, path + [child], g_new))
        
    return None

if __name__ == "__main__":
    # Example problem definition
    problem = {
        'start': (0, 0),
        'destination': (0, 3),
        'actions': [(0, 1), (1, 0), (0, -1), (-1, 0)],  # Right, Down, Left, Up
        'environment': [  # Larger grid with open paths and obstacles
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
    }

    # Run the BFS and DFS algorithms
    for is_bfs in [True, False]:
        search_type = "BFS" if is_bfs else "DFS"
        print(f"Running {search_type}:")
        path = self_driving_car_BFS_DFS(problem, is_bfs, None)
        
        # Print the result
        if path:
            print(f"{search_type} Path found:", path)
        else:
            print(f"{search_type} No path found")

    
    print("IDS: ")
    print(self_driving_car_IDS(problem))


    def heuristic(pos):
        # roads on even columns have more trafic
        x,y = pos
        if y % 2 == 0:
            return 6
        else:
            return 0
        
    print("A*")
    print(A_star(problem, heuristic))