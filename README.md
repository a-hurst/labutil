# labutil

labutil is a command-line tool for managing and deploying experiments on data collection computers in cognitive science labs. It is designed to facilitate installing/managing experiments, creating double-click shortcuts, and easily deploying/running maintenance scripts across multiple computers.

It is currently in early development, and may still change unexpectedly between versions.

## Requirements

labutil is written in Python, and requires a recent version (>=3.8) in order to run. Installing experiments also requires Git to be installed on the computer.

Although labutil has been written so far with cross-platform support in mind, it has only been tested so far on Linux and does not yet support auto-creating experiment shortcuts on macOS or Windows.

## Installation

To install labutil, run the following command in a terminal:

```
python -m pip install git+https://github.com/a-hurst/labutil.git
```

## Usage

After installing labutil, the first thing you need to do is run `labutil configure` to create a configuration file for the current computer. This will specify the screen size, experiment folder, and shortcut folder for labutil to use when installing and running experiments.

Next, you will need to add a repository, which you can do using `labutil repo add [url]`, with `[url]` being a URL to a valid labutil repository.

Once a configuration has been created and a repository has been added, you can install studies from the repository by name using `labutil install [study_name]`. This will clone the experiment code into your configured Experiments folder, as well as create any corresponding shortcuts in your configured Shortcuts folder.

For performing maintenance or other regular system tasks, you can also run custom scripts by name from an added repository using `labutil script [script_name] <script_args>`.
