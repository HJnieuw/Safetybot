import time

def generate_points():
    for x in range(0, 50):
        y = 0   # Keep y constant for simplicity
        z = 0   # Assuming 2D plane
        yield (x, y, z)
        time.sleep(0.5)  # Wait for 0.5 seconds to simulate time passing

# Example usage: Printing the points
for point in generate_points():
    print(point)
