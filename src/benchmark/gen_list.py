import sys
import os
import argparse

### 1. argument: path to folder
parser = argparse.ArgumentParser(description='Generate testset list.')
parser.add_argument('path', type=str , help='path to testset')
parser.add_argument('output', type=str , help='path to output file')

args = parser.parse_args()

### Recursively search for graphml files
graphml_files = []
for root, dirs, files in os.walk(args.path):
    for file in files:
        if file.endswith(".graphml"):
            graphml_files.append(os.path.join(root, file))

### Write graphml files to output file
with open(args.output, 'w') as f:
    for file in graphml_files:
        f.write(file + '\n')