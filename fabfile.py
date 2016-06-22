#!/usr/bin/env python2.7

from __future__ import with_statement
from fabric.api import *
from fabric.contrib import files
from fabric import tasks
from fabric.network import disconnect_all
from fabric.contrib.console import confirm
from functools import wraps
from fabric.colors import red, green
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
@parallel(pool_size=4)
@excludehosts
def update():
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
@parallel(pool_size=8)
@excludehosts
def checkupdate():
    with hide('everything'):
        result = run("yum check-update --disablerepo='*artifactory' %s" % (env.excludes), pty=True)
        if result.return_code == 100:
		    print "<font color=yellow>%s needs updating.</font>" % env.host
        elif result.return_code == 0:
            print "<font color=blue>%s does not seem to need any updates</font>" % env.host
        elif result.return_code == 1:
            print "<font color=red>%s returned an error</font>" % env.host

@task
@excludehosts
def slowReboot():
	"""Do a careful reboot with checks."""
	with hide('everything'):
		print "<font color=red>Rebooting %s now!</font>" % env.host
		preresult = run("uname -r")
		preresult.failed
		print "<font color=red>Kernel version before reboot:</font><font color=green> %s</font>" % preresult
		reboot(wait=120)
		postresult = run("uname -r")
		print "<font color=red>Kernel version after reboot: <font color=green> %s</font>" % postresult

@task
@parallel(pool_size=5)
@excludehosts
def fastReboot():
	"""Do a fast reboot with checks."""
	with hide('everything'):
	    print "<font color=red>Rebooting %s now!</font>" % env.host
	    preresult = run("uname -r")
	    preresult.failed
	    print "<font color=red>%s kernel version before reboot:</font><font color=green> %s</font>" % (env.host, preresult)
	    reboot()
	    postresult = run("uname -r")
	    print "<font color=red>%s kernel version after reboot: <font color=green> %s</font>" % (env.host, preresult)

@task
@parallel(pool_size=5)
@excludehosts
def cleanOldKernels():
    """Get rid of all kernels except for the last two"""
    with hide('everything'):
        checkinstalled = run("rpm -q yum-utils")
        print "check results: %s" % checkinstalled
        if checkinstalled == 'package yum-utils is not installed':
            print "Yum utils as not installed, installing..."
            sudo("yum install -y yum-utils")
        kernels = run("rpm -q kernel")
        numkern = len(kernels.split('\n'))
        print "<font color=green>%s: Number of installed kernels: </font><font color=red>%s</font>" % (env.host, numkern)
        if numkern > 2:
            print "<font color=green>%s has more then 2 kernels, sweeping extra old kernels under the rug</font>" % env.host
            sudo("package-cleanup -y --oldkernels --count=2")
            afterkernels = run("rpm -q kernel")
            afternumkern = len(afterkernels.split('\n'))
            print "<font color=green>%s now has <font color=red> %s </font><font color=green>installed kernels</font>" % (env.host, afternumkern)

@task
@parallel(pool_size=5)
@excludehosts
def kernelReport():
    """Report all running kernel versions"""
    with hide('everything'):
        env.parallel = True
        result = run("uname -r")
        redhat = run("cat /etc/redhat-release")
        uptime = run("uptime")
        print "<font color=white>%s: </font><font color=yellow>%s</font>" % (env.host, result)
        print "<font color=white>%s: </font><font color=yellow>%s</font>" % (env.host, redhat)
        print "<font color=white>%s uptime: </font><font color=yellow>%s</font></br>" % (env.host, uptime)

@task
@parallel(pool_size=5)
@excludehosts
def get_stats():
    """report kernel cpus and memory info from server"""
    with hide('everything'):
        with cd("/tmp"):
            kernelver = run("uname -r")
            cpuinfo = run("cat /proc/cpuinfo |grep processor|wc -l")
            meminfo = run("egrep 'MemTotal|MemFree|MemAvailable|SwapCached|SwapTotal|SwapFree' /proc/meminfo")
            print "%s is running kernel: %s" % (env.host, kernelver)
            print "%s has %s CPU cores." % (env.host, cpuinfo)
            print "%s meminfo:\n %s \n\n" % (env.host, meminfo)

