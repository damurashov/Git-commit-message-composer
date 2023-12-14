#!/usr/bin/python3

# TODO: option to make it to ask for a change type for each file being added
# into the commit
# TODO: Snippets
# TODO: Handle renames

import argparse
import copy
import dataclasses
import os
import pathlib
import tired.command
import tired.git
import tired.logging
import tired.ui


OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS = False
OPTION_STEM_MODULE_DETAILS = False
OPTION_KEEP_EXTENSION = False
MODULE_CONTENT_STEM_SYMBOL = "*"
COMMIT_MESSAGE_TEMPORARY_FILE_NAME = ".commitmsg"
OPTION_FILE_MEDIATED_INPUT_EDITOR = "vim"
OPTION_USE_COMMON_COMMIT_MESSAGE = True
COMMON_COMMIT_MESSAGE = None
OPTION_USE_COMMON_COMMIT_TYPE = True

# Same as `COMMIT_MESSAGE_TEMPORARY_FILE_NAME`, but with header. Can be considered "garbaged" file
GIT_COMMIT_MESSAGE_WITH_META_FILE_NAME = ".commitmsg_deleteme"


def _git_stash_unstaged_files():
    tired.command.execute("git stash -k")


def _git_unstash():
    tired.logging.info("Restoring staged files")
    # tired.command.execute("git checkout stash@{0} --theirs .")
    tired.command.execute("git restore --source=stash@{0} --worktree .")


def _git_unstage_all_files():
    tired.command.execute("git reset")


def _git_commit(commit_message):
    """
    File-mediated commit to fix the problem with escape sequences
    """
    with open(GIT_COMMIT_MESSAGE_WITH_META_FILE_NAME, 'w') as f:
        f.write(commit_message)

    tired.command.execute(f"git commit --file {GIT_COMMIT_MESSAGE_WITH_META_FILE_NAME}")
    os.remove(GIT_COMMIT_MESSAGE_WITH_META_FILE_NAME)


@dataclasses.dataclass
class File:
    module: str
    full_path: str
    commit_type: str

    def get_representation(self):
        if OPTION_KEEP_EXTENSION:
            representation = pathlib.Path(self.full_path).name
        else:
            representation = pathlib.Path(self.full_path).stem

        return representation


class Staged:

    def __init__(self):
        self._module_map = dict()

    def add_file(self, module, file_path, commit_type):

        file = File(module, file_path, commit_type)

        if module not in self._module_map:
            self._module_map[module] = list()

        self._module_map[module].append(file)

    def get_module_map(self):
        return self._module_map


class FormattingStrategy:
    def format_commit_content(self, commit_content):
        module_representation_map = commit_content.get_module_map()

        commit_message = '['
        commit_types = set()

        # State machine quirks
        is_first = True

        for module_name in module_representation_map.keys():
            if is_first:
                is_first = False
            else:
                commit_message += ' '

            commit_message += module_name
            commit_message += ':'

            if OPTION_STEM_MODULE_DETAILS:
                tired.logging.debug("Stemming module details")
                commit_message += MODULE_CONTENT_STEM_SYMBOL
            else:
                commit_message += ','.join(set(i.get_representation() for i in module_representation_map[module_name]))

            commit_types = commit_types.union({i.commit_type for i in module_representation_map[module_name]})

        commit_message += "] "
        commit_message += ' '.join(commit_types)
        commit_message += ' | '

        return commit_message



class CommitContent:
    def __init__(self) -> None:
        self._modulemap = dict()

    def add_file(self, module_name, file: File):
        if module_name not in self._modulemap:
            self._modulemap[module_name] = list()

        self._modulemap[module_name].append(file)

    def get_module_map(self):
        return self._modulemap

    def is_empty(self):
        return len(self._modulemap.values()) == 0

class Execution:
    """
    Executes sequential commits
    """

    def __init__(self, staged: Staged):
        # All staged files
        self._module_map = staged.get_module_map()
        self._commit_queue = list()
        self._formatting_strategy = FormattingStrategy()

    def _add_commit(self, commit_content: CommitContent):
        self._commit_queue.append(copy.copy(commit_content))

    def execute_commit(self, commit_content: CommitContent):
        if commit_content.is_empty():
            tired.logging.warning("Empty commit, skipping")

            return

        commit_message = self._formatting_strategy.format_commit_content(commit_content)

        for file_paths in commit_content.get_module_map().values():
            for file_path in file_paths:
                tired.logging.debug(f"Adding file {file_path.full_path}")
                tired.command.execute(f"git add \"{file_path.full_path}\"")

        if OPTION_USE_COMMON_COMMIT_MESSAGE:
            # Commit through use of intermediate garbaged file to improve reliability
            _git_commit(f"{commit_message}{COMMON_COMMIT_MESSAGE}")
        else:
            tired.ui.get_input_using_temporary_file(GIT_COMMIT_MESSAGE_WITH_META_FILE_NAME, OPTION_FILE_MEDIATED_INPUT_EDITOR, commit_message, True)
            tired.command.execute(f"git commit --file \"{GIT_COMMIT_MESSAGE_WITH_META_FILE_NAME}\"")

    def _build_commit_queue(self):
        tired.logging.info("Building commit queue")
        commit_content = CommitContent()
        should_commit_after_file = OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS and not OPTION_STEM_MODULE_DETAILS
        should_commit_after_module = OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS and OPTION_STEM_MODULE_DETAILS

        for module_name in self._module_map.keys():

            for file in self._module_map[module_name]:
                commit_content.add_file(module_name, file)

                if should_commit_after_file:
                    self._add_commit(commit_content)
                    commit_content = CommitContent()

            if should_commit_after_module:
                self._add_commit(commit_content)
                commit_content = CommitContent()

        self._add_commit(commit_content)

    def _execute_commit_queue(self):
        tired.logging.info("Executing commit queue")

        for commit_content in self._commit_queue:
            self.execute_commit(commit_content)

    def run(self):
        self._build_commit_queue()
        self._execute_commit_queue()


