import sys
import subprocess as sub
import click

def err(msg):
    e = "\nError: {0}\n".format(msg)
    click.echo(click.style(e, fg='red'))
    sys.exit(1)

def echo(msg, color='bright_green'):
    click.echo(click.style(msg, fg=color))

def run_cmd(cmd):
    p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()
    return p.returncode == 0

def cmd_output(cmd):
    ret = sub.run(cmd, capture_output=True, text=True)
    out = ret.stderr if len(ret.stderr) else ret.stdout
    return out.rstrip()
