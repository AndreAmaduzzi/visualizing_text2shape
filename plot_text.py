'''

This script plots worldclouds to visualize the most frequent words of the dataset.

'''

import argparse
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import csv
import os

def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--csv_path', type=str, default='input_examples/captions.tablechair.csv',
                        help='path to CSV file with textual descriptions')
    
    parser.add_argument('--category', type=str, default='all', choices=['Chair', 'Table', 'All'],
                        help='category of shapes to be analyzed')
   
    parser.add_argument('--output_folder', type=str, default='output_plots/',
                        help='path to the image to save')
    

    args = parser.parse_args()
    return args
    
def build_text(csv_path, category):
    text_prompts = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if category != 'all':
                if row["category"] == category:
                    text_prompt = row['description']
                    text_prompt = text_prompt.lower()
                    text_prompts.append(text_prompt)   
            else:
                text_prompt = row['description']
                text_prompt = text_prompt.lower()
                text_prompts.append(text_prompt)   

    all_texts = "\n\n".join(text_prompts)
    return all_texts, text_prompts

def main():
    args = parse_args()
    print(args)
    print(f'Building WordCloud for category {args.category}...')
    merged_texts, all_prompts = build_text(args.csv_path, args.category)
    print(f'Built {len(all_prompts)} text prompts')
    wordcloud = WordCloud(width = 800, height = 800,
                background_color ='black',  
                colormap='viridis',              
                min_font_size = 10).generate(merged_texts)
 
    # plot the WordCloud image                      
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    plt.savefig(os.path.join(args.output_folder, f'worcloud_{args.category}.png'))
    plt.show()

if __name__ == "__main__":
    main()