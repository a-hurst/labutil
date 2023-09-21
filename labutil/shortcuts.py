import os
import sys

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
        cmd = 'labutil script -w {0} "{1}" --taskdir {2}'
        cmd = cmd.format(info['script'], info['args'], taskname)
    else:
        cmd = 'labutil run -w {0} "{1}"'
        cmd = cmd.format(taskname, info['args'])
    icon = info['xdg_icon'] if info['xdg_icon'] else "application-other"
    shortcut = xdg_template.format(cmd, taskdir, taskname, icon)
    # Write shortcut to file
    outpath = os.path.join(shortcut_dir, name)
    print("   - {0}".format(outpath))
    with open(outpath, "w") as f:
        f.write(shortcut)

def create_shortcut(shortcut_dir, name, taskdir, taskname, info):
    if sys.platform == "linux":
        create_shortcut_linux(shortcut_dir, name, taskdir, taskname, info)
    else:
        msg = " - Shortcuts not yet implemented for platform '{0}'"
        print(msg.format(sys.platform))
