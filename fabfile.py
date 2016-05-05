#!/usr/bin/env python2.7

from fabric.api import *
from fabric.contrib import files
from fabric import tasks
from fabric.network import disconnect_all
from fabric.contrib.console import confirm
import re
# import os


def update():
            sudo("yum -y update --disablerepo='*artifactory' --exclude=puppet* --exclude=sensu --exclude=mongo* --exclude=redis* --exclude=rabbitmq*", pty=True)





