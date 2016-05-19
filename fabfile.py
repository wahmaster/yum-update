#!/usr/bin/env python2.7

from fabric.api import *
from fabric.contrib import files
from fabric import tasks
from fabric.network import disconnect_all
from fabric.contrib.console import confirm
import re
import os

def excludehosts(func):
    def closuref(*args, **kwargs):
        exhosts = json.loads(env.exhosts)
        if exhosts:
            print(green("Verifying host %s") % (env.host))
            if any(env.host in s for s in exhosts):
                print(green("Excluding host %s" % (env.host)))
                return
        return func(*args, **kwargs)
    # This is necessary so that custom decorator is interpreted as fabric decorator
    # Fabric fix: https://github.com/mvk/fabric/commit/68601ae817c5c26f4937f0d04cb56e2ba8ca1e04
    # is also necessary.
    closuref.func_dict['wrapped'] = func
    return wraps(func)(closuref)

@task
@parallel
def update():
	if run("yum check-update").return_code != 0:
		"""Run yum update with exclusions"""
		env.parallel = True
		print ("These are the excludes: %s") % (env.excludes)				
                sudo("yum -y update --disablerepo='*artifactory' %s" % (env.excludes), pty=True) 

@task
@parallel
def slowReboot():
	"""Do a careful reboot with checks."""
	preresult = run("uname -r")
	preresult.failed
	reboot(wait=120)
	postresult = run("uname -r")
	print "<br/><br/>"
	print "<font color=red>Kernel version before reboot:</font><font color=green> %s</font>" % preresult
	print "<font color=red>Kernel version after reboot: <font color=green> %s</font>" % postresult
	print "<br/><br/>"


@task
@parallel
def kernelReport():
	"""Report all running kernel versions"""
	with hide('everything'):
		env.parallel = True
		result = run("uname -r")
		print "<font color=green>%s is running kernel version: </font><font color=red>%s</font>" % (env.host, result)

@task
@parallel
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

