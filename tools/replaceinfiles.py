#!/usr/bin/python3

import re
import subprocess
from shlex import split
from sys import argv

def listout(l: list):
	print('>', ' '.join(l))

def command_output(commands, verbose=True):
	"""
	:param commands: commands to execute. The commands are executed in a sequential manner, i.e. piped
	:return: console output, string
	"""
	commands = [split(c) for c in commands]
	procs = []

	listout(commands[0])
	p = subprocess.Popen(commands[0], stdout=subprocess.PIPE)

	for c in commands[1:]:
		print("  ↑ piped into ↓")
		listout(c)
		p = subprocess.Popen(c, stdout=subprocess.PIPE, stdin=p.stdout)

	p.wait()
	out = p.stdout.read()

	if verbose and len(out):
		print(out.decode("unicode_escape"))

	return out, p.returncode


def ex():
	if argv[1].find('-h') != -1 or len(argv) != 4:
		print(f"Syntax: FILE_GLOB_EXTENSION   REGEX_RENAME_FROM   REGEX_RENAME_TO")
	else:
		fileglob = argv[1]
		re_from = argv[2]
		re_to = argv[3]

		command = f'find . -iname \'{fileglob}\' -type f | xargs -n1 sed -i \'s/{re_from}/{re_to}/g\''
		command = command.split(' | ')
		print(command)
		command_output(command, False)


if __name__ == "__main__":
	ex()


