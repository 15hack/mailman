#!/usr/bin/env python3
import re
import sys
from urllib.parse import urljoin

import bs4
import requests
import urllib3

from markdownify import markdownify, MarkdownConverter

urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()


class MyConverter(MarkdownConverter):
    def convert_a(self, el, text, convert_as_inline):
        url = el.attrs["href"]
        if "." in text and text in url:
            return text
        return text+ " <{}>".format(url.rstrip("/"))
        #return super().convert_a(el, text, convert_as_inline)

def my_md(html, **options):
    return MyConverter(**options).convert(html)

def to_md(s):
    txt_md = my_md(str(s), bullets="*")
    txt_md = re.sub(r"^\s*\n", "", txt_md)
    txt_md = re.sub(r"\n\s*\n\s*\n+", "\n\n", txt_md)
    txt_md = re.sub(r"\n+#", "\n\n#", txt_md)
    return txt_md.rstrip()

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

soup = get(url)
h1 = soup.find("h1", attrs={"class": "entry-title"})

print('''
From: 15hack@riseup.net
Subject: {0}

Share link: {1}
'''.format(h1.get_text().strip(), url).strip()+"\n")

content = soup.find("div", attrs={"class": "entry-content"})
for a in content.findAll("a"):
    txt = a.get_text().strip()
    url = a.attrs.get("href", None)
    if len(txt) == 0 or url is None or url.startswith("#"):
        a.unwrap()

print(to_md(content))
