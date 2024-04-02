from generate import generate_config
from utils.wrapper import Config
from utils.io import *
import argparse


def main(args):
    if args.base is not None:
        config = load_config(args.base)
    else:
        config = { 'triggers': [], 'overrides': {}, 'researchIgnore': [] }

    generate_config(Config(config))

    if args.print:
        print(dump_config(config, args.pretty))

    if args.out is not None:
        save_config(config, args.out, args.pretty)


def parse_args():
    parser = argparse.ArgumentParser(description='Generate the config for the Evolve script')

    parser.add_argument('--base', type=str, help='Path to the base (default) config.json. Any changes will be applied on top of the values that are in this config.')
    parser.add_argument('--out', type=str, help='Path to save the generated config.json to.')
    parser.add_argument('--print', action='store_true', default=False, help='Print the result to the console.')
    parser.add_argument('--pretty', action='store_true', default=False, help='Add indentation and newlines to the resulting json.')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
