from PIL import Image
import numpy as np

def convert_image_to_maze(image_path):
    # Load the image
    img = Image.open(image_path)
    
    # Convert to grayscale
    img = img.convert("L")
    
    # Convert to binary (thresholding)
    threshold = 128  # This value might need adjustment
    binary_img = np.array(img) < threshold  # True for paths, False for walls
    
    # Convert to binary array (1 for wall, 0 for path)
    maze = np.where(binary_img, 0, 1)
    
    return maze

# Example usage
maze = convert_image_to_maze("test.jpg")
