import numpy as np

def simulate_robot_path(step=2):
    """Simulate a robot moving through zones, yielding (x, y, z) coordinates.
    Input: step (int): Step size for interpolation.
    Output: tuple: The next point on the path (x, y, z)"""
    
    dataset_points = [
        (1588, 705, 0),
        (1777, 715, 0),
        (2199, 1403, 0),
        (2643, 1405, 0),
        (2714, 1290, 0),
        (2787, 1335, 0)
    ]

    for i in range(len(dataset_points) - 1):
        # Define start and end points
        start = np.array(dataset_points[i])
        end = np.array(dataset_points[i + 1])

        # Calculate direction and distance
        direction = end - start
        distance = np.linalg.norm(direction)
        num_steps = int(distance // step)

        # Yield interpolated points
        if num_steps == 0:
            yield tuple(map(int, start))
        else:
            unit_direction = direction / distance
            for j in range(num_steps):
                yield tuple(map(int, start + unit_direction * step * j))
        
        # Yield the end point to ensure complete coverage
        yield tuple(map(int, end))