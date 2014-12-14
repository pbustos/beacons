# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys
import bluetooth._bluetooth as bluez
import re


dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print "ble thread started"

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

with open("datosT.txt","w") as file, open("datosIBKT.txt","w") as fileIBK:
    cont = 0
    while cont < 100:
        returnedList = blescan.parse_events(sock, 1)
        print "----------"
        for beacon in returnedList:
            print beacon
            words = beacon.split(',')
            if words[3] == '1734':
                print "REMOTTE", cont, ": ", words[3], words[4], words[5]
                file.write(str(words[3]))
                file.write(' ')
                file.write(str(words[4]))
                file.write(' ')
                file.write(str(words[5]))
                file.write(' ')
                file.write('\n')
                cont = cont+1;
                
            if words[3] == '1':
                print "IBK ", cont, ": ", words[3], words[4], words[5]
                fileIBK.write(str(words[3]))
                fileIBK.write(' ')
                fileIBK.write(str(words[4]))
                fileIBK.write(' ')
                fileIBK.write(str(words[5]))
                fileIBK.write(' ')
                fileIBK.write('\n')
                cont = cont+1;
            
