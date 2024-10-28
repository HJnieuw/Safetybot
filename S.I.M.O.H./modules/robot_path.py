import numpy as np

def simulate_robot_path(step=2):
    """Simulate a robot moving through zones, yielding [x, y, z] coordinates.
    Input: step (int): Step size for interpolation.
    Output: list: The next point on the path [x, y, z]"""
    
    dataset_points = [
        [[1257, 1600], [1098, 1442], [511, 1646], [363, 1542]],
        [[363, 1542], [516, 1654.54353453], [1146, 1436], [1573, 1390.5453534], [1588, 705]],
        [[1588, 705], [2527, 760], [2506, 812]]
    ]

    # dataset_points = [
    #     [1588, 705, 0],
    #     [1777, 715, 0],
    #     [2199, 1403, 0],
    #     [2643, 1405, 0],
    #     [2714, 1290, 0],
    #     [2787, 1335, 0]
    # ]
    
    # Loop over each path in dataset_points
    for path in dataset_points:
        # Loop over each segment within the current path
        for i in range(len(path) - 1):
            # Define start and end points
            start = np.array(path[i])
            end = np.array(path[i + 1])

            # Calculate direction and distance
            direction = end - start
            distance = np.linalg.norm(direction)
            num_steps = int(distance // step)

            # Yield interpolated points
            if num_steps == 0:
                yield list(map(int, start))
            else:
                unit_direction = direction / distance
                for j in range(num_steps):
                    yield list(map(int, start + unit_direction * step * j))
            
            # Yield the end point to ensure complete coverage
            yield list(map(int, end))