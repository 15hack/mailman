#!/bin/sh
{
for list in $(/usr/lib/mailman/bin/list_lists -b) ; do
	/usr/lib/mailman/bin/list_members --fullnames $list
done
} | sort | uniq
