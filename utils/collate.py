'''Read the CSVs and collate them into queryable database'''
import argparse
import csv
import os.path
import re
import shelve


HIGHLIGHTS = ['highlights_top.csv', 'highlights_top_02.csv', 'highlights_top_03.csv']
FLV_URLS = ['highlights_top_flv_01.csv', 'highlights_top_flv_02-03.csv', 'disco_top_1000_views_flv.csv']
VIDEO_TOP = ['video_top_discovery.csv']


def main():
    arg_parser = argparse.ArgumentParser()
    subparsers = arg_parser.add_subparsers(title='commands')

    import_parser = subparsers.add_parser('import')
    import_parser.set_defaults(func=import_data)

    get_flv_parser = subparsers.add_parser('getflv')
    get_flv_parser.add_argument('video_id')
    get_flv_parser.set_defaults(func=get_flv)

    get_flv_list_parser = subparsers.add_parser('getflvlist')
    get_flv_list_parser.add_argument('video_ids_file', type=argparse.FileType('r'))
    get_flv_list_parser.set_defaults(func=get_flv_list)

    count_parser = subparsers.add_parser('count')
    count_parser.add_argument('type', default='videos', choices=['videos', 'flvs'])
    count_parser.add_argument('--views-limit', type=int)
    count_parser.set_defaults(func=count_command)

    missing_flv_parser = subparsers.add_parser('missingflv')
    missing_flv_parser.add_argument('--views-limit', type=int)
    missing_flv_parser.add_argument('--user')
    missing_flv_parser.set_defaults(func=missing_flv_command)

    args = arg_parser.parse_args()
    args.db = shelve.open('twitchy.db')
    args.func(args)
    args.db.close()


def import_data(args):
    db = args.db

    for filename in HIGHLIGHTS:
        with open(os.path.join('..', 'csv', filename), 'r') as in_file:
            print('Processing', filename)
            reader = csv.reader(in_file)

            for row in reader:
                if not row:
                    continue

                video_id, url, date, views, length = row

                if video_id == 'id':
                    continue

                views = int(views)

                match = re.search(r'twitch\.tv/([^/]+)', url)
                user = match.group(1)

                doc = db.get(video_id, {})

                doc['user'] = user
                doc['views'] = views

                db[video_id] = doc

    for filename in FLV_URLS:
        with open(os.path.join('..', 'csv', filename), 'r') as in_file:
            print('Processing', filename)
            reader = csv.reader(in_file)

            for row in reader:
                video_id, index, url, type_ = row

                if video_id == 'video_id':
                    continue

                index = int(index)

                doc = db.get(video_id, {})

                if 'flv' not in doc:
                    doc['flv'] = {}

                if index >= 0:
                    doc['flv'][index] = url

                doc['type'] = type_

                db[video_id] = doc

    for filename in VIDEO_TOP:
        with open(os.path.join('..', 'csv', filename), 'r') as in_file:
            print('Processing', filename)
            reader = csv.reader(in_file)

            for row in reader:
                video_id, user, views = row

                if video_id == 'video_id':
                    continue

                views = int(views)

                doc = db.get(video_id, {})

                doc['user'] = user
                doc['views'] = views

                db[video_id] = doc


def get_flv(args):
    db = args.db

    if args.video_id not in db:
        raise Exception('Video ID not in db.')

    flv_dict = db[args.video_id].get('flv')

    if flv_dict is None:
        raise Exception('FLVs not found.')

    for index in sorted(flv_dict.keys()):
        print(flv_dict[index])


def get_flv_list(args):
    db = args.db

    for line in args.video_ids_file:
        video_id = line.strip()

        if video_id not in db:
            raise Exception('Video ID not in db.', video_id)

        doc = db[video_id]
        flv_dict = doc.get('flv')

        if flv_dict is None:
            raise Exception('FLVs not found.', video_id, doc['user'])

        for index in sorted(flv_dict.keys()):
            print(flv_dict[index])


def count_command(args):
    count = 0
    db = args.db

    for video_id in db:
        doc = db[video_id]
        if args.views_limit and doc['views'] < args.views_limit:
            continue

        if args.type == 'videos':
            count += 1
        else:
            count += len(doc.get('flv', ()))

    print(count)


def missing_flv_command(args):
    db = args.db

    for video_id in db:
        doc = db[video_id]
        if args.views_limit and doc['views'] < args.views_limit:
                continue

        if args.user and doc['user'] != args.user:
            continue

        flv_dict = doc.get('flv')

        if not flv_dict:
            print(video_id)


if __name__ == '__main__':
    main()
