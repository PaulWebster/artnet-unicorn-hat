# Art-Net protocol for Pimoroni Unicorn Hat and Pimoroni Mote
# Open Pixel Control protocol for Pimoroni Unicorn Hat and Pimoroni Mote
# License: MIT
from __future__ import print_function

# Do not enable more than one device
# #note# done this so that some imports can be skipped because it was causing problems on my system and needed root
PimUnicorn = False
PimMote = True

SupportArtNet = False

if PimUnicorn:
    import unicornhat as unicorn
if PimMote:
    from mote import Mote
    
from twisted.internet import protocol, endpoints
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import numpy as np

import sys
if sys.version_info[0] < 3:
    oldPython = True
else:
    oldPython = False

if PimUnicorn:
    # 8x8 grid
    x_max = 8
    y_max = 8

if PimMote:
    mote = Mote()
    # #note# Hard-coded as a 4 (y) channels (sticks) each of 16 (x) (LEDs) - but this should be made more flexible in future
    x_max = 16
    y_max = 4

    
# Adjust the LED brightness as needed.
if PimUnicorn:
    unicorn.brightness(0.5)
if PimMote:
    # Device initialisation
    y = 1
    while (y <= y_max):
        mote.configure_channel(y, x_max, False)
        y +=1

    
class ArtNet(DatagramProtocol):

    # def datagramReceived(self, data, (host, port)): - change to Python3 compatible ... but untested!
    def datagramReceived(self, data, source):
        host, port = source
        if ((len(data) > 18) and (data[0:8] == "Art-Net\x00")):
            if oldPython:
                rawbytes = map(ord, data) ## need to work on this to make it safe for Python 2 and 3
            else:
                rawbytes = data ## "map" changed in Python3 - in theory list(map()) should have worked but did not
                
            opcode = rawbytes[8] + (rawbytes[9] << 8)
            protocolVersion = (rawbytes[10] << 8) + rawbytes[11]
            if ((opcode == 0x5000) and (protocolVersion >= 14)):
                sequence = rawbytes[12]
                physical = rawbytes[13]
                sub_net = (rawbytes[14] & 0xF0) >> 4
                universe = rawbytes[14] & 0x0F
                net = rawbytes[15]
                rgb_length = (rawbytes[16] << 8) + rawbytes[17]
                # print("seq %d phy %d sub_net %d uni %d net %d len %d" % \
                # (sequence, physical, sub_net, universe, net, rgb_length))
                idx = 18
                x = 0
                y = 0
                while ((idx < (rgb_length+18)) and (y < y_max)):
                    r = rawbytes[idx]
                    idx += 1
                    g = rawbytes[idx]
                    idx += 1
                    b = rawbytes[idx]
                    idx += 1
                    if PimUnicorn:
                        unicorn.set_pixel(x, y, r, g, b)
                    if PimMote:
                        mote.set_pixel(y+1, x, r, g, b)
                    x += 1
                    if (x >= x_max):
                        x = 0
                        y += 1

                if PimUnicorn:
                    unicorn.show()
                if PimMote:
                    mote.show()

