import cv2
import numpy as np
import pathlib
# Load the image
path = pathlib.Path(r"C:\Users\Jonas\Pictures\Bloons_py\maps_ingame\sands_ingame_right.png")


img = cv2.imread(str(path))

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Define the seed points for the different regions
seeds = {
    "ground": [(50, 50), (100, 100)],
    "water": [(200, 200), (250, 250)],
    "no_tower": [(300, 300)],
}

# Define the cutoffs for the left, right, bottom, and top of the spread
left_cutoff = 0
right_cutoff = img.shape[1]
bottom_cutoff = img.shape[0]
top_cutoff = 0

# Define the maximum threshold distance between a pixel and its neighboring pixels
max_distance = 50

# Create an empty mask for the regions
mask = np.zeros_like(gray)

# Perform seeded region growing to identify the different regions
for class_name, class_seeds in seeds.items():
    for i, seed in enumerate(class_seeds):
        if (
            left_cutoff <= seed[0] < right_cutoff and 
            top_cutoff <= seed[1] < bottom_cutoff
        ):
            region_mask = cv2.floodFill(
                image=gray,
                mask=None,
                seedPoint=seed,
                newVal=i+1,
                loDiff=max_distance,
                upDiff=max_distance,
            )[1]
            mask += region_mask * (i+1)

# Save the resulting images to disk
for class_name, class_seeds in seeds.items():
    for i, seed in enumerate(class_seeds):
        if (
            left_cutoff <= seed[0] < right_cutoff and 
            top_cutoff <= seed[1] < bottom_cutoff
        ):
            region_mask = (mask == i+1).astype(np.uint8) * 255
            cv2.imwrite(f"{class_name}_{i+1}.png", region_mask)
