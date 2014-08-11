'''SHA1 hash the item names because the rsync destination wasn't configured
correctly'''
import argparse
import hashlib


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input', type=argparse.FileType('r'))

    args = arg_parser.parse_args()

    for line in args.input:
        name = line.strip()
        digest = hashlib.sha1(name.encode('ascii')).hexdigest()
        print(name, digest)


if __name__ == '__main__':
    main()
