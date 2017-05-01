import argparse
import unittest

def main():
    args = parse_args()

def parse_args():
    parser = argparse.ArgumentParser()
    parser = create_parser(parser)
    args = parser.parse_args()
    return args

def create_parser(parser):
    parser.add_argument(metavar='client-ip',
        dest='response_ip')
    parser.add_argument(metavar='client-port',
        dest='response_port', type=int)
    parser.add_argument('-t', '--test', action='store_true')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--multiple',
        help="Specify filename")
    group.add_argument('-s', '--single',
        help="Specify IP and port", nargs=3)
    return parser

if __name__ == "__main__":
    main()
