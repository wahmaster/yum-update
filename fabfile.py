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
            print("<font color=green>Verifying host %s</font>" % (env.host))
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
@parallel
@excludehosts
def update():
	if run("yum check-update").return_code != 0:
		"""Run yum update with exclusions"""
		env.parallel = True
		print ("These are the excludes: %s") % (env.excludes)
                sudo("yum -y update --disablerepo='*artifactory' %s" % (env.excludes), pty=True)

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
@parallel
@excludehosts
def fastReboot():
	"""Do a fast reboot with checks."""
	with hide('everything'):
	    print "<font color=red>Rebooting %s now!</font>" % env.host
	    preresult = run("uname -r")
	    preresult.failed
	    print "<font color=red>%s kernel version before reboot:</font><font color=green> %s</font>" % (env.host, preresult)
	    """ reboot(wait=120) """
	    postresult = run("uname -r")
	    print "<font color=red>%s kernel version after reboot: <font color=green> %s</font>" % (env.host, preresult)

@task
@parallel
@excludehosts
def cleanOldKernels():
    """Get rid of all kernels except for the last two"""
    with hide('everything'):
        checkinstalled = run("rpm -q yum-utils")
        if checkinstalled == 'package yum-utils is not installed':
            print "Yum utils as not installed"
        kernels = run("rpm -q kernel")
        numkern = len(kernels.split('\n'))
        print "<font color=green>%s: Number of installed kernels: </font><font color=red>%s</font>" % (env.host, numkern)
        if numkern > 2:
            print "<font color=green>%s has more then 2 kernels, sweeping extra old kernels under the rug</font>" % env.host
            """ sudo("package-cleanup -y --oldkernels --count=2") """
            afterkernels = run("rpm -q kernel")
            afternumkern = len(afterkernels.split('\n'))
            print "<font color=green>%s now has <font color=red> %s </font><font color=green>installed kernels</font>" % (env.host, afternumkern)





@task
@parallel
@excludehosts
def kernelReport():
	"""Report all running kernel versions"""
	with hide('everything'):
		env.parallel = True
		result = run("uname -r")
		print "<font color=green>%s is running kernel version: </font><font color=red>%s</font>" % (env.host, result)

@task
@parallel
@excludehosts
def get_stats():
    """get stats from server"""
    with cd("/tmp"):
	run("uname -r")
        run("cat /proc/cpuinfo |grep processor|wc -l")
        run("free -m")
        run("egrep --color 'Mem|Cache|Swap' /proc/meminfo")
        run("df -TH")
        run("ldd --version|grep ldd")
        run("perl -v |grep 'This is perl'")

