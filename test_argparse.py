import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-H")
args = parser.parse_args()
print(args.echo)