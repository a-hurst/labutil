import os
import shutil
import yaml
from .utils import err
from .config import config_dir


class Study(object):

    def __init__(self, name, info):
        # Make sure required fields are all there
        fields = list(info.keys())
        if not "url" in fields:
            e = "Required field 'url' missing from study '{0}'"
            raise RuntimeError(e.format(name))
        
        # Initialize fields
        self.name = name
        self.url = info["url"]
        self.run_cmd = info['run_cmd'] if 'run_cmd' in fields else None
        self.shortcut_dir = info['shortcut_dir'] if 'shortcut_dir' in fields else None

        # Parse any shortcuts for the study
        self.shortcuts = {}
        if 'shortcuts' in fields:
            for s in info['shortcuts']:
                sfields = list(s.keys())
                if not "name" in sfields:
                    e = "Required field 'name' missing from shortcut for study '{0}'"
                    raise RuntimeError(e.format(name))
                self.shortcuts[s['name']] = {
                    "script": s['script'] if 'script' in sfields else None,
                    "args": s['args'] if 'args' in sfields else "",
                    "xdg_icon": s['xdg_icon'] if 'xdg_icon' in sfields else None,
                }


def load_repo_config(path):
    config_file = os.path.join(path, "repo.yml")
    with open(config_file, "r") as f:
        repo_conf = yaml.safe_load(f.read())
    return repo_conf

def load_repos():
    repo_dir = os.path.join(config_dir, "repos")
    tmp_path = os.path.join(repo_dir, "_tmp")
    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
    repos = {}
    for repo in os.listdir(repo_dir):
        repo_path = os.path.join(repo_dir, repo)
        if not os.path.isdir(repo_path):
            continue
        repo_conf = load_repo_config(repo_path)
        repos[repo] = repo_conf
    return repos

def load_study(name):
    study = None
    repos = load_repos()
    for repo, config in repos.items():
        if name in config['studies'].keys():
            study = Study(name, config['studies'][name])
            break
    if not study:
        err("No task matching the name '{0}' in any current repository.".format(name))
    return study

def load_script(name):
    script = None
    repos = load_repos()
    for repo, config in repos.items():
        if name in config['scripts'].keys():
            tmp = config['scripts'][name]
            # Ensure required fields exist
            for field in ['script', 'language']:
                if not field in tmp.keys():
                    e = "Required field '{0}' missing for script '{1}'."
                    err(e.format(field, name))
            # Ensure script file exists in repo
            script_dir = os.path.join(config_dir, 'repos', repo, 'scripts')
            script_path = os.path.join(script_dir, tmp['script'])
            if not os.path.exists(script_path):
                e = "Script '{0}' does not exist within the {1} repository."
                err(e.format(tmp['script'], repo))
            script = tmp.copy()
            script['path'] = script_path
            break
    if not script:
        err("No script with the name '{0}' in any current repository.".format(name))
    return script
