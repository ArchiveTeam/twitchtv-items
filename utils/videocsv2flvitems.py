'''Convert CSV list of videos to tracker discovery items.
'''

import argparse
import csv
import json
import glob


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('csv_filename')
    args = arg_parser.parse_args()
    
    with open(args.csv_filename, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        
        for row in reader:
            video_id = row[0]
            
            if video_id == 'id':
                continue
            
            print('flv:{}'.format(video_id))


if __name__ == '__main__':
    main()
