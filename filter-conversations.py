#!/usr/bin/env python3

import sys
import json
import re

if len(sys.argv) < 2:
   print(f"usage: {sys.argv[0]} CONFIG.JSON", file=sys.stderr)
   sys.exit(1)

with open(sys.argv[1]) as f:
   config = json.load(f)

exclude_set = set(config['exclude']) if config['exclude'] is not None else None

curr_convo = []
skip_convo = False

for _line in sys.stdin:
   line = _line.rstrip()

   if line == "": # signals end of convo
      if not skip_convo and len(curr_convo) != 0:
         print('\n'.join(curr_convo) + "\n")
      skip_convo = False
      curr_convo = []
   elif not skip_convo:
      curr_convo.append(line)
      if line.startswith("TERM: "):
         term = line[line.index(" ")+1:]
         if term not in config['words']:
            skip_convo = True
      else:
         line_words = re.split(r'[^a-zA-Z0-9]+', line)
         if exclude_set.intersection(line_words):
            skip_convo = True
