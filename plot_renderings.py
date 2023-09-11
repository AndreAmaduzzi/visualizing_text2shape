import matplotlib.pyplot as plt
from PIL import Image
import csv
import os
import math
import argparse

def find_descriptions(target_model_id, csv_file):
    descriptions = []
    
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            if row['modelId'] == target_model_id:
                descriptions.append(row['description'])
    
    return descriptions

def read_images(folder_path):
    image_filenames = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            image_path = os.path.join(folder_path, filename)
            image_filenames.append(image_path)
    return image_filenames

def plot_figure(image_paths, text_prompts, save_fig, output_fig):
    # Calculate the number of rows and columns for the grid
    num_images = len(image_paths)
    num_rows = int(math.sqrt(num_images))
    num_cols = int(math.ceil(num_images / num_rows))

    # Create a grid of subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 12))
    plt.style.use('dark_background')

    # Plot descriptions as text in the first subplot
    axes[0, 0].axis('off')
    quoted_descriptions = ['"' + desc + '"' for desc in text_prompts]
    axes[0, 0].text(0.1, 0.5, "\n".join(quoted_descriptions) + "\n\n", fontsize=12, verticalalignment='center', color='white')

    # Plot images in the remaining subplots
    for i, image_filename in enumerate(image_paths):
        row_idx = i // num_cols
        col_idx = i % num_cols
        ax = axes[row_idx, col_idx]
        
        ax.axis('off')  # Turn off axis
        image = Image.open(image_filename)
        ax.imshow(image)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    # Remove any empty subplots
    for i in range(num_images, num_rows * num_cols):
        row_idx = i // num_cols
        col_idx = i % num_cols
        fig.delaxes(axes[row_idx, col_idx])

    if save_fig:
        plt.savefig(output_fig)
    plt.show()

def parse_args():
    parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
    
    parser.add_argument('--csv_path', type=str, default='input_examples/captions.tablechair.csv',
                        help='path to CSV file with textual descriptions')
    
    parser.add_argument('--obj_path', type=str, default='',
                        help='path to OBJ file of the 3D shape')
    
    parser.add_argument('--renders_folder', type=str, default='output_renders/',
                        help='path to folder with renderings')
    
    parser.add_argument('--output_folder', type=str, default='output_plots/',
                        help='path to the image to save')

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    model_id = os.path.splitext(os.path.basename(args.obj_path))[0]
    print('model id: ', model_id)
    
    descriptions = find_descriptions(model_id, args.csv_path)
    print('descriptions: ', descriptions)
    
    renders_folder = os.path.join(args.renders_folder, model_id)
    image_filenames = read_images(folder_path=renders_folder)
    print('image_filenames: ', image_filenames)
    
    output_path = os.path.join(args.output_folder, 'output_renderings.png')
    plot_figure(image_filenames, descriptions, save_fig=True, output_fig=output_path)

if __name__ == '__main__':
    main()