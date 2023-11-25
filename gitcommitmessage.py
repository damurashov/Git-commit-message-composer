#!/usr/bin/python3

# TODO: option to make it to ask for a change type for each file being added
# into the commit
# TODO: Snippets
# TODO: Handle renames

import argparse
import dataclasses
import pathlib
import tired.command
import tired.git
import tired.ui


OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS = False
OPTION_STEM_MODULE_DETAILS = False
OPTION_KEEP_EXTENSION = False
MODULE_CONTENT_STEM_SYMBOL = "*"
COMMIT_MESSAGE_TEMPORARY_FILE_NAME = ".commitmsg_deleteme"
OPTION_FILE_MEDIATED_INPUT_EDITOR = "vim"


def _git_stash_unstaged_files():
    tired.command.execute("git stash -k -u")


def _git_unstash():
    tired.command.execute("git stash pop")


@dataclasses.dataclass
class File:
    full_path: str
    module: str
    representation: str
    commit_type: str


class Staged:

    def __init__(self):
        self._module_map = dict()

    def add_file(self, module, file_path, commit_type):
        if OPTION_KEEP_EXTENSION:
            representation = pathlib.Path(file_path).name
        else:
            representation = pathlib.Path(file_path).stem

        file = File(file_path, module, representation)

        if module not in self._module_map:
            self._module_map[module] = list()

        self._module_map[module].append(file)

    def get_module_map(self):
        return self._module_map


class FormattingStrategy:
    pass


class Execution:
    """
    Executes sequential commits
    """

    def __init__(self, staged: Staged):
        self._module_map = staged.get_module_map()

    @staticmethod
    def format_commit_message(module_representation_map):
        commit_message = '['
        is_first = True
        commit_types = set()

        for module_name in module_representation_map.keys():
            if is_first:
                is_first = False
            else:
                commit_message += ' '

            commit_message += module_name
            commit_message += ':'
            commit_message += ','.join(module_representation_map[module_name].representation)
            commit_types = commit_types.union(module_representation_map[module_name].commit_type)

        commit_message += "] "
        commit_message += ' '.join(commit_types)
        commit_message += ' | '

    def execute_commit(self, module_representation_map: dict):
        commit_message = self.format_commit_message(module_representation_map)
        tired.ui.get_input_using_temporary_file(COMMIT_MESSAGE_TEMPORARY_FILE_NAME, OPTION_FILE_MEDIATED_INPUT_EDITOR, commit_message)

        for v in module_representation_map.values():
            tired.command.execute(f"git add \"{v.full_path}\"")

        tired.command.execute(f"git commit --file \"{COMMIT_MESSAGE_TEMPORARY_FILE_NAME}\"")

    def run(self):
        module_representation_map = dict()

        for module_name in self._module_map.keys():
            module_name[module_representation_map] = set()

            if OPTION_STEM_MODULE_DETAILS:
                module_representation_map[module_name] = MODULE_CONTENT_STEM_SYMBOL

                if OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS:
                    self.execute_commit(module_representation_map)
                    module_representation_map = dict()
            else:
                for file in self._module_map[module_name]:
                    module_representation_map[module_name] = module_representation_map[module_name].union({file})

                if OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS:
                    self.execute_commit(module_representation_map)
                    module_representation_map = dict()


def file_path_decompose(file_path: str):
    return pathlib.Path(file_path).parts


def _cli_get_file_module(file_path: str) -> str:
    options = pathlib.Path(file_path).parts

    if len(options) == 0:
        return ""

    option_id = tired.ui.select(options, file_path)
    selected_option = options[option_id]

    return selected_option


def _cli_get_commit_type() -> str
    commit_types = [
        "[b] Bug",  # Fixed some bug
        "[i] Impl"  # Implementation (added new feature)
        "[e] Enh",  # Enhancement / optimization (changed / optimized old feature)
        "[r] Ref"  # Made refactoring
        "[u] Build",  # Build system / project management tweaks
        "[d] Doc",  # Updated documentation
    ]
    selected_id = tired.ui.select(commit_types, "Select commit type")
    commit_type = commit_types[selected_id][4:]

    return commit_type


def _get_args():
    global OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS
    global OPTION_STEM_MODULE_DETAILS

    parser = argparse.ArgumentParser()
    parser.add_argument("--sep", action="store_true", help="Push each dir:module pair as a separate commit under the same name")
    parser.add_argument("--stem", action="store_true", help="If true, module components will not be comma-enumerated"
        ", but replaced w/ * symbol, if there is more than 1 element in each module")
    parser.add_argument("--ext", action="store_true", help="Keep file extension")
    p = parser.parse_args()

    OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS = p.sep
    OPTION_STEM_MODULE_DETAILS = p.stem
    OPTION_KEEP_EXTENSION = p.ext

    return p


def main():
    # Only apply changes that are staged (useful, since we operate with file names)
    _git_stash_unstaged_files()
    staged = Staged()

    try:
        commit_type = _cli_get_commit_type()

        for staged_file_path in tired.git.get_staged_file_names():
            module = _cli_get_file_module(staged_file_path)
            staged.add_file(module, staged_file_path)

        execution = Execution(staged)
        execution.run()
    finally:
        _git_unstash()


if __name__ == "__main__":
    main()
