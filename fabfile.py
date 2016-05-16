#!/usr/bin/env python2.7

from fabric.api import *
from fabric.contrib import files
from fabric import tasks
from fabric.network import disconnect_all
from fabric.contrib.console import confirm
import re
import os


@parallel
def update():
	if run("yum check-update").return_code != 0:
		"""Run yum update with exclusions"""
		env.parallel = True
		print ("These are the excludes: %s") % (env.excludes)				
                sudo("yum -y update --disablerepo='*artifactory' %s" % (env.excludes), pty=True) 

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


@parallel
def kernelReport():
	"""Report all running kernel versions"""
	env.parallel = True
	result = run("uname -r")
	print "<font color=red>Kernel version:</font><font color=green> %s</font>" % result

@parallel
def get_stats():
    """get stats from server"""
    with cd("/tmp"):
	kernver = run("uname -r")
        cpus = run("cat /proc/cpuinfo |grep processor|wc -l")
        freemem = run("free -m")
        meminfo = run("egrep --color 'Mem|Cache|Swap' /proc/meminfo")
        dfinfo = run("df -TH")
        lddinfo = run("ldd --version|grep ldd")
        perlver = run("perl -v |grep 'This is perl'")
	print "<font color=red>Kernel version:</font><font color=green> %s</font>" % kernver
	print "<font color=red>CPUs:</font><font color=green> %s</font>" % cpus
	print "<font color=red>Free Memory:</font><font color=green> %s</font>" % freemem
	print "<font color=red>Memory Info:</font><font color=green> %s</font>" % meminfo
	print "<font color=red>df info:</font><font color=green> %s</font>" % dfinfo
	print "<font color=red>ldd info:</font><font color=green> %s</font>" % lddinfo
	print "<font color=red>Perl version:</font><font color=green> %s</font>" % perlver

