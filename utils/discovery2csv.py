'''Convert discovery items to tracker items.

Use Python 3.
'''
import argparse
import glob
import itertools
import gzip
import json
import csv


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('directory')
    arg_parser.add_argument('csv_file')
    arg_parser.add_argument('type', choices=['flv', 'user', 'video'])
    
    args = arg_parser.parse_args()
    filenames = itertools.chain(
        glob.iglob(args.directory + '/*.gz'),
        glob.iglob(args.directory + '/*/*.gz'),
    )

    with open(args.csv_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        
        if args.type == 'flv':
            writer.writerow(['video_id', 'index', 'url', 'type'])
        elif args.type == 'user':
            # is a plaintext file, no header needed
            pass
        elif args.type == 'video':
            writer.writerow(['video_id', 'views'])
        else:
            raise Exception('Unsupported CSV type')
    
        for filename in filenames:
            with gzip.GzipFile(filename, mode='rb') as in_file:
                doc = json.loads(in_file.read().decode())
            
            if 'video_type' in doc and args.type == 'flv':
                flv_file_discovery(doc, writer)
            elif doc['type'] == 'discovery':
                if args.type == 'user':
                    user_discovery(doc, writer)
                else:
                    video_discovery(doc, writer)
            else:
                raise Exception('Unsupported discovery result')


def flv_file_discovery(doc, writer):
    if len(doc['urls']) == 0:
        writer.writerow([doc['id'], -1, None, None])

    for index in range(len(doc['urls'])):
        url = doc['urls'][index]
        writer.writerow([doc['id'], index, url, doc['video_type']])


def user_discovery(doc, writer):
    for user in users:
        writer.writerow([user])


def video_discovery(doc, writer):
    for video_id, views in doc['videos']:
        writer.writerow([video_id, views])
    

if __name__ == '__main__':
    main()