class OPC(protocol.Protocol):
    # Parse Open Pixel Control protocol. See http://openpixelcontrol.org/
    parseState = 0
    pktChannel = 0
    pktCommand = 0
    pktLength = 0
    pktCount = 0
    pixelCount = 0
    pixelLimit = 0
    lastSet = []    # Hold copy of last set of LEDs sent
    MAX_LEDS = x_max * y_max

    def dataReceived(self, data):
        if oldPython:
            rawbytes = map(ord, data) ## need to work on this to make it safe for Python 2 and 3
        else:
            rawbytes = data ## "map" changed in Python3 - in theory list(map()) should have worked but did not

        OPC.pktCount += 1
        #print("len(rawbytes) %d" % len(rawbytes))
        #print("Packet count %d" % OPC.pktCount)
        #print(rawbytes)
        
        if (np.array_equal(OPC.lastSet, rawbytes)):
            # New data is same as last so skip it to save work since LEDs retain last value
            i = len(rawbytes)    # Set to force skip of processing below
            # print("Same data as before")
        else:
            OPC.lastSet = rawbytes    # Assume this set will be sent
            i = 0    # Force this set to be processed
       
        while (i < len(rawbytes)):
            #print("parseState %d i %d" % (OPC.parseState, i))
            if (OPC.parseState == 0):   # get OPC.pktChannel
                OPC.pktChannel = rawbytes[i]
                i += 1
                OPC.parseState += 1
            elif (OPC.parseState == 1): # get OPC.pktCommand
                OPC.pktCommand = rawbytes[i]
                i += 1
                OPC.parseState += 1
            elif (OPC.parseState == 2): # get OPC.pktLength.highbyte
                OPC.pktLength = rawbytes[i] << 8
                i += 1
                OPC.parseState += 1
            elif (OPC.parseState == 3): # get OPC.pktLength.lowbyte
                OPC.pktLength |= rawbytes[i]
                i += 1
                OPC.parseState += 1
                OPC.pixelCount = 0
                OPC.pixelLimit = min(3*OPC.MAX_LEDS, OPC.pktLength)
                #print("OPC.pktChannel %d OPC.pktCommand %d OPC.pktLength %d OPC.pixelLimit %d" % \
                #    (OPC.pktChannel, OPC.pktCommand, OPC.pktLength, OPC.pixelLimit))
                if (OPC.pktLength > 3*OPC.MAX_LEDS):
                    print("Received pixel packet exeeds size of buffer! Data discarded.")
                if (OPC.pixelLimit == 0):
                    OPC.parseState = 0
            elif (OPC.parseState == 4):
                copyBytes = min(OPC.pixelLimit - OPC.pixelCount, len(rawbytes) - i)
                if (copyBytes > 0):
                    OPC.pixelCount += copyBytes
                    #print("OPC.pixelLimit %d OPC.pixelCount %d copyBytes %d" % \
                    #        (OPC.pixelLimit, OPC.pixelCount, copyBytes))
                    if ((OPC.pktCommand == 0) and (OPC.pktChannel <= 1)):
                        x = 1
                        y = 1
                        iLimit = i + copyBytes
                        while ((i < iLimit) and (y <= y_max)):
                            #print("i %d" % (i))
                            r = rawbytes[i]
                            i += 1
                            g = rawbytes[i]
                            i += 1
                            b = rawbytes[i]
                            i += 1
                            #print("x %d y %d r %d g %d b %d" % (x,y,r,g,b))
                            if PimUnicorn:
                                unicorn.set_pixel(x-1, y-1, r, g, b)
                            if PimMote:
                                mote.set_pixel(y, x-1, r, g, b)

                            x += 1
                            if (x > x_max):
                                x = 1
                                y += 1

                        if (OPC.pixelCount >= OPC.pixelLimit):
                            if PimUnicorn:
                                unicorn.show()
                            if PimMote:
                                # print("Showing")
                                mote.show()
                                # print("Shown")
                    else:
                        i += copyBytes
                    if (OPC.pixelCount == OPC.pktLength):
                        OPC.parseState = 0
                    else:
                        OPC.parseState += 1
            elif (OPC.parseState == 5):
                discardBytes = min(OPC.pktLength - OPC.pixelLimit, len(rawbytes) - i)
                print("discardBytes %d" % (discardBytes))
                OPC.pixelCount += discardBytes
                i += discardBytes
                if (OPC.pixelCount >= OPC.pktLength):
                    OPC.parseState = 0
                if (discardBytes == 0):
                    OPC.parseState = 0
                    print("Unexpected 0 bytes to discard")
            else:
                print("Invalid OPC.parseState %d" % (OPC.parseState))


class OPCFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return OPC()

if SupportArtNet:
    reactor.listenUDP(6454, ArtNet())
    
endpoints.serverFromString(reactor, "tcp:7890").listen(OPCFactory())
reactor.run()
