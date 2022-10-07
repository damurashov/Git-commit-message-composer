#!/usr/bin/python3

# TODO: option to make it to ask for a change type for each file being added
# into the commit
# TODO: Snippets

from simple_term_menu import TerminalMenu
from command import command
from os.path import split
import os
from gitshort import get_staged
import argparse

COMMITMSG = ".commitmsg"
EDITOR = "vim"


def splitext(f):
    hidden = (f[0] == '.')
    res = list(f.split('.'))
    res = list(map(str.strip, res))

    if hidden:
        res = ["%s%s" % (".", res[1])] + res[2:]

    return res


def get_units():
    staged = get_staged()
    units = set([splitext(s)[0] for s in staged])  # Echo.cpp, Echo.hpp -> Echo
    print(units)
    return units

def get_modulemap(unit, modulemap=dict()):
    unit_initial = unit
    basename, unit = split(unit)
    basename = basename.split('/')
    basename = list(reversed(basename))

    if len(basename) > 1:
        print(f"Unit {unit}. Select module")
        module = basename[TerminalMenu(basename).show()]
    elif len(basename) == 1:
        module = basename[0]
    else:
        module = ""

    if module not in modulemap.keys():
        modulemap[module] = set()

    modulemap[module] = set.union(modulemap[module], {unit_initial})

    return modulemap

def get_commit_type():
    print("Select commit type...")
    types = ["[i]Impl", "[e]Enh", "[b]Bug", "[c]Cascade", "[o]Opt", "[r]Ref", "[u]Build"]
    return types[TerminalMenu(types).show()][3:]

def fmt(modulemap, commit_type, stem=False):
    modstrings = []

    for k, v in modulemap.items():
        if len(v) > 1 and stem:
            vals = "*"
        else:
            vals = ','.join(list(map(lambda p: split(p)[1], v)))

        modstrings.append(k + ":" + vals)

    return '[' + ' '.join(modstrings) + '] ' + commit_type + " | "

def command_commit(prefix):
    with open(COMMITMSG, 'w') as f:
        f.write(prefix)
    command("vim " + COMMITMSG)
    command("git commit --file " + COMMITMSG)


def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sep", action="store_true", help="Push each dir:module pair as a separate commit under the same name")
    parser.add_argument("--stem", action="store_true", help="If true, module components will not be comma-enumerated"
        ", but replaced w/ * symbol, if there is more than 1 element in each module")
    p = parser.parse_args()

    return p


def get_commit_message():
    temp = ".tempmsg"

    with open(temp, 'w') as f:
        pass

    os.system("%s %s" % (EDITOR, temp))

    with open(temp, 'r') as f:
        res = f.read()

    assert len(res.strip()) > 0
    os.remove(temp)

    return res


def main():
    args = _get_args()

    try:
        modulemap = dict()
        units = get_units()

        for unit in units:
            modulemap = get_modulemap(unit, modulemap)
            print(modulemap)

        commit_type = get_commit_type()

        if not args.sep:
            formatted = fmt(modulemap, commit_type, args.stem)
            command_commit(formatted)
        else:
            command("git reset")
            commit_msg = get_commit_message()

            for k, vs in modulemap.items():
                for v in vs:
                    print("adding %s" % (str(v)))
                    formatted = fmt({k: {v}}, commit_type, args.stem)
                    command("git add %s.*" % v)
                    command("git commit -m \'%s%s\'" % (formatted, commit_msg))


    except Exception as e:
        print(e)
    finally:
        command("rm -f " + COMMITMSG)


if __name__ == "__main__":
    main()
