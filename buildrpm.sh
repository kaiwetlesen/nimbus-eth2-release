#!/bin/bash
set -e
if [ "$1" == "--buildvarsfile" ]; then
	shift
	buildvars=$1
	shift
	if [ -n "$buildvars" ] && [ ! -f "$buildvars" ]; then
		echo 'Option "--buildvars" provided but does not point to a valid file'
		exit 1
	fi
fi
spec=$1
if [ ! -f "$spec" ]; then
	echo "Spec '$1' not found"
	exit 2
fi
dnf -y upgrade
dnf -y install dnf-plugins-core rpmdevtools
cd /root
rpmdev-setuptree
cd -
dnf -y builddep $spec
if [ -f "$buildvars" ]; then
	echo '----------------------- Fetching sources -----------------------'
	while read version; do
		spectool --debug --get-files --all --sourcedir --define="target_ver $version" $spec
	done < $buildvars
	wait
	echo '----------------------- Running builds -----------------------'
	while read version; do
		rpmbuild -D "target_ver $version" -bb $spec
	done < builds.txt
	wait
else
	spectool --debug --get-files --all --sourcedir $spec
	rpmbuild -bb $spec
fi
chmod -R a+r ${HOME}/rpmbuild/RPMS
if [ -d /rpms ]; then
	cp ${HOME}/rpmbuild/RPMS/* /rpms
fi
