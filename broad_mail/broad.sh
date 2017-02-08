#!/bin/sh
MAIL=$1
for list in $(/usr/lib/mailman/bin/list_lists -b) ; do
#while read list; do
	msg=$(mktemp)
	echo "To: $list" > $msg
	cat "$MAIL" >> $msg
	/usr/lib/mailman/bin/inject -l $list $msg
#done < $1
done
