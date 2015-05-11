# PathPicker
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
PathPicker should work with most Bash environments and requires Python >2.6
and <3.0.

ZSH is supported as well but won't have a few features like alias expansion
in command line mode.

## Installing PathPicker


### Homebrew

Installing PathPicker is easiest with [Homebrew for mac](http://brew.sh/):

* `brew update` (to pull down the recipe since it is new)
* `brew install fpp`

### Manual Installation

However if you're on a system without Homebrew, it's still quite easy to install
PathPicker since it's essentially just a bash script that calls some Python. These
steps more-or-less outline the process:

* `cd /usr/local/ # or wherever you install apps`
* `git clone git@github.com:facebook/PathPicker.git`
* `cd PathPicker/`

Here we make a symbolic link from the bash script in the repo
to `/usr/local/bin/` which is assumed to be in the current
`$PATH`

* `ln -s ./fpp /usr/local/bin/fpp`
* `fpp --help # should work!`

### Add-ons

For tmux users, you can additionally install `tmux-fpp` which adds a key combination to run PathPicker on the last received `stdout`. It makes jumping into file selection mode even easier -- [check it out here](https://github.com/jbnicolai/tmux-fpp).


## Advanced Functionality

As mentioned above, PathPicker allows you to also execute arbitrary commands with the specified files.
Here is an example showing a `git checkout` command executed against the selected files:
<a href="https://asciinema.org/a/19520" target="_blank"><img src="https://asciinema.org/a/19520.png" width="597"/></a>

The selected files are appended to the command prefix to form the final command. If you need the files
in the middle of your command, you can use the `$F` token instead, like:

`cat $F | wc -l`

## How PathPicker works
PathPicker is a combination of a bash script and some small Python modules.
It essentially has three steps:

* First in the bash script, it redirects all standardout in to a python module that
parses and extracts out the filenames. This data is saved in a temporary file
and the python script exits.
* Next, the bash script switches to terminal input mode and
another python module reads out the saved entries and presents them in a
selector UI built with `curses`. The user either selects a few files to edit or inputs a command
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
