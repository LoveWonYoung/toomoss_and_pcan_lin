import os
import time
import PLinApi
from ctypes import *
from decoratorTools import *


class LinBus:

    def __init__(self, baudrate):

        self.bus = PLinApi.PLinApi()
        if self.bus is False:
            raise Exception("PLIN API Not Loaded")

        self.hClient = PLinApi.HLINCLIENT(0)
        self.hHw = PLinApi.HLINHW(0)
        self.HwMode = PLinApi.TLIN_HARDWAREMODE_MASTER
        self.HwBaudrate = c_ushort(baudrate)

        result = self.bus.RegisterClient("Embed Master", None, self.hClient)
        if result is not PLinApi.TLIN_ERROR_OK:
            raise Exception("Error registering client")

        self.hHw = PLinApi.HLINHW(1)
        result = self.bus.ConnectClient(self.hClient, self.hHw)
        if result is not PLinApi.TLIN_ERROR_OK:
            raise Exception("Error connecting client")

        result = self.bus.InitializeHardware(
            self.hClient, self.hHw, PLinApi.TLIN_HARDWAREMODE_MASTER, self.HwBaudrate)
        if result is not PLinApi.TLIN_ERROR_OK:
            raise Exception("Error initialising hardware")

        result = self.bus.RegisterFrameId(self.hClient, self.hHw, 0x3C, 0x3D)
        if result is not PLinApi.TLIN_ERROR_OK:
            raise Exception("Error registering frame id client")

        self.bus.SetClientFilter(
            self.hClient, self.hHw, c_uint64(0xFFFFFFFFFFFFFFFF))

    def getFormattedRcvMsg(self, msg):
        if msg.Type != PLinApi.TLIN_MSGTYPE_STANDARD.value:
            if msg.Type == PLinApi.TLIN_MSGTYPE_BUS_SLEEP.value:
                strTemp = 'Bus Sleep status message'
            elif msg.Type == PLinApi.TLIN_MSGTYPE_BUS_WAKEUP.value:
                strTemp = 'Bus WakeUp status message'
            elif msg.Type == PLinApi.TLIN_MSGTYPE_AUTOBAUDRATE_TIMEOUT.value:
                strTemp = 'Auto-baudrate Timeout status message'
            elif msg.Type == PLinApi.TLIN_MSGTYPE_AUTOBAUDRATE_REPLY.value:
                strTemp = 'Auto-baudrate Reply status message'
            elif msg.Type == PLinApi.TLIN_MSGTYPE_OVERRUN.value:
                strTemp = 'Bus Overrun status message'
            elif msg.Type == PLinApi.TLIN_MSGTYPE_QUEUE_OVERRUN.value:
                strTemp = 'Queue Overrun status message'
            else:
                strTemp = 'Non standard message'
            return strTemp
        # format Data field as string
        dataStr = ""
        for i in range(msg.Length):
            dataStr = str.format("{0}{1} ", dataStr, hex(msg.Data[i]))
        # remove ending space
        dataStr = dataStr[:-1]
        # format Error field as string
        error = ""
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_CHECKSUM:
            error = error + 'Checksum,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_GROUND_SHORT:
            error = error + 'GroundShort,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_ID_PARITY_BIT_0:
            error = error + 'IdParityBit0,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_ID_PARITY_BIT_1:
            error = error + 'IdParityBit1,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_INCONSISTENT_SYNCH:
            error = error + 'InconsistentSynch,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_OTHER_RESPONSE:
            error = error + 'OtherResponse,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_SLAVE_NOT_RESPONDING:
            error = error + 'SlaveNotResponding,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_SLOT_DELAY:
            error = error + 'SlotDelay,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_TIMEOUT:
            error = error + 'Timeout,'
        if msg.ErrorFlags & PLinApi.TLIN_MSGERROR_VBAT_SHORT:
            error = error + 'VBatShort,'
        if msg.ErrorFlags == 0:
            error = 'O.k. '
        # remove ending comma
        error = error[:-1]
        # format message
        # print(dataStr)

        return ["Length: {} Id:{} Data: {:<40} Time: {} Error: {}".format(msg.Length, hex(msg.FrameId), dataStr,
                                                                          msg.TimeStamp,
                                                                          error),
                [int(x, 16) for x in dataStr.split(' ')], msg.ErrorFlags]

    @stimer
    def linWrite(self, frameId, data):
        data_buffer = (c_ubyte * len(data))(*data)
        pMsg = PLinApi.TLINMsg()
        pMsg.Direction = PLinApi.TLIN_DIRECTION_PUBLISHER
        pMsg.Length = c_ubyte(8)
        pMsg.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_CLASSIC if frameId == 0x3c else PLinApi.TLIN_CHECKSUMTYPE_ENHANCED
        pMsg.Data = data_buffer

        npid = c_ubyte(frameId)
        self.bus.GetPID(npid)
        pMsg.FrameId = c_ubyte(npid.value)
        self.bus.CalculateChecksum(pMsg)
        r = self.bus.Write(self.hClient, self.hHw, pMsg)
        return self.rec()
        # print(r)

    @stimer
    def linRead(self, frameId):
        p2Msg = PLinApi.TLINMsg()
        p2Msg.Direction = PLinApi.TLIN_DIRECTION_SUBSCRIBER
        p2Msg.Length = c_ubyte(8)
        p2Msg.ChecksumType = PLinApi.TLIN_CHECKSUMTYPE_CLASSIC \
            if frameId == 0x3c or frameId == 0x3d \
            else PLinApi.TLIN_CHECKSUMTYPE_ENHANCED

        npid = c_ubyte(frameId)
        self.bus.GetPID(npid)
        p2Msg.FrameId = c_ubyte(npid.value)
        self.bus.CalculateChecksum(p2Msg)
        self.bus.Write(self.hClient, self.hHw, p2Msg)
        return self.rec()[1]

    @stimer
    def rec(self):
        listMsg = []
        pRcvMsg = PLinApi.TLINRcvMsg()
        linResult = self.bus.Read(self.hClient, pRcvMsg)
        if linResult == PLinApi.TLIN_ERROR_OK:
            # append received message to message list
            listMsg.append(self.getFormattedRcvMsg(pRcvMsg))
            # print(self.getFormattedRcvMsg(pRcvMsg))
        # print(f"读取信息，错误码{linResult}")

        for msg in listMsg:
            print(msg[0])
            return msg

    @stimer
    def pcanBreak(self):
        ret = -1
        for _ in range(10):
            try:
                if self.linWrite(0x3c, [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88])[2] == 0:
                    time.sleep(0.5)
                    ret = 1
                    return ret
            except TypeError:
                time.sleep(0.5)
                pass
        return ret


if __name__ == "__main__":
    c = LinBus(19200)
    c.pcanBreak()
    c.linWrite(0x3c, hexStringToByteList("7f 03 22 f1 89 ff ff ff"))
    for _ in range(3):
        c.linRead(0x3d)
