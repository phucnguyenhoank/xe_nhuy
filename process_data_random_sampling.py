import os
import random
import shutil

# Configure paths
source_dir = 'fire_dataset/1_fire'
target_dir = 'fire_dataset/1_fire_mini'
sample_size = 45  # Number of images to sample

# NEW: Create the target directory if it doesn't exist
os.makedirs(target_dir, exist_ok=True)

# List all image files
files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

# Select random files
random_files = random.sample(files, min(len(files), sample_size))

# Copy selected files
for file_name in random_files:
    # Build full paths for source and destination
    src_path = os.path.join(source_dir, file_name)
    # Shutil.copy will now correctly place the file inside the existing target_dir
    shutil.copy(src_path, target_dir)

print(f"Successfully copied {len(random_files)} images to {target_dir}")
