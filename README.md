# GiCo 🤌

Git commit composer, or GiCo, is your ultimate answer to "keep your commits as
small as possible". Once you have staged whatever the mess you have accumulated
so far, run `gico`, and it will make you a neat and comprehensive commit
history.

```
git add <your files>
gico --help
gico
```

GiCo provides you with a zero-friction way to do this

```
> git log --all --decorate --oneline

e01f0cc (HEAD -> master) [bb:b] Impl | Similar message for each commit
358fcb1 [aa:a] Ref | Similar message for each commit, but different commit types
8c73fb5 [aa:a] Impl | Similar message for each commit, but different commit types
af31232 [aa:* bb:*] Impl | Stemmed representation
7f2c4bd [:b] Ref | hi
39f881c [:a] Impl | echo
4063a8e (tag: base) [:README] Impl | Yo
c9bd056 [:README] Impl |
```

... instead of this

```
> git log --all --decorate --oneline

e01f0cc (HEAD -> master) Minor changes (9999 files)
c9bd056 Initial message. Thank God, it finally works!!11
```

# Requirements

- Vim (for file-mediated prompt);
- Linux (for complete and vibrant life);

# Installation

## From Github

```
pip install git+https://github.com/damurashov/Git-commit-message-composer.git@main -U --force
```

## From PyPi

~~It might actually be published on PyPi. At the appropriate juncture. In the fullness of time.~~

```
python3 -m pip install gico -U --force
```

### I have this fancy new python 3.11 with "walruses", and stuff

```
python3 -m pip install gico -U --force --break-system-packages
```

# Acknowledgements

- Simple-term-menu, https://github.com/IngoMeyer441/simple-term-menu
- Shlex, https://docs.python.org/3/library/shlex.html
- Tired https://pypi.org/project/tired/. This library is one big boilerplate, and its good!

# Known limitations / issues

- It does not handle renames well (yet);

# Announced features

- Cache previous selection for file-module associations;
- Cache messages for further reuse;
