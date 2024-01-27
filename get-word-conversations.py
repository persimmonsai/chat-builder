#!/usr/bin/env python3

from subprocess import Popen, PIPE, DEVNULL

import sys
import re
import os
import json

if len(sys.argv) < 2:
	print(f"usage: {sys.argv[0]} CONFIG.JSON", file=sys.stderr)
	sys.exit(1)

with open(sys.argv[1]) as f:
	config = json.load(f)


tempdir = "/dev/shm" if os.path.isdir('/dev/shm') else "/tmp"

outfile = tempdir + "/tmp-" + config['name'] + "-conv.txt"

exwords_re = '(' + '|'.join(config['exclude']) + ')'

words_count = {}

for word in config['words']:
	words_count[word] = 0

if os.path.exists(outfile):
	with open(outfile) as f:
		for line in f:
			line = line.rstrip()
			conv_words = re.split(r'[^a-zA-Z0-9]', line)
			for word in conv_words:
				if word in words_count: words_count[word] += 1

prompt = '\n'.join(config['prompt_lines'])

model = os.environ.get('MODEL')
if model is None and 'model' in config:
	model = config['model']
if model is None:
	model = 'llama-2-7b.Q4_K_M.gguf'

for word in config['words']:
	if words_count[word] > 0:
		print(f"skipping {word}", file=sys.stderr)
		continue
	print(f"processing {word}", file=sys.stderr)
	p = Popen(["./main", "--log-disable", "--escape", "-m", model, "-p",  prompt.format(word = word)], stdout=PIPE, stderr=DEVNULL, encoding="utf-8")

	lines = []

	n = 0	
	for line in p.stdout:
		line = line.rstrip()

		if ( n := n + 1) == 1:
			continue

		if n == 2 and line.find(word) < 0:
			print(f"missing {word} in line {line}", file=sys.stderr)
			lines = []
			break

		if line.find(':') < 0:
			print(f"ending early {word} with: {line}", file=sys.stderr)
			lines = []
			break

		if re.search(exwords_re, line, re.IGNORECASE):
			print(exwords_re)
			print(line)
			print(f"has excluded word {word}", file=sys.stderr)
			lines = []
			break

		m = re.match(r'(.*): Teacher, ([a-zA-Z])(.*)', line)
		if m:
			line = m.group(1) + ': ' + m.group(2).upper() + m.group(3)

		m = re.match(r'(.*): (?:Excuse me,? )?(?:Teacher|Professor,Miss|Sir|Mister|Mr|Mrs|Ms)\.?(?: *[^ ,]*), ([a-zA-Z])(.*)', line)
		if m:
			line = m.group(1) + ': ' + m.group(2).upper() + m.group(3)

		line = re.sub(r': "([^"]*)"$', r': \1', line)

		lines.append(line)

		words_count[word] += 1
		conv_words = re.split(r'[^a-zA-Z0-9]', line)
		for w in conv_words:
			if w in words_count: words_count[w] += 1

	if len(lines) > 0:
		with open(outfile, "a") as f:
			for line in lines:
				print(line, file=sys.stderr)
				print(line, file=f)
			print('', file=f)


with open(outfile) as f:
	for line in f:
		print(line, end='')
os.unlink(outfile)

print("")
