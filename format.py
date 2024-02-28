#!/usr/bin/env python3

import sys
import re

# CHANGE THESE AS NEEDED:
# searches for the dict keys, removing lines that don't start with it.
# then swaps keys for their value (symbol)
terms_dict = {
	"STUDENT": "=",
	"TEACHER": "#",
	"TERM": "~",
}

if len(sys.argv) < 2:
	print(f"usage: {sys.argv[0]} conv.txt", file=sys.stderr)
	sys.exit(1)

with open(sys.argv[1]) as f:
	conversations = f.read()

# remove lines that aren't key terms
re_terms_pat = "^(" + ".*\\n|".join(terms_dict.keys()) + ".*\\n|[\\n\\r])"
conversations = "".join(re.findall(re_terms_pat, conversations, re.MULTILINE))

# remove trailing student lines
conversations = re.sub(r"^STUDENT.*[\r\n][\r\n]", "\n", conversations, flags=re.MULTILINE)

# replace all terms with their symbols
for term in terms_dict.keys():
	conversations = conversations.replace(term + ":", terms_dict[term])

# output!
print(conversations)
