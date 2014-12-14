# -*- coding: utf-8 -*-
"""
Created on Fri Nov 28 13:46:19 2014

@author: pbustos
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Update a simple plot as rapidly as possible to measure speed.
"""

from PySide import QtGui, QtCore
#from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import blescan
import sys
import bluetooth._bluetooth as bluez


class BTPlotter():
    nextColor=0
    def __init__(self,app):
        self.app = app
        pg.setConfigOptions(antialias=True)        
        self.win = pg.GraphicsWindow(title="Basic plotting examples")
        self.win.resize(800,800)
        self.win.setWindowTitle('SmartPolyTech Beacon System')
        
        self.p = self.win.addPlot(title='RSSI graph')
        self.graphView = self.win.addViewBox(row=1,col=0)
        #self.graphView.setLimits(xMin=-5, xMax=5, yMin = -5, yMax=5)
        self.graphView.setAspectLocked()
        self.graphView.setRange(rect=QtCore.QRectF(-6,6,12,-12))
       
        box = QtGui.QGraphicsRectItem(-10, 5, 20, -10)
        box.setPen(pg.mkPen("w"))
        box.setBrush(pg.mkBrush(None))
        self.graphView.addItem(box)
        self.graphView.show()
        self.graph = pg.GraphItem()
        self.graphView.addItem(self.graph)
        
        self.bufferLength = 20
        self.p.setRange(QtCore.QRectF(0, 0, self.bufferLength, 100)) 
        self.p.setLabel('bottom', 'Samples')
        self.p.setLabel('left', 'Signal Strength')
        self.p.setAutoVisible(y=True)
        
        #cross hair
        try:
            dev_id = 0
            self.sock = bluez.hci_open_dev(dev_id)
            print "ble thread started"
        except:
            print "error accessing bluetooth device..."
            sys.exit(1)
        
        #Variables
        self.lastTime = time()
        self.fps = None
        
        #Timers
        self.timerBluetooth = QtCore.QTimer()
        self.timerBluetooth.timeout.connect(self.updateBluetooth)
        self.timerBluetooth.start(300)       
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.compute)
        self.timer.start(100)
       
        #self.p.scene().sigMouseMoved.connect(self.mouseMoved)
        
        self.signalList = {}
        self.curveList = {}

    def compute(self):
        #self.timeElapsed()
        #self.app.processEvents()  ## force complete redraw for every plot
        pass
    
#    def updateSpace(self, poseList):
#
#        ## Define positions of nodes
#        poses = np.array()
#        edges = np.array()
#        np.append(poses, [belX,belY])
#        i=1
#        for p in poseList:
#            np.append(poses, p)
#            e = [0,i]
#            np.append(edges, e)            
#            i += 1
#    
#       self.graph.setData(pos=poses, adj=edges)
#    
    def updateBluetooth(self): 
        returnedList = blescan.parse_events(self.sock, 1)
        for beacon in returnedList:
            words = beacon.split(',')
            mac = words[0]
            uid = words[1]
            major = words[2]
            minor = words[3]
            power = words[4]
            rssi = words[5]
            print mac, rssi, minor
            #print "dict lenght" ,len(self.signalList)
            
            if mac not in self.signalList:
                #self.signalList[mac] = np.zeros(self.bufferLength,'f')
                self.signalList[mac] = np.zeros(0,'f')
                self.curveList[mac] = self.p.plot(pen=QtGui.QPen(pg.intColor(self.nextColor)))
                self.nextColor += 1
            
            s = self.signalList[mac]
            val = 100 + float(rssi)
            if s.size < self.bufferLength:
                s = np.append(s,val)
#                if s.size > 4:
#                     s[-1] = self.runningMeanFast(s,3)[0]             
                print "append" , val
            else:      
                s = np.roll(s,-1)
                s[-1] = val         
#                s[-1] = self.runningMeanFast(s,3)[0]             
        
            self.curveList[mac].setData(s)       
            self.signalList[mac] = s
            self.timeElapsed()
            self.app.processEvents()  ## force complete redraw for every plot
        
    def runningMeanFast(self,x, N):
        return np.convolve(x, np.ones((N,))/N)[(N-1):] 
        
    def mouseMoved(self,pos):
        if self.p.sceneBoundingRect().contains(pos):
            mousePoint = self.p.vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < 100:
                self.label.setText("<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,<span style='color: green'>y2=%0.1f</span>" % (mousePoint.x(), 50,70))
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())    
    
    def timeElapsed(self):
        now = time()
        dt = now - self.lastTime
        self.lastTime = now
        if self.fps is None:
            self.fps = 1.0/dt
        else:
            s = np.clip(dt*3., 0, 1)
            self.fps = self.fps * (1-s) + (1.0/dt) * s
        self.p.setTitle('%0.2f fps' % self.fps)
    
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app = QtGui.QApplication([])   
        bt = BTPlotter(app)
        QtGui.QApplication.instance().exec_()