def file_path_decompose(file_path: str):
    return pathlib.Path(file_path).parts


def _cli_get_file_module(file_path: str) -> str:
    options = pathlib.Path(file_path).parts

    # File name itself is not needed
    options = options[:-1]

    if len(options) == 0:
        return ""

    option_id = tired.ui.select(options, file_path)
    selected_option = options[option_id]

    return selected_option


def _cli_get_commit_type(file_name="") -> str:
    commit_types = [
        "[b] Bug",  # Fixed some bug
        "[i] Impl",  # Implementation (added new feature)
        "[e] Enh",  # Enhancement / optimization (changed / optimized old feature)
        "[r] Ref",  # Made refactoring
        "[u] Build",  # Build system / project management tweaks
        "[d] Doc",  # Updated documentation
    ]
    selected_id = tired.ui.select(commit_types, f"Select commit type {file_name}")
    commit_type = commit_types[selected_id][4:]

    return commit_type


def _parse_arguments():
    global OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS
    global OPTION_STEM_MODULE_DETAILS
    global OPTION_KEEP_EXTENSION
    global OPTION_USE_COMMON_COMMIT_MESSAGE
    global OPTION_USE_COMMON_COMMIT_TYPE

    parser = argparse.ArgumentParser()
    parser.add_argument("--sep", action="store_true", help="Push each dir:module pair as a separate commit under the same name")
    parser.add_argument("--stem", action="store_true", help="If true, module components will not be comma-enumerated, but replaced w/ * symbol")
    parser.add_argument("--ext", action="store_true", help="Keep file extension")
    parser.add_argument("--mes", action="store_false", help="Use separate commit message for each file")
    parser.add_argument("--typ", action="store_false", help="Use individual commit type for each file")
    p = parser.parse_args()

    OPTION_SEPARATE_MODULE_FILE_PAIRS_BETWEEN_COMMITS = p.sep
    OPTION_STEM_MODULE_DETAILS = p.stem
    OPTION_KEEP_EXTENSION = p.ext
    OPTION_USE_COMMON_COMMIT_MESSAGE = p.mes
    OPTION_USE_COMMON_COMMIT_TYPE = p.typ

    return p


def main():
    global OPTION_USE_COMMON_COMMIT_MESSAGE
    global COMMON_COMMIT_MESSAGE
    global OPTION_USE_COMMON_COMMIT_TYPE
    # Only apply changes that are staged (useful, since we operate with file names)
    _parse_arguments()
    _git_stash_unstaged_files()
    staged = Staged()

    try:
        # Change PWD to git root directory. This is the simplest, and the most reliable way to handle relative paths
        os.chdir(tired.git.get_git_directory_from_nested_context())

        # Specify commit type for all messages, if appropriate
        if OPTION_USE_COMMON_COMMIT_TYPE:
            commit_type = _cli_get_commit_type()

        # Specify commit message for each file
        if OPTION_USE_COMMON_COMMIT_MESSAGE:
            COMMON_COMMIT_MESSAGE = tired.ui.get_input_using_temporary_file(COMMIT_MESSAGE_TEMPORARY_FILE_NAME, OPTION_FILE_MEDIATED_INPUT_EDITOR, "Erase this, and type in your commit message", False)

        tired.logging.debug(f"Staged files: {list(tired.git.get_staged_file_paths())}")

        for staged_file_path in tired.git.get_staged_file_paths(True):
            if not OPTION_USE_COMMON_COMMIT_TYPE:
                commit_type = _cli_get_commit_type(staged_file_path)

            module = _cli_get_file_module(staged_file_path)
            staged.add_file(module, staged_file_path, commit_type)

        # Unstage files. Each file will be staged separately
        _git_unstage_all_files()

        execution = Execution(staged)
        execution.run()
    finally:
        _git_unstash()


if __name__ == "__main__":
    main()
