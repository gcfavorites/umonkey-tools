#!/bin/sh
#
# This script uploads all GAE instances (subfolders).  For this to work,
# the .hg/hgrc file must contain the following code:
#
#     [hooks]
#     preoutgoing.gae = sh gae/upload.sh

if [ -z "${MAIL}" ]; then
	echo "Please set the MAIL envar to update GAE on push." >&2
	exit 1
fi

if [ -z "${GAE_DIR}" ]; then
	echo "Please point the GAE_DIR envar to SDK update GAE on push." >&2
	exit 1
fi

ROOT=$(hg root)

for dir in ${ROOT}/gae/*; do
	if [ -d "${dir}" -a -f "${dir}/app.yaml" ]; then
		echo "Updating $(basename ${dir})"
		${GAE_DIR}/appcfg.py -e ${MAIL} update ${dir}
	fi
done
