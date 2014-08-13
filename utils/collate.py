'''Read the CSVs and collate them into queryable database'''
import argparse
import csv
import json
import os.path
import random
import re
import requests
import shelve


HIGHLIGHTS = [
    'highlights_top.csv',
    'highlights_top_02.csv',
    'highlights_top_03.csv',
    'highlights_top_04.csv'
    ]
FLV_URLS = [
    'highlights_top_flv_01.csv',
    'highlights_top_flv_02-03.csv',
    'disco_top_1000_views_flv.csv',
    'suggestions_19553_flv.csv',
    'suggestions_missed19553_19616_flv.csv',
    'suggestions_flv_19795_and_socialblade.csv',
    ]
VIDEO_TOP = [
    'video_top_discovery.csv',
    'video_discovery_rand200k_suggestions-id19553.csv',
    'video_suggestions-id19616.csv',
    'video_suggestions_missed_from_19553_19616.csv',
    'video_suggestions-id19795.csv'
    ]


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--database', default='twitchy.db')
    subparsers = arg_parser.add_subparsers(title='commands')

    import_parser = subparsers.add_parser('import')
    import_parser.set_defaults(func=import_data)

    get_parser = subparsers.add_parser('get')
    get_parser.add_argument('video_id')
    get_parser.set_defaults(func=get_command)

    get_flv_parser = subparsers.add_parser('getflv')
    get_flv_parser.add_argument('video_id')
    get_flv_parser.set_defaults(func=get_flv)

    get_flv_list_parser = subparsers.add_parser('getflvlist')
    get_flv_list_parser.add_argument('video_ids_file', type=argparse.FileType('r'))
    get_flv_list_parser.set_defaults(func=get_flv_list)

    missing_flv_parser = subparsers.add_parser('missingflv')
    missing_flv_parser.add_argument('--views-min', type=int)
    missing_flv_parser.add_argument('--user')
    missing_flv_parser.set_defaults(func=missing_flv_command)

    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--type', default='videos', choices=['videos', 'flvs'])
    list_parser.add_argument('--views-min', type=int)
    list_parser.add_argument('--views-max', type=int)
    list_parser.add_argument('--flv-min', type=int)
    list_parser.add_argument('--flv-max', type=int)
    list_parser.add_argument('--date-min')
    list_parser.add_argument('--date-max')
    list_parser.add_argument('--count-only', action='store_true')
    list_parser.add_argument('--video-type', choices=['a', 'c'])
    list_parser.add_argument('--by-user-top-video', type=int)

    user_list_group = list_parser.add_mutually_exclusive_group()
    user_list_group.add_argument('--user')
    user_list_group.add_argument('--user-file', type=argparse.FileType('r'))
    user_list_group.add_argument('--not-user-file', type=argparse.FileType('r'))

    list_parser.set_defaults(func=list_command)

    sample_size_parser = subparsers.add_parser('samplesize')
    sample_size_parser.set_defaults(func=sample_size_command)

    missing_user_parser = subparsers.add_parser('missinguser')
    missing_user_parser.set_defaults(func=missing_user_command)

    missing_user_list_group = missing_user_parser.add_mutually_exclusive_group(required=True)
    missing_user_list_group.add_argument('--user')
    missing_user_list_group.add_argument('--user-file', type=argparse.FileType('r'))

    args = arg_parser.parse_args()
    args.db = shelve.open(args.database)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        arg_parser.print_usage()
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
                elif index == -1:
                    doc['no_flv'] = True

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


def get_command(args):
    print(json.dumps(args.db[args.video_id], indent=2))


def get_flv(args):
    db = args.db

    if args.video_id not in db:
        raise Exception('Video ID not in db.')

    if db[args.video_id].get('no_flv'):
        raise Exception('Video explicitly has no FLVs.')

    flv_dict = db[args.video_id].get('flv')

    if flv_dict is None:
        raise Exception('FLVs not in database.')

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
            raise Exception('FLVs not in database.', video_id, doc['user'])

        for index in sorted(flv_dict.keys()):
            print(flv_dict[index])


def missing_flv_command(args):
    db = args.db

    for video_id in db:
        doc = db[video_id]
        if args.views_min and doc['views'] < args.views_min:
            continue

        if args.user and doc['user'].lower() != args.user.lower():
            continue

        flv_dict = doc.get('flv')

        if flv_dict is None:
            print(video_id)


