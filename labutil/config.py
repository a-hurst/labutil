import os
import sys
import click
import platformdirs as pd


config_dir = pd.user_data_dir("labutil", "labutil")

def _get_desktop_dir():
    if sys.platform == "win32":
        from platformdirs.windows import get_win_folder
        return os.path.normpath(get_win_folder("CSIDL_DESKTOPDIRECTORY"))
    else:
        homedir = os.path.abspath(os.path.expanduser("~"))
        return os.path.join(homedir, "Desktop")


def create_config():
    outpath = os.path.join(config_dir, "config")
    default_exp_dir = os.path.join(pd.user_documents_dir(), "Experiments")
    default_shortcut_dir = os.path.join(_get_desktop_dir(), "Shortcuts")
    if os.path.exists(outpath):
        s = "A configuration file for this computer already exists. Overwrite?"
        if not click.confirm(s):
            return 1
    conf = {}
    # TODO: input sanitization
    conf['screen_size'] = click.prompt(
        "Please enter the computer's diagonal screen size (in inches)"
    ).strip()
    conf['experiment_dir'] = click.prompt(
        "Please enter the full path to the desired experiments folder",
        default=default_exp_dir
    ).strip()
    conf['shortcut_dir'] = click.prompt(
        "Please enter the full path to the desired shortcuts folder",
        default=default_shortcut_dir
    ).strip()
    # Actually write out the file
    out = ""
    for k, value in conf.items():
        out += "{0} = {1}\n".format(k, value)
    if os.path.exists(outpath):
        os.remove(outpath)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    with open(outpath, "w") as f:
        f.write(out)


def read_config():
    confpath = os.path.join(config_dir, "config")
    conf = {}
    with open(confpath, "r") as f:
        for line in f.readlines():
            if not len(line):
                continue
            setting, value = line.split(" = ", 1)
            conf[setting.strip()] = value.strip()
    return conf
