from time import sleep
# from TmsPyApi import *

from ctypes import *
import os
from decoratorTools import stimer
# 定义函数返回错误代码
LIN_EX_SUCCESS = 0  # 函数执行成功
LIN_EX_ERR_NOT_SUPPORT = (-1)  # 适配器不支持该函数
LIN_EX_ERR_USB_WRITE_FAIL = (-2)  # USB写数据失败
LIN_EX_ERR_USB_READ_FAIL = (-3)  # USB读数据失败
LIN_EX_ERR_CMD_FAIL = (-4)  # 命令执行失败
LIN_EX_ERR_CH_NO_INIT = (-5)  # 该通道未初始化
LIN_EX_ERR_READ_DATA = (-6)  # LIN读数据失败
# LIN和校验模式
LIN_EX_CHECK_STD = 0  # 标准校验，不含PID
LIN_EX_CHECK_EXT = 1  # 增强校验，包含PID
LIN_EX_CHECK_USER = 2  # 自定义校验类型，需要用户自己计算并传入Check，不进行自动校验
LIN_EX_CHECK_NONE = 3  # 数据没有校验
LIN_EX_CHECK_ERROR = 4  # 接收数据校验错误

# 定义主从模式
LIN_EX_MASTER = 1
LIN_EX_SLAVE = 0

# 定义消息类型
LIN_EX_MSG_TYPE_UN = 0  # 未知类型
LIN_EX_MSG_TYPE_MW = 1  # 主机向从机发送数据
LIN_EX_MSG_TYPE_MR = 2  # 主机向从机读取数据
LIN_EX_MSG_TYPE_SW = 3  # 从机发送数据
LIN_EX_MSG_TYPE_SR = 4  # 从机接收数据
LIN_EX_MSG_TYPE_BK = 5  # 只发送BREAK信号，若是反馈回来的数据，表明只检测到BREAK信号
LIN_EX_MSG_TYPE_SY = 6  # 反馈回来的数据，表明检测到了BREAK，SYNC信号
LIN_EX_MSG_TYPE_ID = 7  # 反馈回来的数据，表明检测到了BREAK，SYNC，PID信号
LIN_EX_MSG_TYPE_DT = 8  # 反馈回来的数据，表明检测到了BREAK，SYNC，PID,DATA信号
LIN_EX_MSG_TYPE_CK = 9  # 反馈回来的数据，表明检测到了BREAK，SYNC，PID,DATA,CHECK信号

# 定义电压输出值
POWER_LEVEL_NONE = 0  # 不输出
POWER_LEVEL_1V8 = 1  # 输出1.8V
POWER_LEVEL_2V5 = 2  # 输出2.5V
POWER_LEVEL_3V3 = 3  # 输出3.3V
POWER_LEVEL_5V0 = 4  # 输出5.0V

# 根据系统自动导入对应的库文件，若没能识别到正确的系统，可以修改下面的源码

windll.LoadLibrary(os.getcwd() + "/libs/windows/x86_64/libusb-1.0.dll")
USB2XXXLib = windll.LoadLibrary(
    os.getcwd() + "/libs/windows/x86_64/USB2XXX.dll")


# windll.LoadLibrary("./libusb-1.0.dll")
# USB2XXXLib = windll.LoadLibrary("./USB2XXX.dll")


# Device info define
class DEVICE_INFO(Structure):
    _fields_ = [
        ("FirmwareName", c_char * 32),  # firmware name string
        ("BuildDate", c_char * 32),  # firmware build date and time string
        ("HardwareVersion", c_uint),  # hardware version
        ("FirmwareVersion", c_uint),  # firmware version
        ("SerialNumber", c_uint * 3),  # USB2XXX serial number
        ("Functions", c_uint)  # USB2XXX functions
    ]


