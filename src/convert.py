#encoding: utf-8
#
# Modified from waveshare source
#
# Convert images to 800by600 for the waveshare eink photo frame
#
# Convert an image file to a a bmp image
# if filename is a directory then convert all non bmp files to bmp's
#

import sys
import os.path
import argparse
from typing import List
from PIL import Image, ImagePalette, ImageOps


def is_directory(path: str) -> bool:
    """Checks if the given path is a directory."""
    return os.path.isdir(path)


def is_bmp_image(filepath: str) -> bool:
    """Checks if the given file is not a BMP image based on its extension."""
    return filepath.lower().endswith('.bmp')


def is_valid_image(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()  # Verifies the file can be opened as an image
        return True
    except (IOError, SyntaxError):
        return False


def list_filenames(directory: str) -> List:
    """Lists all filenames in the given directory."""
    try:
        # Get a list of filenames in the directory
        filenames = os.listdir(directory)

        # Filter out only files (not subdirectories)
        filenames = [f for f in filenames if os.path.isfile(os.path.join(directory, f))]

        return filenames
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' was not found.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{directory}'.")
        return []


def convert_to_bmp(input_filename: str, display_orientation: str, display_dither: int, verbose: bool) -> bool:
    # Check whether the input file exists
    if not os.path.isfile(input_filename):
        print(f'Error: file {input_filename} does not exist')
        return False

    if not is_valid_image(input_filename):
        return False

    # Read input image
    input_image = Image.open(input_filename)

    # Get the original image size
    width, height = input_image.size

    # Specified target size
    if display_orientation:
        if display_orientation == 'landscape':
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800
    else:
        if  width > height:
            target_width, target_height = 800, 480
        else:
            target_width, target_height = 480, 800

    if verbose:
        print(f"{input_filename} {width} by {height} ({(height/width):0.3f}), Output BMP {target_width} by {target_height}, ({(target_height/target_width):0.3f})")

    # Computed scaling
    scale_ratio = max(target_width / width, target_height / height)

    # Calculate the size after scaling
    resized_width = int(width * scale_ratio)
    resized_height = int(height * scale_ratio)

    # Resize image
    output_image = input_image.resize((resized_width, resized_height))

    # Create the target image and center the resized image
    resized_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
    left = (target_width - resized_width) // 2
    top = (target_height - resized_height) // 2
    resized_image.paste(output_image, (left, top))

    # Create a palette object
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)
    
    # The color quantization and dithering algorithms are performed, and the results are converted to RGB mode
    quantized_image = resized_image.quantize(dither=display_dither, palette=pal_image).convert('RGB')

    # Save output image
    output_filename = os.path.splitext(input_filename)[0] + '.8b6.bmp'
    if  display_orientation == 'landscape':
        output_filename = os.path.splitext(input_filename)[0] + '.6b8.bmp'
    quantized_image.save(output_filename)

    return True


# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Convert images to 800by600 for the waveshare eink photo frame.')

parser.add_argument('image_file', type=str, help='Input image file or directory')
parser.add_argument('--orient', choices=['landscape', 'portrait'], nargs='?', type=str, const='portrait', default='portrait', help='Image orientation')
parser.add_argument('--dither', type=int, nargs='?', const=Image.FLOYDSTEINBERG, choices=[Image.NONE, Image.FLOYDSTEINBERG], default=Image.FLOYDSTEINBERG, help='Image dithering algorithm (NONE(0) or FLOYDSTEINBERG(3))')
parser.add_argument('--verbose', type=bool, nargs='?', const=False, default=False, help='Verbose output')

# Parse command line arguments
args = parser.parse_args()

# Get command line parameters
filename = args.image_file   # may be a directory name
orientation = args.orient
mode = args.mode
dither = Image.Dither(args.dither)
verbose = args.verbose

print(f"Input image: {filename}")
print(f"Orientation: {orientation}")
print(f"Dither     : {dither}")
print(f"Verbose    : {verbose}")

converted_files = 0
if is_directory(filename):
    files = list_filenames(filename)
    for file in files:
        if convert_to_bmp(filename+'/'+file, orientation, dither, verbose):
            converted_files +=1 
    print(f"Converted {converted_files} from {len(files)}")
else: 
    if convert_to_bmp(filename, orientation, dither, verbose):
        converted_files +=1 



