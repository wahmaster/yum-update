#!/usr/bin/env python2.7

from fabric.api import *
from fabric.contrib import files
from fabric import tasks
from fabric.network import disconnect_all
from fabric.contrib.console import confirm
import re
import os


def update():
	"""Run yum update with exclusions"""
	sudo("yum -y update --disablerepo='*artifactory' --exclude=puppet* --exclude=sensu --exclude=mongo* --exclude=redis* --exclude=rabbitmq*", pty=True)

def slowReboot():
	"""Do a careful reboot with checks."""
	print("Get the kernel version before reboot.")
	preresult = run("uname -r")
	preresult.failed
	print "Let's talk about %s." % preresult
	# reboot(wait=120)
	print("Get the kernel version after reboot.")
	postresult = run("uname -f")
	print "Let's talk about %s." % postresult


