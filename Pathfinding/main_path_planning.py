import json
import bandit as bd
import agent as agent
import Lowerlevel_network as LN
import Upperlevel_network as UN
import BIM_mockup as BIM

def define_epsilon():
    # Initialize the environment and epsilon values
    env = bd.CustomBanditzones()
    epsilon_values = [0.5, 0.4, 0.3, 0.2, 0.1]

    # Create an instance of EpsilonGreedyOptimizer
    optimizer = agent.EpsilonGreedyBandit(env, epsilon_values, n_steps=1000)

    # Run the simulation
    optimizer.run_simulation()

    # Get the best epsilon value
    best_epsilon = optimizer.get_best_epsilon()
    return best_epsilon

def calc_schedule(epsilon):
    env = bd.CustomBanditzones()
    epsilon_values = [epsilon]
    calc_schedule_optimizer = agent.EpsilonGreedyBandit(env, epsilon_values, n_steps=20)
    schedule = calc_schedule_optimizer.run_simulation()

    # Remove exact duplicates from the schedule
    def remove_exact_duplicates(lst):
        if not lst:
            return []  # Handle empty list case
        result = [lst[0]]  # Start with the first element

        for i in range(1, len(lst)):
            # Only append if current element is different from the previous one
            if lst[i] != lst[i-1]:
                result.append(lst[i])

        return result

    # Clean up the schedule by removing consecutive duplicates
    newschedule = remove_exact_duplicates(schedule)
    
    return newschedule

def load_cordinates_from_json_or_BIM(file_path):
    with open(file_path, 'r') as file:
        coordinates = json.load(file)
    return coordinates

def run_Upperlevel_network(schedule, coordinates):    
    # Initialize the GraphAnalyzer with nodes and connections from BIM_mockup  
    analyzer = UN.GraphAnalyzer(BIM.nodes, BIM.connections_list)

    # Define a dictionary of nodes with their positions (coordinates)
    nodes = BIM.nodes

    # Initialize the NodeLocator with the nodes
    locator = UN.NodeLocator(nodes)

    # This should itterate for al the locations in the planning
    source_zone = schedule[0]
    target_zone = schedule[1]

    # Define source and target locations (coordinates)
    source_location = tuple(coordinates.values())[source_zone]['location']
    target_location = tuple(coordinates.values())[target_zone]['location']

    # Find the closest nodes to the source and target locations
    closest_to_source = locator.find_closest_node(source_location)
    closest_to_target = locator.find_closest_node(target_location)

    # Print the results
    print(f"Closest node to current location {source_location} is node: {closest_to_source[0]} at {closest_to_source[1]}")
    print(f"Closest node to target location {target_location} is node: {closest_to_target[0]} at {closest_to_target[1]}")

    # Find the shortest path
    shortest_path = analyzer.find_shortest_path(closest_to_source[0], closest_to_target[0])
    if shortest_path:
        print("Shortest path:", shortest_path)

    return shortest_path, source_location, target_location
    
def run_Lowerlevel_network(shortest_path, source_location, target_location):
    image_path = "construction_site_bk.jpg"
    all_paths = []

    # Calculate path from zone location to first node
    rrt_star_planner = LN.RRTStar(image_path, source_location, BIM.nodes[shortest_path[0]])
    path_to_closest_node = rrt_star_planner.rrt_star_with_smoothing(smooth=False)  # No smoothing for initial segment
    all_paths.extend(path_to_closest_node)

    for i in range(len(shortest_path) - 1):
        start = BIM.nodes[shortest_path[i]]
        goal = BIM.nodes[shortest_path[i + 1]]
        rrt_star_planner = LN.RRTStar(image_path, start, goal)

        # Get the path from RRT* without smoothing
        path_segment = rrt_star_planner.rrt_star_with_smoothing(smooth=False)

        # Append the new path segment, excluding the first point of the new segment (to avoid duplicate points at the junction)
        if len(all_paths) > 0:
            all_paths.extend(path_segment[1:])  # Skip the first point to avoid duplication
        else:
            all_paths.extend(path_segment)  # If first segment, add all points

    # Calculate path from last node to target location
    rrt_star_planner = LN.RRTStar(image_path, BIM.nodes[shortest_path[-1]], target_location)
    path_to_target_node = rrt_star_planner.rrt_star_with_smoothing(smooth=False)  # No smoothing for this segment
    all_paths.extend(path_to_target_node)

    # Now smooth the combined path once
    rrt_star_planner = LN.RRTStar(image_path, all_paths[0], all_paths[-1])
    smoothed_path = rrt_star_planner.smooth_path(all_paths)  # Smooth the entire combined path

    # Plot the result
    rrt_star_planner.plot_result(smoothed_path)
    print(f'The combined path consists of these coordinates: {smoothed_path}')
    
    # Calculate the length of the smoothed path
    length_of_all_paths = rrt_star_planner.calculate_path_length(smoothed_path)
    print("Length of the smoothed path:", length_of_all_paths)

if __name__ == "__main__":
    best_epsilon = define_epsilon()
    print(f"The best epsilon is: {best_epsilon}")
    listschedule = calc_schedule(best_epsilon)
    print("New Schedule:", listschedule)
    
    coordinates = load_cordinates_from_json_or_BIM("zone_id.json")

    for i in range(len(listschedule)-1):
        schedule = [listschedule[i], listschedule[i+1]]
        print(schedule)
        shortest_path, source_location, target_location = run_Upperlevel_network(schedule, coordinates)
        if shortest_path:
            run_Lowerlevel_network(shortest_path, source_location, target_location)