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


def prt(s, *args, **kargv):
    if len(args) > 0:
        s = s.format(*args)
    s = s.lstrip()
    s = re_blank.sub("\n\n", s)
    print(s, **kargv)


soup = get(url)
h1 = soup.find("h1", attrs={"class": "entry-title"})

prt('''
From: 15hack@riseup.net
Subject: {0}

Share link: {1}
''', h1.get_text().strip(), url)

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
for n in content.findAll(["p"]):
    n.append("\n")
for n in content.findAll(["li"]):
    n.insert(0, "- ")
prt(content.get_text().strip())
