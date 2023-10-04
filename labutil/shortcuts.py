import os
import sys
import shutil

xdg_template = """
[Desktop Entry]
Exec={0}
Path={1}
Name={2}
Type=Application
Icon={3}
Terminal=true
StartupNotify=true
X-KDE-SubstituteUID=false
"""

def create_shortcut_linux(shortcut_dir, name, taskdir, taskname, info):
    if info["script"]:
        cmd = 'bash -i labutil script -w {0} "{1}" --taskdir {2}'
        cmd = cmd.format(info['script'], info['args'], taskname)
    else:
        cmd = 'bash -i labutil run -w {0} "{1}"'
        cmd = cmd.format(taskname, info['args'])
    icon = info['xdg_icon'] if info['xdg_icon'] else "application-other"
    shortcut = xdg_template.format(cmd, taskdir, name, icon)
    # Write shortcut to file
    outpath = os.path.join(shortcut_dir, name)
    if not os.getenv("XDG_CURRENT_DESKTOP", "") == "KDE":
        outpath += ".desktop"  # Needed for Linux Mint, at least
    if os.path.exists(outpath):
        os.remove(outpath)
    print("   - {0}".format(outpath))
    with open(outpath, "w") as f:
        f.write(shortcut)

def create_shortcut_windows(shortcut_dir, name, taskdir, taskname, info):
    from win32com.client import Dispatch
    outpath = os.path.join(shortcut_dir, "{0}.lnk".format(name))
    # Generate command for shortcut
    if info["script"]:
        cmd = 'labutil script {0} "{1}" --taskdir {2}'
        cmd = cmd.format(info['script'], info['args'], taskname)
    else:
        cmd = 'labutil run {0} "{1}"'
        cmd = cmd.format(taskname, info['args'])
    # Remove shortcut if it already exists
    if os.path.exists(outpath):
        os.remove(outpath)
    # Create shortcut using pywin32
    sh = Dispatch("WScript.Shell")
    lnk = sh.CreateShortcut(outpath)
    lnk.TargetPath = shutil.which("cmd")
    lnk.WorkingDirectory = taskdir
    lnk.Arguments = '"/K" ' + cmd
    print("   - {0}".format(outpath))
    lnk.save()

def create_shortcut(shortcut_dir, name, taskdir, taskname, info):
    if sys.platform == "linux":
        create_shortcut_linux(shortcut_dir, name, taskdir, taskname, info)
    elif sys.platform == "win32":
        create_shortcut_windows(shortcut_dir, name, taskdir, taskname, info)
    else:
        msg = " - Shortcuts not yet implemented for platform '{0}'"
        print(msg.format(sys.platform))
