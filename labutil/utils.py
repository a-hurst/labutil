import sys
import subprocess as sub
import click

def err(msg):
    e = "\nError: {0}\n".format(msg)
    click.echo(click.style(e, fg='red'))
    sys.exit()

def run_cmd(cmd):
    p = sub.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    p.communicate()
    return p.returncode == 0
