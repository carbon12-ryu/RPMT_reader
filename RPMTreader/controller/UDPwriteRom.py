import socket
from datetime import datetime, timedelta, timezone

class UDPwriteRom:
  def __init__(self, TARGET_IP, PORT):
    self.ip = TARGET_IP
    self.port = PORT
    self.cmd_dict = {
      "writeMode"    : "ff 80 01 01 00 00 01 00  5b", #NEUNETを書き込みモードにする
      "setTime"      : "ff 80 01 07 00 00 01 90", # 時刻書き込み (アドレス: 0x0190, 長さ: 7 byte = 0x07)
      "setTimeLLD"      : "ff 80 01 08 00 00 01 98", # LLD, TMH, TML書き込み (アドレス: 0x0198, 長さ: 8 byte = 0x08)
      "startMes"      : "ff 80 01 02 00 00 01 86  00 00", # 測定モード (アドレス: 0x0186, 長さ: 2 byte = 0x02)
    }


  def sendUDP(self, cmd_str):
    cmd = bytes.fromhex(cmd_str)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      sock.settimeout(1)
      sock.sendto(cmd, (self.ip, self.port))
      reply, addr = sock.recvfrom(1024)
    rbcp_header = reply[:8]
    data_body = reply[8:]
    return data_body
  
  
  ### 時間書き換え (0x0190) ###
  def setTime(self):
    utc_time = datetime.now(timezone.utc)
    base_time = datetime(2008, 1, 1, 0, 0, 0, tzinfo=timezone.utc) # 基準時刻
    total_elapsed = (utc_time - base_time).total_seconds() # 経過秒
    S = int(total_elapsed) # S（整数秒）
    SS = int((total_elapsed - S) * 32768) # SS（32.768kHz）
    US = int(((total_elapsed - S) - (SS / 32768.0)) / 0.000000025 ) # US（40MHz = 25ns）
    US = max(0, min(US, 2047))

    b0 = (S >> 22) & 0xFF
    b1 = (S >> 14) & 0xFF
    b2 = (S >> 6) & 0xFF
    b3 = ((S & 0x3F) << 2) | ((SS >> 13) & 0x03)
    b4 = (SS >> 5) & 0xFF
    b5 = ((SS & 0x1F) << 3) | ((US >> 8) & 0x07)
    b6 = US & 0xFF

    time_bytes = bytes([b0, b1, b2, b3, b4, b5, b6])
    time_str = ''.join(f'{b:02x}' for b in [b0, b1, b2, b3, b4, b5, b6])
    
    writeMode = self.sendUDP(self.cmd_dict["writeMode"])
    result = self.sendUDP(self.cmd_dict["setTime"] + time_str)
    return None
  
  ### LLD, time_low, time_high###
  def setTimeLLD(self, LLD, time_low, time_high):
    text = (
        f"{LLD:04x}"
        f"{time_high:06x}"
        f"{time_low:06x}"
    )
    writeMode = self.sendUDP(self.cmd_dict["writeMode"])
    res = self.sendUDP(self.cmd_dict["setTimeLLD"] + text)
    return None
  
  
  def startMes(self):
    res = self.sendUDP(self.cmd_dict["startMes"])
    return None
  
# TARGET_IP = "192.168.0.16"
# PORT = 0x1234
# UDPwriteRom(TARGET_IP, PORT).setTime()
# UDPwriteRom(TARGET_IP, PORT).setTimeLLD(0, 0, 160000)
