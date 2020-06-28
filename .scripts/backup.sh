#!/bin/sh

### Database Backup Script ###

if (( $# != 3 ))
  then
      echo "Usage: $0 database /path/to/save/dump.sql user"
      exit 1
fi

DB=${1}
DIR=${2}
DB_USER=${3}

echo "[`date "+%d-%m-%Y %H:%M:%S"`] Initiating backup of [${DB}] to: [${DIR}]"
/usr/bin/mysqldump -u ${DB_USER} ${DB} > ${DIR}
echo "[`date "+%d-%m-%Y %H:%M:%S"`] Backup complete"