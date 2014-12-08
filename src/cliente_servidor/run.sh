#!/bin/bash

ipython=`which ipython2 2> /dev/null || which ipython`

if [ `id -u` != 0 ] ; then
	echo "This script needs to be run as root"
	exit
fi

sudo $ipython server.py 1> /dev/null &
sudo $ipython client.py $@
