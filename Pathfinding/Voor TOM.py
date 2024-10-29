from Pathfinding.main_path_planning import NetworkPlanner

# Create an instance of NetworkPlanner
planner = NetworkPlanner('assets/BIM.json')
    
# Run the planner
planner.run()
    
# Access the smoothed paths
smoothed_paths = planner.smoothed_paths
    
# Print or process the smoothed paths
print("Smoothed Paths:", smoothed_paths)
