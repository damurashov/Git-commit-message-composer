import subprocess
from shlex import split


def command_output(cmd):
	print('>  ' + cmd)
	ret = subprocess.run(split(cmd), stdout=subprocess.PIPE)

	if ret.returncode != 0:
		raise Exception("Command execution error")

	return ret.stdout.decode("unicode_escape").strip()


def command_output_code(cmd):
	print('>  ' + cmd)
	ret = subprocess.run(split(cmd), stdout=subprocess.PIPE)

	return ret.stdout.decode("unicode_escape").strip(), ret.returncode


def command(cmd):
	print('>  ' + cmd)
	ret = subprocess.run(split(cmd))

	if ret.returncode != 0:
		raise Exception(f"Command execution error (returncode - {ret.returncode})")
