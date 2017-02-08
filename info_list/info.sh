#!/bin/sh
for l in $(/usr/lib/mailman/bin/list_lists -b | sort); do
	M=$(/usr/lib/mailman/bin/list_members "$l" | wc -l)
	A=$(/usr/lib/mailman/bin/list_owners -m "$l" | wc -l)
	echo "$M\t$A\t$l"
done
