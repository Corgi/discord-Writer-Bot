#!/bin/sh

### Restore Database Script ###

if (( $# != 3 ))
  then
      echo "Usage: $0 database /path/to/dump.sql user"
      exit 1
fi

DB=${1}
FILE=${2}
DB_USER=${3}

echo "[`date "+%d-%m-%Y %H:%M:%S"`] Initiating restore of [${DB}] from: [${FILE}]"
mysql -u ${DB_USER} -p -e "DROP DATABASE IF EXISTS ${DB}; CREATE DATABASE IF NOT EXISTS ${DB}; USE ${DB}; SOURCE ${FILE};"
echo "[`date "+%d-%m-%Y %H:%M:%S"`] Restore complete"