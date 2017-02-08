#!/bin/sh
for list in $(/usr/lib/mailman/bin/list_lists -b) ; do
#while read list; do
	/usr/lib/mailman/bin/config_list -i _add.py $list
#done < $1
done
