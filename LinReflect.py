import TmsFunc3
import time
from ctypes import *
from LinBus import LinBus
from decoratorTools import *


class LinFunction:
    def __init__(self) -> None:
        try:
            self.com = LinBus(19200)
            print("pcan 连接成功")
        except Exception:
            print("pcan 连接失败，连接图莫斯")
            self.com = TmsFunc3.TmsFunction()
            if not self.com.tmsInit():
                print("图莫斯连接失败")
            if not self.com.tmsLinMasterInit():
                print("图莫斯初始化失败")
                exit()

    @stimer
    def comBreak(self):
        r = 0
        if hasattr(self.com, "tmsBreak"):
            r = self.com.tmsBreak()
        else:
            r = self.com.pcanBreak()
        return r


if __name__ == "__main__":
    lin = LinFunction()
    if lin.comBreak():
        for _ in range(10):
            lin.com.linWrite(0x3c, [1] * 8)
            lin.com.linRead(0x3d)
