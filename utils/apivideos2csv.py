'''Convert video JSON data into CSV list.

The JSON documents should be from
 https://api.twitch.tv/kraken/videos/top?limit=20&offset=0&period=all
'''

import argparse
import csv
import json
import glob


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('directory')
    arg_parser.add_argument('csv_filename')
    args = arg_parser.parse_args()
    
    with open(args.csv_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['id', 'url', 'date', 'views', 'length'])
        
        for filename in sorted(glob.glob(args.directory + '/*.json')):
            with open(filename) as json_file:
                doc = json.load(json_file)
            
            for video in doc['videos']:
                writer.writerow([video['_id'], video['url'], video['recorded_at'], video['views'], video['length']])


if __name__ == '__main__':
    main()
