#!/bin/sh
for l in $(/usr/lib/mailman/bin/list_lists -b | grep "$1" | sort); do
	echo -n "$l: "
	/usr/lib/mailman/bin/list_members "$l" | wc -l
done
