import time

# Straight Robot Path
def simulate_robot_path():
    """Simulate the robot moving through zones"""
    # For simplicity, let's simulate the robot moving through zones. 
    # Starting from x=0 and increasing x over time
    # Speed and range can be adjusted 

    for x in range(0,200):
        y = 50               # Keep y constant for simplicity, can modify for path
        z = 0               # Assuming 2D plane
        yield (x, y, z)