class LIN_EX_MSG(Structure):
    _fields_ = [
        ("Timestamp", c_uint),  # 接收数据表示时间戳，单位为100us；发送数据表示数据发送后的延时时间，单位为毫秒
        ("MsgType", c_ubyte),  # 帧类型
        ("CheckType", c_ubyte),  # 数据校验类型
        ("DataLen", c_ubyte),  # 数据字节数
        ("Sync", c_ubyte),  # 同步数据，固定值0x55，若接收数据时该值不为0x55，那么数据有可能有错
        ("PID", c_ubyte),  # 接收数据表示带校验位的ID值，发送数据的时候只需要传递ID值即可，底层会自动计算校验位并添加上去
        ("Data", c_ubyte * 8),  # 接收或者发送的数据
        ("Check", c_ubyte),  # 根据CheckType校验类型进行计算的校验数据，发送数据时若不是自定义校验类型则底层会自动计算
        ("BreakBits", c_ubyte),  # 该帧的BRAK信号位数，有效值为10到26，若设置为其他值则默认为13位
        ("Reserve1", c_ubyte),  # 保留
    ]


# Scan device
def USB_ScanDevice(pDevHandle):
    return USB2XXXLib.USB_ScanDevice(pDevHandle)


# Open device
def USB_OpenDevice(DevHandle):
    return USB2XXXLib.USB_OpenDevice(DevHandle)


# Reset device
def USB_ResetDevice(DevHandle):
    return USB2XXXLib.USB_ResetDevice(DevHandle)


# Get USB2XXX infomation
def DEV_GetDeviceInfo(DevHandle, pDevInfo, pFunctionStr):
    return USB2XXXLib.DEV_GetDeviceInfo(DevHandle, pDevInfo, pFunctionStr)


# Close device
def USB_CloseDevice(DevHandle):
    return USB2XXXLib.USB_CloseDevice(DevHandle)


def DEV_EraseUserData(DevHandle):
    return USB2XXXLib.DEV_EraseUserData(DevHandle)


def DEV_WriteUserData(DevHandle, OffsetAddr, pWriteData, DataLen):
    return USB2XXXLib.DEV_WriteUserData(DevHandle, OffsetAddr, pWriteData, DataLen)


def DEV_ReadUserData(DevHandle, OffsetAddr, pReadData, DataLen):
    return USB2XXXLib.DEV_ReadUserData(DevHandle, OffsetAddr, pReadData, DataLen)


def DEV_SetPowerLevel(DevHandle, PowerLevel):
    return USB2XXXLib.DEV_SetPowerLevel(DevHandle, PowerLevel)


def DEV_GetTimestamp(DevHandle, BusType, pTimestamp):
    return USB2XXXLib.DEV_GetTimestamp(DevHandle, BusType, pTimestamp)


def DEV_ResetTimestamp(DevHandle):
    return USB2XXXLib.DEV_ResetTimestamp(DevHandle)


"""
____________________________________
"""


# 设置从模式下ID操作模式


def LIN_EX_Init(DevHandle, LINIndex, BaudRate, MasterMode):
    return USB2XXXLib.LIN_EX_Init(DevHandle, LINIndex, BaudRate, MasterMode)


def LIN_EX_MasterSync(DevHandle, LINIndex, pInMsg, pOutMsg, MsgLen):
    return USB2XXXLib.LIN_EX_MasterSync(DevHandle, LINIndex, pInMsg, pOutMsg, MsgLen)


def LIN_EX_MasterWrite(DevHandle, LINIndex, PID, pData, DataLen, CheckType):
    return USB2XXXLib.LIN_EX_MasterWrite(DevHandle, LINIndex, PID, pData, DataLen, CheckType)


def LIN_EX_MasterBreak(DevHandle, LINIndex):
    return USB2XXXLib.LIN_EX_MasterBreak(DevHandle, LINIndex)


def LIN_EX_MasterRead(DevHandle, LINIndex, PID, pData):
    return USB2XXXLib.LIN_EX_MasterRead(DevHandle, LINIndex, PID, pData)


def LIN_EX_SlaveGetIDMode(DevHandle, LINIndex, pLINMsg, MsgLen):
    return USB2XXXLib.LIN_EX_SlaveGetIDMode(DevHandle, LINIndex, pLINMsg, MsgLen)


def LIN_EX_SlaveSetIDMode(DevHandle, LINIndex, pLINMsg, MsgLen):
    return USB2XXXLib.LIN_EX_SlaveSetIDMode(DevHandle, LINIndex, pLINMsg, MsgLen)


def LIN_EX_SlaveGetData(DevHandle, LINIndex, pLINMsg):
    return USB2XXXLib.LIN_EX_SlaveGetData(DevHandle, LINIndex, pLINMsg)


