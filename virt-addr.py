#!/usr/bin/env python

from lxml import etree
import libvirt
import sys,os
import StringIO

parser = etree.XMLParser(remove_blank_text=True)

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

messages=os.popen("grep 'dnsmasq.*DHCPACK' /var/log/messages","r").readlines()
messages.reverse()

for domx in domains:
    try:
        domCurr = conn.lookupByID(domx)
    except:
        print 'Failed to find the domain with id=%d' % domx
        sys.exit(1)
    macaddr=macAddrFromdomObj(domCurr)
    ipData = []
    for lineStr in messages:
        line = lineStr.strip().split()
        if line[-1]==macaddr:
            ipData=line[-2:]
            break
    if ipData:
        print "%s\t\t%s\t\t%s" % (domCurr.name(),ipData[-1],ipData[-2])    