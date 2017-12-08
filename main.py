import sys
import argparse

from interpreter import FtpInterpreter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='Use this to see debug output from the '
                             'FTP client.')
    args = parser.parse_args(sys.argv[1:])

    ftps_interpreter = FtpInterpreter(debug=args.debug)
    ftps_interpreter.cmdloop()


if __name__ == '__main__':
    main()
