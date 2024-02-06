#!/usr/bin/env python3

import sys
import json

if len(sys.argv) < 2:
   print(f"usage: {sys.argv[0]} CONFIG.JSON", file=sys.stderr)
   sys.exit(1)

with open(sys.argv[1]) as f:
   config = json.load(f)

curr_convo = []
skip_convo = False

for _line in sys.stdin:
   line = _line.rstrip()
   line_words = line.split(" ")

   if line == "": # signals end of convo
      if not skip_convo and len(curr_convo) != 0:
         print('\n'.join(curr_convo) + "\n")
      skip_convo = False
      curr_convo = []
   elif not skip_convo:
      curr_convo.append(line)
      if line_words[0] == "TERM:":
         term = " ".join(line_words[1:])
         if term not in config['words'] or term in config['exclude']:
            skip_convo = True
