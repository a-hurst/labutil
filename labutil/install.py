import os
import sys
import shutil

from .utils import err, echo, run_cmd, cmd_output
from .shortcuts import create_shortcut


def install_task(exp_dir, taskname, url):
    taskdir = os.path.join(exp_dir, taskname)
    if os.path.exists(taskdir):
        msg = " * '{0}' already exists in the experiments folder, skipping..."
        print(msg.format(taskname))
        return
    print("\n=== Installing experiment code for {0} ===\n".format(taskname))
    os.chdir(exp_dir)
    success = run_cmd(['git', 'clone', url])
    if not success:
        err("Errors encountered installing the task.")
    # Initialize the pipenv for the task, if one exists
    if os.path.exists(os.path.join(taskdir, 'Pipfile')):
        print("\n=== Initializing the task's virtual environment ===\n")
        os.chdir(taskdir)
        tracked_lockfile = cmd_output(['git', 'ls-files', 'Pipfile.lock'])
        if tracked_lockfile:
            success = run_cmd(["pipenv", "install", "--deploy"])
        else:
            success = run_cmd(["pipenv", "install"])
        if not success:
            err("Unable to create the task's virtual environment.")


def update_task(exp_dir, taskname):
    taskdir = os.path.join(exp_dir, taskname)
    print("\n=== Updating code for {0} ===\n".format(taskname))
    os.chdir(taskdir)
    # First, check for local changes
    changes = []
    clean = run_cmd(['git', 'diff-index', '--quiet', 'HEAD', '--'])
    if not clean:
        for line in cmd_output(['git', 'status', '-s']).split("\n"):
            changes.append(line.split(" ")[-1])
    # If already up to date, exit early
    cmd_output(['git', 'fetch'])
    rev_local = cmd_output(['git', 'rev-parse', 'HEAD'])
    rev_latest = cmd_output(['git', 'rev-parse', '@{u}'])
    if rev_local == rev_latest:
        if len(changes):
            print("NOTE: The following files have been modified locally:")
            for f in changes:
                echo(" - " + f, 'yellow')
            print("")
        print("=== Already up to date! ===\n")
        return
    # Check for local modifications to the code that might be overwritten
    if len(changes):
        echo("--- Update Aborted ---", color='red')
        print("Updating the task would overwrite local changes to the following files:")
        for f in changes:
            echo(" - " + f, 'yellow')
        print("\nPlease revert or back up these changes before trying to update.\n")
        sys.exit(1)
    # If we're all good, pull the latest updates
    success = run_cmd(['git', 'pull'])
    if not success:
        err("Errors encountered updating the task code.")
    # Update the Pipenv for the task, if one exists
    if os.path.exists('Pipfile'):
        print("\n=== Updating the task's virtual environment ===\n")
        tracked_lockfile = cmd_output(['git', 'ls-files', 'Pipfile.lock'])
        if tracked_lockfile:
            success = run_cmd(['pipenv', 'sync'])
        else:
            success = run_cmd(['pipenv', 'update'])
        if not success:
            err("Error encountered updating the virtual environment.")
        # Remove any packages that were removed from the pipfile
        run_cmd(['pipenv', 'clean'])
        print("")


def create_shortcuts(shortcut_dir, taskdir, taskname, shortcuts):
    if os.path.exists(shortcut_dir):
        shutil.rmtree(shortcut_dir)
    os.mkdir(shortcut_dir)
    for name, info in shortcuts.items():
        create_shortcut(shortcut_dir, name, taskdir, taskname, info)
