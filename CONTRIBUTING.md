# Contributing to Facebook PathPicker

Welcome to the community and thanks for stopping by! Facebook PathPicker is actually quite
easy to contribute to -- it has minimal external and internal dependencies and just some
simple input-output tests to run.

The easiest way to get set up is to:
* First, clone the repo with:
  * `git clone https://github.com/facebook/PathPicker.git`
* Second, ensure you have Python 3 installed:
  * `python3 --version`
* Go ahead and execute the script!
  * `cd PathPicker; ./fpp`

The three areas to contribute to are:
* Regex parsing (for detecting filenames and ignoring normal code)
* UI functionality (either bug fixes with curses or new functionality)
* General pipeline work related to our bash scripts.

### Pull Requests

Send them over! Our bot will ask you to sign the CLA and after that someone
from the team will start reviewing.

Before sending them over, make sure the tests pass with:
`./scripts/runTests.sh`

### Test dependencies

* Install [poetry](https://github.com/python-poetry/poetry).
* Select poetry environment with `poetry env use 3.6`. Some linters depend on Python version and it's better to check on the same version as we use in CI.

### PyCharm project
You can open PathPicker in PyCharm. You will also need to install [poetry plugin](https://plugins.jetbrains.com/plugin/14307-poetry) for using poetry environment.

### Contributor License Agreement ("CLA")

In order to accept your pull request, we need you to submit a CLA. You only need to do this once, so if you've done this for another Facebook open source project, you're good to go. If you are submitting a pull request for the first time, just let us know that you have completed the CLA and we can cross-check with your GitHub username.
[Complete your CLA here](https://code.facebook.com/cla)

## Bugs

### Where to Find Known Issues

We will be using GitHub Issues for our public bugs. It's worth checking there before reporting your own issue.

### Reporting New Issues

Always try to provide a minimal test case that repros the bug.

### Documentation

* Do not wrap lines at 80 characters - configure your editor to soft-wrap when editing documentation.

## License

By contributing to Facebook PathPicker, you agree that your contributions will be licensed under its MIT license.
