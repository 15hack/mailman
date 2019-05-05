#!/usr/bin/env python3
import re
import sys
from urllib.parse import urljoin

import bs4
import requests
import urllib3

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()

re_blank = re.compile(r"\n\s*\n")
heads = ["h" +str(h) for h in range(1,7)]

def get(url):
    r = requests.get(url, verify=False)
    soup = bs4.BeautifulSoup(r.content, "lxml")
    for a in soup.findAll("a[href]"):
        href = a.attrs["href"]
        if not href.startswith("#"):
            a.attrs["href"] = urljoin(url, href)
    return soup


url = sys.argv[1] if len(sys.argv) == 2 else None
if url is None or url.isdigit():
    soup = get("https://15hack.tomalaplaza.net")
    index = (1 if url is None else int(url))-1
    entradas = soup.findAll("h1", attrs={"class": "entry-title"})
    if index < 0 or index >= len(entradas):
        sys.exit("El indice ha de estar entre %s and %s" % (1, len(entradas)))
    h1 = entradas[index]
    a = h1.find("a")
    url = a.attrs["href"]
elif not url.startswith("http"):
    sys.exit(url + " no es una url valida")


def prt(*args, **kargv):
    args = list(args)
    for i, a in enumerate(args):
        if isinstance(a, bs4.Tag):
            args[i] = a.get_text().strip()
    s = args[0]
    if len(args) > 1:
        s = s.format(*args[1:])
    s = s.lstrip()
    s = re_blank.sub("\n\n", s)
    print(s, **kargv)

def subrayar(tag, c="="):
    txt = tag.get_text()
    ancho = max(len(l.rstrip()) for l in txt.split("\n"))
    sub = "=" * ancho
    if not txt.endswith("\n"):
        sub = "\n" + sub
    if txt.endswith("\n"):
        sub = sub + "\n"
    tag.append(sub)


soup = get(url)
h1 = soup.find("h1", attrs={"class": "entry-title"})

prt('''
From: 15hack@riseup.net
Subject: {0}

Share link: {1}
''', h1, url)

content = soup.find("div", attrs={"class": "entry-content"})
for a in content.findAll("a"):
    txt = a.get_text().strip()
    url = a.attrs.get("href", None)
    if len(txt) == 0 or url is None or url.startswith("#"):
        a.unwrap()
    else:
        if txt in url:
            a.string = url
        else:
            a.append(" (%s)" % url)

for n in content.findAll(["p"] + heads):
    n.append("\n")

i = 0
for hs in heads:
    hs = content.findAll(hs)
    if len(hs)>0:
        pre = ("#" * i)+" "
        for h in hs:
            if i == 0:
                subrayar(h)
            else:
                h.insert(0 , pre)
        i + 1
for n in content.findAll(["li"]):
    n.insert(0, "- ")
prt(content)
