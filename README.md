# PathPicker

[![Build Status](https://travis-ci.org/facebook/PathPicker.svg?branch=master)](https://travis-ci.org/facebook/PathPicker)

Facebook PathPicker is a simple command line tool that solves the perpetual
problem of selecting files out of bash output. PathPicker will:
* Parse all incoming lines for entries that look like files
* Present the piped input in a convenient selector UI
* Allow you to either:
    * Edit the selected files in your favorite `$EDITOR`
    * Execute an arbitrary command with them

It is easiest to understand by watching a simple demo:
<a href="https://asciinema.org/a/19519" target="_blank"><img src="https://asciinema.org/a/19519.png" width="597"/></a>

## Examples
After installing PathPicker, using it is as easy as piping into `fpp`. It takes
a wide variety of input -- try it with all the options below:

* `git status | fpp`
* `hg status | fpp`
* `git grep "FooBar" | fpp`
* `grep -r "FooBar" . | fpp`
* `git diff HEAD~1 --stat | fpp`
* `find . -iname "*.js" | fpp`
* `arc inlines | fpp`

and anything else you can dream up!

## Requirements
PathPicker requires Python >2.6 or >3.0.

### Supported Shells:

* Bash is fully supported and works the best.
* ZSH is supported as well but won't have a few features like alias expansion in command line mode.
* csh/fish/rc are supported in the latest version, but might have quirks or issues in older versions of PathPicker. Note however if your default shell and current shell is not in the same family (bash/zsh... v.s. fish/rc), you need to manually export environment variable `$SHELL` to your current shell.

## Installing PathPicker

### Homebrew

Installing PathPicker is easiest with [Homebrew for mac](http://brew.sh/):

* `brew update` (to pull down the recipe since it is new)
* `brew install fpp`

### Linux

On debian systems, installation can be done by installing the debian package from [here](https://github.com/facebook/PathPicker/releases/latest). To build the package locally, run these steps:

```
$ git clone https://github.com/facebook/PathPicker.git
$ cd debian
$ ./package.sh 
$ ls ../fpp_0.7.2_noarch.deb
```

On Arch Linux, PathPicker can be installed from Arch User Repository (AUR).
[the AUR fpp-git package](https://aur.archlinux.org/packages/fpp-git/).

If you are on another system, or prefer manual installation, please
follow the instructions given below.

### Manual Installation

However if you're on a system without Homebrew, it's still quite easy to install
PathPicker since it's essentially just a bash script that calls some Python. These
steps more-or-less outline the process:

* `cd /usr/local/ # or wherever you install apps`
* `git clone https://github.com/facebook/PathPicker.git`
* `cd PathPicker/`

Here we make a symbolic link from the bash script in the repo
to `/usr/local/bin/` which is assumed to be in the current
`$PATH`

* `ln -s "$(pwd)/fpp" /usr/local/bin/fpp`
* `fpp --help # should work!`

### Add-ons

For tmux users, you can additionally install `tmux-fpp` which adds a key combination to run PathPicker on the last received `stdout`. It makes jumping into file selection mode even easier -- [check it out here](https://github.com/tmux-plugins/tmux-fpp).


## Advanced Functionality

As mentioned above, PathPicker allows you to also execute arbitrary commands with the specified files.
Here is an example showing a `git checkout` command executed against the selected files:
<a href="https://asciinema.org/a/19520" target="_blank"><img src="https://asciinema.org/a/19520.png" width="597"/></a>

The selected files are appended to the command prefix to form the final command. If you need the files
in the middle of your command, you can use the `$F` token instead, like:

`cat $F | wc -l`

Another important note is that PathPicker by default only selects files that exist on the filesystem. If you
want to skip this (perhaps to selected deleted files in `git status`), just run PathPicker with the `--no-file-checks` (or `-nfc` for short) flag.

## How PathPicker works
PathPicker is a combination of a bash script and some small Python modules.
It essentially has three steps:

* First the bash script redirects all standard out in to a python module that
parses and extracts out filename candidates. These candiates are extracted with a series of
regular expressions, since the input to PathPicker can be any stdout from another program. Rather
than make specialized parsers for each program, we treat everything as noisy input and select candidates via
regexes. To limit the number of calls to the filesystem (to check existence), we are fairly restrictive on the
candidates we extract.

This has the downside that files that are single words with no extension (like `test`) that are not prepended by
a directory will fail to match. This is a known limitation to PathPicker, and means that it will sometimes fail to find valid files in the input.

* Next, a selector UI built with `curses` is presented to the user. Here you can select a few files to edit or input a command
to execute.
* Lastly, the python script outputs a command to a bash file that is later
executed by the original bash script.

It's not the most elegant architecture in the world but (in our opinion) provides a lot of utility.

## Documentation & Configuration

For all documentation and configuration options, see the output of `fpp --help`.

## Join the PathPicker community
See the CONTRIBUTING file for how to help out.

## License
PathPicker is BSD-licensed. We also provide an additional patent grant.
