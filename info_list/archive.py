# -*- coding: utf-8 -*-
import glob
import mailbox
import re
import fnmatch
import os
from datetime import datetime
from email.utils import parsedate_tz

mboxs = []
for root, dirnames, filenames in os.walk('/var/lib/mailman/archives/private/'):
  for filename in fnmatch.filter(filenames, '*.mbox'):
    mboxs.append(os.path.join(root, filename))

campos=["From", "To"]
correo=re.compile(r"[^<\"@\s]+@[^@\s]+\.[^@\s>\",]+")

data={}

def to_datetime(datestring):
    try:
      time_tuple = parsedate_tz(datestring.strip())
      dt = datetime(*time_tuple[:6])
      return dt
    except:
      print datestring
      return None

for mbox in mboxs:
  #print mbox
  mbox = mailbox.mbox(mbox)
  for mail in mbox:
    if mail["From"] and "15hack@riseup.net" in mail["From"]:
      continue
    correos=[]
    #print mail['Date']
    date=to_datetime(mail['Date'])
    if not date:
      continue
    #print str(date)
    for campo in campos:
      if mail[campo]:
        correos = correos + [c.lower() for c in  correo.findall(mail[campo])]

    correos=sorted(list(set(correos)))
    for c in correos:
      if not c in data or data[c]<date:
        data[c]=date
    #print str(correos)

correos=sorted(data.keys())
for c in correos:
  print str(data[c])+"\t"+c
