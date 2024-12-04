from collections import deque
import heapq
import random

# Helper functions
def is_wall_in_row(environment, router_x, router_y, target_x, target_y):
    """Check if there's a wall between the router and the target cell in the same row."""
    if router_x != target_x:  # Ensure they are on the same row
        return False
    for j in range(min(router_y, target_y) + 1, max(router_y, target_y)):  # Loop between router and target
        if environment[router_x][j] == 'W':  # Check for walls
            return True
    return False

def is_wall_in_column(environment, router_x, router_y, target_x, target_y):
    """Check if there's a wall between the router and the target cell in the same column."""
    if router_y != target_y:  # Ensure they are in the same column
        return False
    for i in range(min(router_x, target_x) + 1, max(router_x, target_x)):  # Loop between router and target
        if environment[i][router_y] == 'W':  # Check for walls
            return True
    return False

def is_wall_in_diagonal(environment, router_x, router_y, target_x, target_y):
    """Check if there's a wall between the router and the target cell on a diagonal."""
    if abs(router_x - target_x) != abs(router_y - target_y):  # Ensure they are on a diagonal
        return False
    dx = 1 if target_x > router_x else -1
    dy = 1 if target_y > router_y else -1
    nx, ny = router_x + dx, router_y + dy

    while nx != target_x and ny != target_y:  # Traverse the diagonal
        if environment[nx][ny] == 'W':  # Check for walls
            return True
        nx += dx
        ny += dy

    return False

def wall_between_router_pos(environment, router_x, router_y, target_x, target_y):
    """
    Check if there's a wall between the router and the target cell, considering rows, columns, and diagonals.

    Args:
        environment (list of list of str): The grid environment where 'R' = Room, '.' = Open space, 'W' = Wall.
        router_x (int): The row index of the router.
        router_y (int): The column index of the router.
        target_x (int): The row index of the target cell.
        target_y (int): The column index of the target cell.

    Returns:
        bool: True if there is a wall between the router and the target cell, False otherwise.
    """
    # Check for walls in the row, column, or diagonal between the router and the target
    if is_wall_in_row(environment, router_x, router_y, target_x, target_y):
        return True
    if is_wall_in_column(environment, router_x, router_y, target_x, target_y):
        return True
    if is_wall_in_diagonal(environment, router_x, router_y, target_x, target_y):
        return True
    return False

