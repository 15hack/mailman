#!/bin/sh
/usr/lib/mailman/bin/list_lists -b > list.txt
python archive.py > last.txt
for l in $(/usr/lib/mailman/bin/list_lists -b | sort); do
	M=$(/usr/lib/mailman/bin/list_members "$l" | wc -l)
	A=$(/usr/lib/mailman/bin/list_owners -m "$l" | wc -l)
	L=$(grep "$l" last.txt | cut -d' ' -f1)
	echo "$M\t$A\t$L\t$l"
done
