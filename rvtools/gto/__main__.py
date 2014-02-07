import argparse
import sys

from .core import iter_tokens, filter_tokens, GTO


parser = argparse.ArgumentParser()
parser.add_argument('-l', '--lex', action='store_true')
parser.add_argument('-f', '--filter', action='store_true')
parser.add_argument('input', nargs='?')
args = parser.parse_args()

input_fh = open(args.input) if args.input else sys.stdin

if args.lex:
    tokens = iter_tokens(input_fh)
    if args.filter:
        tokens = filter_tokens(tokens)
    for token in tokens:
        print token

else:
    gto = GTO()
    gto.parse(input_fh)
    print gto.dumps()

