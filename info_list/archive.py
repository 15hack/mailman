# -*- coding: utf-8 -*-
import glob
import mailbox
import re
import fnmatch
import os

mboxs = []
for root, dirnames, filenames in os.walk('/var/lib/mailman/archives/private/'):
    for filename in fnmatch.filter(filenames, '*.mbox'):
        mboxs.append(os.path.join(root, filename))

campos=["From", "To"]
correo=re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

data={}

for mbox in mboxs:
	print mbox
	mbox = mailbox.mbox(mbox)
	for mail in mbox:
		correos=[]
		print mail['Date']
		for campo in campos:
			if mail[campo]:
				correos = correos + correo.findall(mail[campo])
		for i in range(len(correos)):
			c=correos[i].strip()
			if c[-1]==",":
				c=c[0:-1]
				correos[i]=c
			while (c[0]=="<" and c[-1]==">") or (c[0]=="\"" and c[-1]=="\""):
				c=c[1:-1]
				correos[i]=c
		correos=sorted(list(set(correos)))
		print str(correos)
