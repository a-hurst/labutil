import os
import sys
import shutil

from packaging.version import Version
from .utils import err, echo, run_cmd, cmd_output


PYPROJECT_TEMPLATE = """
[project]
name = "{0}"
version = "1.0"
requires-python = ">={1}"
dependencies = [
    {2}
]

[dependency-groups]
dev = [
    {3}
]
"""


def pipenv_active(taskdir):
    if not shutil.which("pipenv"):
        return False
    internal_venv = os.path.join(taskdir, '.venv')
    if os.path.exists(internal_venv):
        return False
    orig_path = os.getcwd()
    os.chdir(taskdir)
    out = cmd_output(['pipenv', '--venv'])
    os.chdir(orig_path)
    return out[:13] != "No virtualenv"


def parse_pipfile(path):
    contents = {}
    with open(path, 'r', encoding='utf-8') as f:
        section = None
        for l in f.read().splitlines():
            if not len(l):
                continue
            elif l[0] == "[" and l[-1] == "]":
                section = l.strip("[]")
                contents[section] = {}
            elif section:
                field, value = l.split("=", 1)
                field = field.strip()
                contents[section][field] = value.strip()
    for section in ['packages', 'requires']:
        if not section in contents.keys():
            contents[section] = {}
    return contents


def _parse_package(package, version):
    # Packages without pinned versions
    if version == '"*"':
        return package
    # Non-PyPI packages installed from URLs
    elif version[:5] == "{file":
        url = version.split(" = ")[-1].strip('"}')
        return "{} @ {}".format(package, url)
    # Packages installed from git repositories
    elif version[:4] == "{git":
        fields = version[1:-1].split(", ")
        raise RuntimeError("need to finish implementing this!")
    # Packages with version restrictions
    return package + version.strip('"')


def convert_pipfile(taskname, taskdir):
    path = os.path.join(taskdir, "Pipfile")
    info = parse_pipfile(path)
    # Get minimum Python version (default to Python 3.11 if not set)
    min_python = "3.11"
    if 'requires' in info.keys():
        if 'python_version' in info['requires'].keys():
            min_python = info['requires']['python_version'].strip('"')
    # Gather names of required packages
    packages = []
    for package, version in info['packages'].items():
        packages.append(_parse_package(package, version))
    # Gather names of dev packages
    dev_packages = []
    for package, version in info['dev-packages'].items():
        dev_packages.append(_parse_package(package, version))
    # If using older klibs, install old setuptools and set max Python version
    old_klibs = False
    for p in packages:
        if p[:5] == "klibs":
            url = p.split(" @ ")[-1]
            if "git+" in url:
                old_klibs = True # Err on side of caution
            elif Version(url.split("/")[-2]) < Version("0.7.8b1"):
                old_klibs = True
            break
    if old_klibs:
        if "setuptools==79.0.1" not in packages:
            packages.append("setuptools==79.0.1")
        min_python = min_python + ",<3.12"
    # Generate and save pyproject.toml
    outfile = os.path.join(taskdir, "pyproject.toml")
    pkg_str = ",\n    ".join(['"{}"'.format(p) for p in packages])
    dev_str = ",\n    ".join(['"{}"'.format(p) for p in dev_packages])
    contents = PYPROJECT_TEMPLATE.format(taskname, min_python, pkg_str, dev_str)
    with open(outfile, "w", encoding='utf-8') as out:
        out.write(contents)
