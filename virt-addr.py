#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Requires fping.
"""

from lxml import etree
import libvirt
import sys,os
import StringIO

debug = False
parser = etree.XMLParser(remove_blank_text=True)

def checkIP(IPAddr):
    retLevel = os.system("fping -r 1 -q %s 2>/dev/null" % IPAddr) >> 8
    return retLevel == 0

def macAddrFromdomObj(domObj):
    global parser
    xmldescription=domObj.XMLDesc(0)
    xmlDescFile=StringIO.StringIO(xmldescription)
    tree = etree.parse(xmlDescFile,parser)
    return tree.find("/devices/interface/mac").attrib["address"]

conn = libvirt.openReadOnly("qemu:///system")
if conn == None:
    print 'Failed to open connection to the hypervisor'
    sys.exit(1)

domains=conn.listDomainsID()
if debug:
    print >>sys.stderr,"domains = %s" % domains

messages=os.popen("grep 'dnsmasq.*DHCPACK' /var/log/daemon.log","r").readlines()
messages.reverse()

for domx in domains:
    try:
        domCurr = conn.lookupByID(domx)
    except:
        print 'Failed to find the domain with id=%d' % domx
        sys.exit(1)
    macaddr=macAddrFromdomObj(domCurr)
    if debug:
        print >>sys.stderr,"macaddr = %s" % macaddr
    ipData = []
    for lineStr in messages:
        line = lineStr.strip().split()
        if debug:
            print >>sys.stderr,"line = %s" % line
        if line[-1]==macaddr:
            ipData=line[-2:]
            if debug:
                print >>sys.stderr,"ipDate = %s" % ipData
            break
    if ipData and checkIP(ipData[0]):
        print "%s\t\t%s\t\t%s" % (domCurr.name(),ipData[0],ipData[1])
