import os
import shutil

from .utils import err, run_cmd
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
        success = run_cmd(["pipenv", "install"])
        if not success:
            err("Unable to create the task's virtual environment.")    

def create_shortcuts(shortcut_dir, taskdir, taskname, shortcuts):
    if os.path.exists(shortcut_dir):
        shutil.rmtree(shortcut_dir)
    os.mkdir(shortcut_dir)
    for name, info in shortcuts.items():
        create_shortcut(shortcut_dir, name, taskdir, taskname, info)
