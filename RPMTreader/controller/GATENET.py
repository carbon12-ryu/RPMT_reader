import socket
import time

from .UDPreadRom import UDPreadRom
from .UDPwriteRom import UDPwriteRom

class GATENET:
  def __init__(self):
    self.IP = "192.168.0.15"
    self.UDPport = 0x1234
    self.TCPport = 23
    self.GatenetUR = UDPreadRom(self.IP, self.UDPport)
    self.GatenetUW = UDPwriteRom(self.IP, self.UDPport)
    
  def config(self):
    text = self.GatenetUR.getAll()
    print(text)
    return None
  
  def setTime(self):
    self.GatenetUW.setTime()
    return None
  
  def setTimeLLD(self, LLD, time_low, time_hi):
    self.GatenetUW.setTimeLLD(LLD, time_low, time_hi)