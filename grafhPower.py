# -*- coding: utf-8 -*-
"""
Created on Fri Nov 28 13:32:47 2014

@author: pbustos
"""

import pyqtgraph as pg
import numpy as np
import blescan
import sys
import bluetooth._bluetooth as bluez

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print "ble thread started"

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

x = 0
plotWidget = pg.plot(title="Beacons")
while True:
    returnedList = blescan.parse_events(sock, 1)
    for beacon in returnedList:
        print beacon
        words = beacon.split(',')
        if words[3] == '1':      
            x = x+1
            plotWidget.plot(x, 100 - int(words[5]), pen=(1,3))