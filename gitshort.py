from command import command_output, command_output_code


def get_staged():
	lst = command_output("git diff --name-only --staged")
	lst = lst.split('\n')
	lst = [l.strip() for l in lst]
	return lst

def get_current_branch():
	lst = command_output("git rev-parse --abbrev-ref HEAD")

	return lst.strip()

def get_branches_local():
	cmd = "git for-each-ref --format='%(refname:short)' refs/heads/"

	out = command_output(cmd)
	out = out.split('\n')
	out = [o.strip() for o in out]
	out = [str(o) for o in out]

	return out

def get_branches_remote():
	"""
	Get both local and remote branches
	"""

	cmd = "git branch -r"

	out = command_output(cmd)
	out = out.split('\n')
	out = [o.strip() for o in out]
	out = [str(o) for o in out]

	return out

def get_branches_all():
	return get_branches_local() + get_branches_remote()

def get_tags():
	cmd = "git tag -l"

	out = command_output(cmd)
	out = out.split('\n')
	out = [o.strip() for o in out]
	out = [str(o) for o in out]

	return out

def get_commit_message(commit):
	return command_output(f"git log --format=%B -n 1 {commit}")

def git_is_ancestor(h1, h2) -> bool:
	"""
	Returns True, if (h1, h2) form (ancestor, descendant) pair
	"""
	command = f'git merge-base --is-ancestor {h1} {h2}'
	_, ret = command_output_code(command)
	return ret == 0