def list_command(args):
    db = args.db
    count = 0
    query_date_min = None
    query_date_max = None

    if args.user_file:
        users_query = frozenset(user.strip().lower() for user in args.user_file)
    else:
        users_query = None

    if args.not_user_file:
        not_users_query = frozenset(user.strip().lower() for user in args.not_user_file)
    else:
        not_users_query = None

    if args.date_min:
        query_date_min = tuple(int(i) for i in args.date_min.split('-'))
    if args.date_max:
        query_date_max = tuple(int(i) for i in args.date_max.split('-'))

    if args.by_user_top_video:
        user_to_video_table = {}

        if args.type != 'videos':
            raise Exception('by-user-top-video only supports videos type')
        if args.count_only:
            raise Exception('Count not supported')

    for video_id in db:
        doc = db[video_id]

        if args.video_type and args.video_type != video_id[0]:
            continue

        if args.views_min and doc['views'] < args.views_min:
            continue

        if args.views_max and doc['views'] > args.views_max:
            continue

        if args.user and doc['user'].lower() != args.user.lower():
            continue

        if users_query and doc['user'].lower() not in users_query:
            continue

        if not_users_query and doc['user'].lower() in not_users_query:
            continue

        flv_doc = doc.get('flv')

        if query_date_min or query_date_max:
            if not flv_doc:
                continue

            url = flv_doc[0]
            match = re.search(r'(\d{2,4})-(\d{1,2})-(\d{1,2})', url)

            if match:
                flv_date = tuple(int(i) for i in (match.group(1), match.group(2), match.group(3)))

                if query_date_min and flv_date < query_date_min:
                    continue

                if query_date_max and flv_date > query_date_max:
                    continue

        if not args.count_only:
            if args.type == 'videos':
                num_flv = None
                if flv_doc:
                    num_flv = len(flv_doc)
                elif doc.get('no_flv'):
                    num_flv = 0

                if args.flv_min is not None and num_flv is not None and num_flv < args.flv_min:
                    continue

                if args.flv_max is not None and num_flv is not None and num_flv > args.flv_max:
                    continue

                if args.by_user_top_video:
                    user = doc['user'].lower()

                    if user not in user_to_video_table:
                        user_to_video_table[user] = []

                    user_to_video_table[user].append((doc['views'], video_id))
                else:
                    print(video_id, doc['user'].lower(), doc['views'], num_flv)

            else:
                if flv_doc:
                    for index in sorted(flv_doc.keys()):
                        print(flv_doc[index])
        else:
            if args.type == 'videos':
                count += 1
            else:
                count += len(doc.get('flv', ()))

    if args.count_only:
        print(count)

    if args.by_user_top_video:
        for user in user_to_video_table:
            video_list = list(reversed(sorted(user_to_video_table[user])))
            for views, video_id in video_list[:args.by_user_top_video]:
                doc = db[video_id]
                flv_doc = doc.get('flv')

                num_flv = None
                if flv_doc:
                    num_flv = len(flv_doc)
                elif doc.get('no_flv'):
                    num_flv = 0

                print(video_id, user, views, num_flv)


def sample_size_command(args):
    db = args.db

    count = 0
    total = 0
    video_ids = random.sample(db.keys(), 5000)

    for video_id in video_ids:
        if count >= 1000:
            break

        doc = db[video_id]
        flv_doc = doc.get('flv')

        if not flv_doc:
            continue

        print('Checking', video_id, 'Count=', count, 'Total=', total,
              'Avg=', int(total / count) if count else 0)

        indexes = list(flv_doc.keys())
        indexes = random.sample(indexes, random.randint(1, len(indexes)))

        for index in indexes:
            url = flv_doc[index]
            print(url)

            try:
                response = requests.head(url)
            except requests.exceptions.RequestException as error:
                print(error)
                continue

            if response.status_code != 200:
                print(response.status_code)
                continue

            total += int(response.headers['Content-Length'])
            count += 1

    print('Count=', count, 'Total=', total, 'Avg=', int(total / count))


def missing_user_command(args):
    db = args.db

    if args.user_file:
        missing_users = set(user.strip().lower() for user in args.user_file)
    else:
        missing_users = set([args.user.lower()])

    for video_id in db:
        doc = db[video_id]

        try:
            missing_users.remove(doc['user'])
        except KeyError:
            pass

    for user in missing_users:
        print(user)


if __name__ == '__main__':
    main()