def calculate_router_coverage(environment, router_range, x, y):
    """Calculates the set of rooms ('R') that would be covered by placing a router at the position (x, y).

    Args:
        environment (list of list of str): The grid environment where 'R' = Room, '.' = Open space, 'W' = Wall.
        range (int): The signal range of the router, defined by Manhattan distance.
        x (int): The row index where the router is placed.
        y (int): The column index where the router is placed.

    Returns:
        set: A set of coordinates representing all 'R' cells (rooms) covered by the router at (x, y).
    """



    rows, cols = len(environment), len(environment[0])
    covered_rooms = set()

    for dx in range(-router_range, router_range + 1):
        for dy in range(-router_range, router_range + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                if ((dx**2) + (dy**2) <= (router_range**2) and environment[nx][ny] == "R"):
                    if environment[nx][ny] == 'R' and not wall_between_router_pos(environment, x, y, nx, ny):
                        covered_rooms.add((nx, ny))
    return covered_rooms

def expand_frontier(environment, routers):
    rows, cols = len(environment), len(environment[0])
    possible_router_placements = []

    for x in range(rows):
        for y in range(cols):
            # Check if the position is open and not already occupied by a router
            if environment[x][y] == '.' and (x, y) not in routers:
                possible_router_placements.append((x, y))

    return possible_router_placements


# BFS
def bfs_router_placement(environment, router_range, num_children=None, max_depth=4):
    rows, cols = len(environment), len(environment[0])

    if num_children is None:
        num_children = rows * cols

    queue = deque()
    visited = set()

    initial_state = ([], set(), 0)
    queue.append(initial_state)

    all_rooms = {(i, j) for i, row in enumerate(environment) for j, cell in enumerate(row) if cell == 'R'}

    explored_paths = []  
    nodes_expanded = 0
    while queue:
        routers, covered_rooms, depth = queue.popleft()

        explored_paths.append(routers)
        nodes_expanded += 1

        # Stop expanding if max depth is reached
        if depth == max_depth:
            continue


        if covered_rooms == all_rooms:
            return {
                "explored_paths": explored_paths,
                "nodes_expanded": nodes_expanded,
                "router_placement": routers
            }
        
        possible_children = expand_frontier(environment, routers)
        
        possible_children_coverages = []
        for x, y in possible_children:
            new_coverage = calculate_router_coverage(environment, router_range, x, y)
            additional_coverage = new_coverage - covered_rooms  # Uncovered rooms this router will cover
            possible_children_coverages.append(((x, y), len(additional_coverage)))

        possible_children_coverages.sort(key=lambda item: item[1], reverse=True)
        top_children = [pos for pos, _ in possible_children_coverages[:num_children]]

        for x, y in top_children:
            new_coverage = calculate_router_coverage(environment, router_range, x, y)
            new_routers = routers + [(x, y)]
            new_covered_rooms = covered_rooms.union(new_coverage)

            if tuple(sorted(new_routers)) not in visited:
                visited.add(tuple(sorted(new_routers)))
                queue.append((new_routers, new_covered_rooms, depth + 1))

    return None

# heruristics 
def heuristic_maximize_new_coverage(environment, current_router_positions, router_range, x, y):
    """
    maximize covering new places minimize router coverage overlap
    """
    rows, cols = len(environment), len(environment[0])

    covered = set()
    for rx, ry in current_router_positions:
        for dx in range(-router_range, router_range + 1):
            for dy in range(-router_range, router_range + 1):
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < rows and 0 <= ny < cols and (dx**2 + dy**2) <= router_range**2:
                    covered.add((nx, ny))

    new_coverage = set()
    for dx in range(-router_range, router_range + 1):
        for dy in range(-router_range, router_range + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (dx**2 + dy**2) <= router_range**2:
                new_coverage.add((nx, ny))

    unique_new_coverage = new_coverage - covered
    return -len(unique_new_coverage)  

def heuristic_central_and_edge(environment, current_router_positions, router_range, x, y):
    """
    Heuristic to prioritize placements that minimize the average distance of all routers to the center.
    """
    rows, cols = len(environment), len(environment[0])
    center_x, center_y = rows / 2, cols / 2

    # Include the new router in the list
    all_routers = current_router_positions + [(x, y)]

    # Calculate the distance to the center for each router
    total_distance = 0
    for rx, ry in all_routers:
        dist_to_center = (((center_x - rx) ** 2) + ((center_y - ry) ** 2)) ** 0.5
        total_distance += dist_to_center

    # Return the average distance
    average_distance = total_distance / len(all_routers)
    return average_distance

def heuristic_random(environment, current_router_positions, router_range, x, y):
    return random.randint(1, 10)
# A* 
def A_star_router_placement(environment, router_range,heuristic=None, num_children=None, max_depth=4, h_factor = 1):
    rows, cols = len(environment), len(environment[0])

    if num_children is None:
        num_children = rows * cols

    priority_queue = []
    visited = set()

    initial_state = (0, [], set(), 0)
    heapq.heappush(priority_queue, initial_state)
    
    all_rooms = {(i, j) for i, row in enumerate(environment) for j, cell in enumerate(row) if cell == 'R'}

    explored_paths = []  
    nodes_expanded = 0
    while priority_queue:
        f, routers, covered_rooms, depth = heapq.heappop(priority_queue)
        print(f"State: {routers}, f={f}")

        explored_paths.append(routers)
        nodes_expanded += 1

        # Stop expanding if max depth is reached
        if depth == max_depth:
            continue


        if covered_rooms == all_rooms:
            return {
                "explored_paths": explored_paths,
                "nodes_expanded": nodes_expanded,
                "router_placement": routers
            }
        
        possible_children = expand_frontier(environment, routers)
        
        possible_children_coverages = []
        for x, y in possible_children:
            new_coverage = calculate_router_coverage(environment, router_range, x, y)
            additional_coverage = new_coverage - covered_rooms  # Uncovered rooms this router will cover
            possible_children_coverages.append(((x, y), len(additional_coverage)))

        possible_children_coverages.sort(key=lambda item: item[1], reverse=True)
        top_children = [pos for pos, _ in possible_children_coverages[:num_children]]

        for x, y in top_children:
            new_coverage = calculate_router_coverage(environment, router_range, x, y)
            new_routers = routers + [(x, y)]
            new_covered_rooms = covered_rooms.union(new_coverage)

            g = len(new_routers)
            h = heuristic(environment, routers, router_range, x, y) if heuristic else 0
            f = g + (h*h_factor)  # Total cost for A*
            
            if tuple(sorted(new_routers)) not in visited:
                visited.add(tuple(sorted(new_routers)))
                heapq.heappush(priority_queue, (f, new_routers, new_covered_rooms, depth + 1))

    return None
