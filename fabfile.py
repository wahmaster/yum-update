#!/usr/bin/env python2.7

from __future__ import with_statement
from fabric.api import *
from fabric.contrib import files
from fabric import tasks
from fabric.network import disconnect_all
from fabric.contrib.console import confirm
from functools import wraps
from fabric.colors import red, green
from time import sleep
import json
import re
import os

def excludehosts(func):
    def closuref(*args, **kwargs):
        exhosts = json.loads(env.exhosts)
        if exhosts:
            if any(env.host in s for s in exhosts):
                print("<font color=red>Excluding host %s</font>" % (env.host))
                return
        return func(*args, **kwargs)
    # This is necessary so that custom decorator is interpreted as fabric decorator
    # Fabric fix: https://github.com/mvk/fabric/commit/68601ae817c5c26f4937f0d04cb56e2ba8ca1e04
    # is also necessary.
    closuref.func_dict['wrapped'] = func
    return wraps(func)(closuref)

@task
@parallel(pool_size=8)
@excludehosts
def update():
    """Will update servers in the stage"""
    result = run("yum check-update --disablerepo='*artifactory' %s" % (env.excludes), pty=True)
    if result.return_code == 100:
     """Run yum update with exclusions"""
     print "<font color=yellow>%s needs updating.</font>" % env.host
     print ("These are the excludes: %s") % (env.excludes)
     sudo("yum -y update --disablerepo='*artifactory' %s" % (env.excludes), pty=True)
    elif result.return_code == 0:
     print "<font color=red>%s does not seem to need any updates, skipping...</font>" % env.host
    elif result.return_code == 1:
     print "<font color=red>%s returned an error</font>" % env.host

@task
@parallel(pool_size=4)
@excludehosts
def DoTheReboot():
	"""Do a fast reboot with no checks."""
	with hide('commands'):
	    print "<font color=red>Rebooting %s now!</font>" % env.host
	    preresult = run("uname -r")
	    preresult.failed
	    print "<font color=red>%s kernel version before reboot:</font><font color=green> %s</font>" % (env.host, preresult)
	    reboot(wait=120)
        postresult = run("uname -r")
        print "<font color=red>%s Kernel version after reboot: <font color=green> %s</font>" % (env.host, postresult)

@task
@parallel(pool_size=4)
@excludehosts
def getUptime():
	with hide('commands'):
	    uptime = run("uptime")
	    uname = run("uname -r")
	    print "<font color=red>%s Uptime:</font><font color=green> %s</font>" % (env.host, uptime)
	    print "<font color=red>%s Kernel:</font><font color=green> %s</font>" % (env.host, uname)

@task
@parallel(pool_size=5)
@excludehosts
def cleanOldKernels():
    """Get rid of all kernels except for the last two"""
    with hide('commands'):
        checkinstalled = run("rpm -q yum-utils")
        print "<font color=white>check results: %s is installed</font>" % checkinstalled
        if checkinstalled == 'package yum-utils is not installed':
            print "Yum utils as not installed, installing..."
            sudo("yum install -y yum-utils")
        kernels = run("rpm -q kernel")
        numkern = len(kernels.split('\n'))
        print "<font color=white>%s: Number of installed kernels: </font><font color=red>%s</font>" % (env.host, numkern)
        if numkern > 2:
            print "<font color=white>%s has more then 2 kernels, sweeping extra old kernels under the rug</font>" % env.host
            sudo("package-cleanup -y --oldkernels --count=2")
            afterkernels = run("rpm -q kernel")
            afternumkern = len(afterkernels.split('\n'))
            print "<font color=white>%s now has <font color=red> %s </font><font color=white>installed kernels</font>" % (env.host, afternumkern)

