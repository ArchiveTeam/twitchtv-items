'''Convert discovery items to tracker items.

Use Python 3.
'''
import argparse
import glob
import itertools
import gzip
import json


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('directory')
    
    args = arg_parser.parse_args()
    filenames = itertools.chain(
        glob.iglob(args.directory + '/*.gz'),
        glob.iglob(args.directory + '/*/*.gz'),
    )

    for filename in filenames:
        with gzip.GzipFile(filename, mode='rb') as in_file:
            doc = json.loads(in_file.read().decode())
        
        if 'video_type' in doc:
            flv_file_discovery(doc)
        elif doc['type'] == 'discover':
            user_and_video_discovery(doc)
        else:
            raise Exception('Unknown discovery result')


def flv_file_discovery(doc):
    for url in doc['urls']:
        print('url:{}'.format(url))


def user_and_video_discovery(doc):
    for user in doc['users']:
        print('user:{}'.format(user))
    
    for video in doc['videos']:
        print('flv:{}'.format(video[0]))
    

if __name__ == '__main__':
    main()
