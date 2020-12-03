#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2012 by the Free Software Foundation, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

__doc__ = """Create a json map of all mailing lists.

Usage: %(program)s [options]

Where:

    -p / --public
        Show only public info.

    --virtual-host-overview=domain
    -V domain
        List only those mailing lists that are homed to the given virtual
        domain.  This only works if the VIRTUAL_HOST_OVERVIEW variable is
        set.

    --outputfile filename
    -o filename
        Output. By default standard out is used.

    -h / --help
        Print this text and exit.

If you want use it in cron you can do:

$ touch %(rela_out)s
$ chmod 600 %(rela_out)s

and add in crontad this rule:

0 0 * * * %(full_path)s -o %(full_out)s
"""

import sys
sys.path.insert(0, '/usr/lib/mailman')

import getopt
import json
import mailbox
from datetime import datetime
from email.utils import parsedate_tz, mktime_tz
from time import time
from os.path import isfile, isdir, realpath, abspath, basename
from os import getcwd
import re
from glob import iglob

from Mailman import mm_cfg
from Mailman import MailList
from Mailman import Utils
from Mailman import Errors
from Mailman.i18n import _
# l=MailList.MailList(Utils.list_names()[0], lock=0)

program = sys.argv[0]
full_path = abspath(__file__)
rela_out =(basename(__file__).split(".", 1)[0])+".json"
full_out = getcwd()+"/"+rela_out
re_campaign = re.compile(r"\b15hack\b.*blogs.*[nm]umble.*etc", re.IGNORECASE)


def usage(code, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, _(__doc__)
    if msg:
        print >> fd, msg
    sys.exit(code)


def url_key(url):
    schema, url = url.split("://", 1)
    dom, path = url.split("/", 1)
    dom = dom.split(".")
    dom.reverse()
    dom = tuple(dom)
    key = tuple((dom, path, schema))
    return key


def to_epoch(maildate):
    input = maildate.strip()
    time_tuple = parsedate_tz(input)
    if time_tuple:
        dt = mktime_tz(time_tuple)
        return dt


def get_mails(l):
    if l.ArchiveFileName() and isfile(l.ArchiveFileName()):
        n = l.internal_name().lower()
        mbox = mailbox.mbox(l.ArchiveFileName())
        for m in mbox:
            frm = (m["From"] or "").strip().lower()
            if "15hack@riseup.net" in frm:
                continue
            sbj = (m["Subject"] or "")
            sbj = " ".join(sbj.split())
            if re_campaign.search(sbj):
                continue
            #if n not in frm and n not in (m["To"] or "").lower():
            #    continue
            yield m


def get_info_mails(l):
    ok = l.ArchiveFileName() and isfile(l.ArchiveFileName())
    r = {
        "__mbox__": l.ArchiveFileName(),
        "__exists__": ok,
        "archive": l.archive,
        "first_date": None,
        "last_date": None,
        "mails": 0
    }
    for m in get_mails(l):
        r["mails"] = r["mails"] + 1
        date = to_epoch(m['Date'])
        if date is not None:
            if r["first_date"] is None:
                r["first_date"] = date
                r["last_date"] = date
                continue
            if r["first_date"] > date:
                r["first_date"] = date
            if r["last_date"] < date:
                r["last_date"] = date
    if r["mails"] == 0 and not(l.archive and ok):
        r["mails"] = None
    base = l.GetBaseArchiveURL().rstrip("/")
    adir = l.archive_dir().rstrip("/")
    lbse = len(adir)
    arch = iglob(adir+"/**/*.html")
    arch = [base+a[lbse:] for a in arch if basename(a)[:-5].isdigit()]
    arch = sorted(arch)
    r["urls"]=arch
    return r

def trim(s):
    if s is None:
        return None
    s = s.strip()
    if len(s)==0:
        return None
    try:
        s.decode("utf-8")
    except UnicodeDecodeError:
        s = s.decode('latin-1')
        s = s.encode("utf-8")
    return s

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'pV:o:h',
                                   ['public',
                                    'virtual-host-overview=',
                                    'outputfile=',
                                    'help'])
    except getopt.error, msg:
        usage(1, msg)

    advertised = 0
    public = 0
    vhost = None
    outfile = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-p', '--public'):
            public = 1
        elif opt in ('-V', '--virtual-host-overview'):
            vhost = arg
        elif opt in ('-o', '--outputfile'):
            outfile = arg

    names = Utils.list_names()
    names.sort()

    mlists = []
    for n in names:
        l = MailList.MailList(n, lock=0)
        if public and not l.advertised:
            continue
        if vhost and mm_cfg.VIRTUAL_HOST_OVERVIEW and \
                vhost.find(l.web_page_url) == -1 and \
                l.web_page_url.find(vhost) == -1:
            continue
        mlists.append(l)

    data = {
        "__timestamp__": time()
    }
    webs = set(i.web_page_url for i in mlists)
    webs = sorted(webs, key=url_key)
    mlists = sorted(mlists, key=lambda l: l.internal_name())
    for web in webs:
        key = web+"listinfo"
        data[key] = []
        for l in mlists:
            if l.web_page_url != web:
                continue
            obj = {
                "mail": l.internal_name(),
                "description": trim(l.description),
                "msg_header": trim(l.msg_header),
                #"msg_footer": trim(l.msg_footer),
                "last_post_time": l.last_post_time,
                "created_at": l.created_at,
                "visibility": {
                    "advertised": l.advertised,
                    "private_roster": l.private_roster,
                    "archive_private": l.archive_private,
                },
                "url": {
                    "listinfo": l.GetScriptURL('listinfo', absolute=1),
                    "archive": l.GetBaseArchiveURL(),
                },
            }
            if not(public and l.archive_private):
                obj['archive'] = get_info_mails(l)
            if not(public and l.private_roster):
                rmembers = l.getRegularMemberKeys()
                dmembers = l.getDigestMemberKeys()
                members = set(rmembers + dmembers)
                members = sorted(members)
                obj['users'] = {
                    "owner": l.owner,
                    "moderator": l.moderator,
                    "members": members,
                    "total": len(set(l.owner + l.moderator + members))
                }
            data[key].append(obj)
    if outfile is None:
        print(json.dumps(data, indent=2))
    else:
        with open(outfile, "w") as f:
            json.dump(data, f, indent=2)


if __name__ == '__main__':
    main()
