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
    print(f"\nBest epsilon value: {best_epsilon}")
    return best_epsilon

# Get the best epsilon value from define_epsilon
epsilon = define_epsilon()


def calc_schedule(epsilon):
    env = bd.CustomBanditzones()
    epsilon_values = [epsilon]
    calc_schedule_optimizer = agent.EpsilonGreedyBandit(env, epsilon_values, n_steps=20)
    calc_schedule_optimizer.run_simulation()

# Pass the best epsilon value to calc_schedule
calc_schedule(epsilon)

def Upperlevel_network():    
    # Initialize the GraphAnalyzer with nodes and connections from BIM_mockup
    analyzer = UN.GraphAnalyzer(BIM.nodes, BIM.connections_list)

    # Define source and target nodes
    source_node = BIM.nodes[1]  
    target_node = BIM.nodes[5]

    # Find the shortest path
    shortest_path = analyzer.find_shortest_path(source_node, target_node)
    if shortest_path:
        print("Shortest path:", shortest_path)

    return shortest_path
    
def Lowerlevel_network():
    image_path = "construction_site_bk.jpg"
    # Define start and goal points based on your BIM_mockup nodes
       
    start = start_node
    goal = target_node

    # Create an instance of the RRTStar class
    rrt_star_instance = LN.RRTStar(image_path, start, goal)

    # Run the RRT* algorithm with smoothing enabled
    tree, smoothed_path = rrt_star_instance.rrt_star_with_smoothing(smooth=True)

    # Calculate the length of the smoothed path
    length_of_smooth_path = rrt_star_instance.calculate_path_length(smoothed_path)
    print(f"Length of the smoothed path: {length_of_smooth_path}")

    # Plot the results
    rrt_star_instance.plot_results(smoothed_path)


