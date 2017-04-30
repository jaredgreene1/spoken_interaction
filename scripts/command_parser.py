import argparse
import unittest

# Here we have a bunch of examples for parsers


# Parser stuff from Networks Programming Assignment 2
class ArgsException(Exception):
    pass

def main():
    parse_command_line()

def parse_command_line():
    parser = instantiate_parser()
    args = parser.parse_args()
    return args

def instantiate_parser():
    parser = argparse.ArgumentParser()
    return create_parser(parser)

def create_parser(parser):
    parser.add_argument(metavar="self-port", dest='self_port', type=int)
    parser.add_argument(metavar="peer-port", dest='peer_port', type=int)
    parser.add_argument(metavar="window-size", dest='window_size', type=int)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--deterministic", help="Drop deterministically",
        type=int)
    group.add_argument("-p", "--probabilistic", help="Drop probabilistically",
        type=float)
    parser.add_argument("-t", "--test", help="Test this node",
        action='store_true')
    return parser

class ErrorRaisingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        #print(message)
        raise ValueError(message)  # reraise an error

class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser(ErrorRaisingArgumentParser())

    def test_invalid_ports(self):
        args = "asdf asdf 3 -d 14"
        with self.assertRaises(ValueError) as cm:
            self.parser.parse_args(args)
        # print('msg:', cm.exception)
        self.assertIn('invalid int value', str(cm.exception))


# A parser from Networks Programming Assignment 1

# def create_parser():
#     parser = argparse.ArgumentParser()
#     group = parser.add_mutually_exclusive_group(required=True)
#     group.add_argument("-s", "--server", help="Start server", type=int)
#     group.add_argument("-c", "--client", help="Start client",
#         nargs=4,
#         action="store")
#     return parser


if __name__ == "__main__":
    unittest.main()