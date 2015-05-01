# PathPicker
Facebook PathPicker is a simple command line tool that solves the perpetual
problem of selecting files out of bash output. PathPicker will:
* Parse all incoming lines for entries that look like files
* Present the piped input in a convenient selector UI

It is easiest to understand by watching a simple demo:
<!---
TODO -- remove token
-->
<img src="https://raw.githubusercontent.com/facebook/PathPicker/master/assets/simple_edit.gif?token=ABFRn-B9WTzjwrvwzJZIyR3Ukhky_usJks5VTQW7wA%3D%3D" />

Here is another example showing arbitrary commands rather than opening the files in an editor:
<!---
TODO -- remove token
-->
<img src="https://raw.githubusercontent.com/facebook/PathPicker/master/assets/command_replace.gif?token=ABFRnyD60MwpDuAuHUwOLNgiyxCunFq7ks5VTQdGwA%3D%3D" />

## Examples
After installing PathPicker, using it is as easy as piping into `fpp`. It takes
a wide variety of input -- try it with all the options below:

* `git status | fpp`
* `hg status | fpp`
* `git grep "FooBar" | fpp`
* `grep -r "FooBar" . | fpp`
* `git diff HEAD~1 --stat | fpp`
* `arc inlines | fpp`
* `find . -iname "*.js" | fpp`
and anything else you can dream up!

## Requirements
PathPicker should work with most Bash environments and requires Python >2.6
and <3.0.

ZSH is supported as well but won't have a few features like alias expansion.

## Installing PathPicker
PIP module -- TODO

## How PathPicker works
PathPicker is a combination of a bash script and some small Python modules.
It essentially has three steps:

* First in the bash script, redirect all standard in to a python module that
parses and extracts out the filenames. This data is saved in a temporary file
and the program exits.
* Secondly, the bash script switches to terminal input mode and
another python module reads out the saved entries and presents them in a
selector UI. The user either selects a few files to edit or inputs a command
to execute.
* Lastly, the python script outputs a command to a bash file that is later
executed by the master bash script.

It is a bit rough around the edges but provides (in our opinion) a lot of
utility.

## Join the PathPicker community
See the CONTRIBUTING file for how to help out.

## License
PathPicker is BSD-licensed. We also provide an additional patent grant.
