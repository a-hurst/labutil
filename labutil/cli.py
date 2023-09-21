import os
import time
import shutil
import click
from .utils import run_cmd, err
from .repos import load_study, load_script, load_repos, load_repo_config
from .config import create_config, read_config, config_dir
from .install import install_task, create_shortcuts

# TODO: labutil update, for pulling latest source + refreshing the pipenv
#       for a given task


@click.group()
def labutil():
    pass


@labutil.command()
@click.option("-s", "--show", is_flag=True, default=False)
def configure(show):
    if show:
        confpath = os.path.join(config_dir, "config")
        if not os.path.exists(confpath):
            e = "No labutil configuration file exists on this machine. "
            e += "Please create one with 'labutil configure'."
            err(e)
        print("\nCurrent Configuration:")
        for key, value in read_config().items():
            print(" - {0}: {1}".format(key, value))
        print("")
    else:
        create_config()


@labutil.group()
def repo():
    pass

@repo.command(name="add")
@click.argument('url')
def repo_add(url):
    repo_dir = os.path.join(config_dir, "repos")
    if not os.path.exists(repo_dir):
        os.mkdir(repo_dir)
    tmp_path = os.path.join(repo_dir, "_tmp")
    # Remove tmp repo if it already exists
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    # Clone requested repo to tmp
    os.chdir(repo_dir)
    print("")
    success = run_cmd(['git', 'clone', url, '_tmp'])
    if not success:
        err("Failed to clone the requested repository.")
    # Get repo name from config and rename accordingly
    conf = load_repo_config(tmp_path)
    repo_path = os.path.join(repo_dir, conf['name'])
    if os.path.exists(repo_path):
        shutil.rmtree(tmp_path)
        err("Repository with the name '{0}' already exists.".format(conf['name']))
    os.rename(tmp_path, repo_path)
    msg = "\n=== Repository '{0}' installed successfully ===\n"
    print(msg.format(conf['name']))

@repo.command(name="remove")
@click.argument('name')
def repo_remove(name):
    repo_dir = os.path.join(config_dir, "repos", name)
    if os.path.exists(repo_dir):
        print("")
        msg = "Repository '{0}' will be removed from labutil. Continue?"
        if click.confirm(msg.format(name)):
            shutil.rmtree(repo_dir)
            print("Repository removed successfully.\n")
    else:
        err("No repository with the name '{0}'.".format(name))

@repo.command(name="list")
def repo_list():
    repos = load_repos()
    print("\nCurrent repositories:")
    for name, info in repos.items():
        print(" - {0}: {1}".format(name, info["url"]))
    print("")

@repo.command(name="update")
def repo_update():
    repos = load_repos()
    for name, info in repos.items():
        repo_dir = os.path.join(config_dir, "repos", name)
        os.chdir(repo_dir)
        print("\nUpdating {0}...\n".format(name))
        success = run_cmd(['git', 'pull'])
        if not success:
            err("Could not update repository '{0}'.".format(name))
    print("")


@labutil.command()
@click.argument("taskname")
def install(taskname):
    # Load labconf for runtime info
    conf = read_config()
    taskinfo = load_study(taskname)

    # Make sure git installed before trying to install task
    if not shutil.which("git"):
        err("Must have Git installed to download and install experiments.")

    # Create Experiments folder if it doesn't already exist
    if not os.path.exists(conf["experiment_dir"]):
        os.mkdir(conf["experiment_dir"])
    install_task(conf["experiment_dir"], taskname, taskinfo.url)

    # Create shortcuts for the task
    if len(taskinfo.shortcuts):
        print(" * Installing shortcuts for the task...")
        if not os.path.exists(conf["shortcut_dir"]):
            os.mkdir(conf["shortcut_dir"])
        taskdir = os.path.join(conf["experiment_dir"], taskname)
        shortcut_dir = conf["shortcut_dir"]
        if taskinfo.shortcut_dir:
            shortcut_dir = os.path.join(shortcut_dir, taskinfo.shortcut_dir)
        create_shortcuts(
            shortcut_dir, taskdir, taskname, taskinfo.shortcuts
        )

    print("\n=== Installation of {0} completed successfully! ===\n".format(taskname))


@labutil.command(context_settings={"ignore_unknown_options": True})
@click.option("-w", "--wait", is_flag=True, default=False)
@click.argument('name', nargs=1)
@click.argument('args', default="")
def run(name, wait, args):

    # Try running the task
    conf = read_config()
    taskinfo = load_study(name)
    taskdir = os.path.join(conf["experiment_dir"], name)
    if os.path.exists(taskdir):
        if taskinfo.run_cmd:
            cmd = taskinfo.run_cmd.split(" ")
        else:
            cmd = ["pipenv", "run", "klibs", "run", conf["screen_size"]]
        if len(args):
            cmd += args.split(" ")
        os.chdir(taskdir)
        run_cmd(cmd)
    else:
        e = "Study '{0}' does not exist in any current repository."
        print(e.format(name))

    # Keep terminal window open at the end
    if wait:
        while True:
            time.sleep(1)


@labutil.command()
@click.option("-w", "--wait", is_flag=True, default=False)
@click.option("--taskdir", default="")
@click.argument("name")
@click.argument("args", default="")
def script(name, wait, args, taskdir):
    info = load_script(name)
    # Build the command to run
    cmd = [info['path']]
    if len(args):
        cmd += args.split(" ")
    if info['language'] == 'python':
        cmd = ['python'] + cmd
    # Actually run the script
    if len(taskdir):
        conf = read_config()
        path = os.path.join(conf["experiment_dir"], taskdir)
        os.chdir(path)
    run_cmd(cmd)
    if wait:
        while True:
            time.sleep(1)