def LIN_EX_CtrlPowerOut(DevHandle, State):
    return USB2XXXLib.LIN_EX_CtrlPowerOut(DevHandle, State)


def LIN_EX_GetVbatValue(DevHandle, pBatValue):
    return USB2XXXLib.LIN_EX_GetVbatValue(DevHandle, pBatValue)


def LIN_EX_MasterStartSch(DevHandle, LINIndex, pLINMsg, MsgLen):
    return USB2XXXLib.LIN_EX_MasterStartSch(DevHandle, LINIndex, pLINMsg, MsgLen)


def LIN_EX_MasterStopSch(DevHandle, LINIndex):
    return USB2XXXLib.LIN_EX_MasterStopSch(DevHandle, LINIndex)


def LIN_EX_MasterGetSch(DevHandle, LINIndex, pLINMsg):
    return USB2XXXLib.LIN_EX_MasterGetSch(DevHandle, LINIndex, pLINMsg)


# ERROR_TYPE = [
#     "函数执行成功",
#     "适配器不支持该函数",
#     "USB写数据失败",
#     "USB读数据失败",
#     "命令执行失败",
#     "该通道未初始化",
#     "LIN读数据失败"
# ]

LINMasterIndex = 0
LINSlaveIndex = 1
DevHandles = (c_uint * 20)()
LINOutMsg = LIN_EX_MSG()
LINMsg = LIN_EX_MSG()


class TmsFunction:
    def __init__(self) -> None:
        pass

    @stimer
    def tmsInit(self) -> bool:
        return False if (USB_ScanDevice(byref(DevHandles)) and USB_OpenDevice(DevHandles[0])) == 0 else True

    @stimer
    def tmsLinMasterInit(self):
        return False if LIN_EX_Init(DevHandles[0], LINMasterIndex, 19200, LIN_EX_MASTER) else True

    @stimer
    def tmsBreak(self):
        LINMsg.MsgType = LIN_EX_MSG_TYPE_BK
        LINMsg.Timestamp = 10
        ret = LIN_EX_MasterSync(
            DevHandles[0], LINMasterIndex, byref(LINMsg), byref(LINOutMsg), 1)
        sleep(0.01)
        return -1 if ret != 1 else 1

    @stimer
    def linWrite(self, frameId: int, data: list):
        data_buffer = (c_byte * len(data))(*data)
        LINMsg.MsgType = LIN_EX_MSG_TYPE_MW
        LINMsg.Timestamp = 0
        LINMsg.PID = frameId
        LINMsg.CheckType = LIN_EX_CHECK_EXT if frameId != 0x3c else LIN_EX_CHECK_STD
        LINMsg.DataLen = 8
        for i in range(0, LINMsg.DataLen):
            LINMsg.Data[i] = data_buffer[i]
        ret = LIN_EX_MasterSync(
            DevHandles[0], LINMasterIndex, byref(LINMsg), byref(LINOutMsg), 1)
        if ret != 1:
            print("LIN ID[0x%02X] 发送失败!" % LINMsg.PID)
            exit()
        else:
            print("M2S", "[0x%02X] " % LINOutMsg.PID, end='')
            for i in range(LINOutMsg.DataLen):
                print("0x%02X " % LINOutMsg.Data[i], end='')
            print("")

    @stimer
    def linRead(self, frameId: int):
        r = []
        LINMsg.MsgType = LIN_EX_MSG_TYPE_MR
        LINMsg.Timestamp = 0
        LINMsg.PID = frameId
        ret = LIN_EX_MasterSync(
            DevHandles[0], LINMasterIndex, byref(LINMsg), byref(LINOutMsg), 1)
        if ret != 1:
            print("读取失败!")
            exit()
        else:
            print("S2M", "[0x%02X] " % LINOutMsg.PID, end='')
            for i in range(LINOutMsg.DataLen):
                print("0x%02X " % LINOutMsg.Data[i], end='')
                r.append(LINOutMsg.Data[i])
            print("")
        return r


if __name__ == "__main__":
    p = TmsFunction()
    print(p.tmsInit())
    print(p.tmsLinMasterInit())
    print(p.tmsBreak())
