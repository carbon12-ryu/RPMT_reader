import socket
from datetime import datetime, timedelta


# UDPでメモリー各領域の読み出し命令文
cmd_histogram = bytes.fromhex("ff c0 00 40 00 00 00 00") # ヒストグラム ROM 用バッファ (アドレス: 0x0000, 長さ: 64 byte = 0x40)
cmd_mod_info = bytes.fromhex("ff c0 00 40 00 00 00 40") # モジュール情報 ROM 用バッファ (アドレス: 0x0040, 長さ: 64 byte = 0x40)
cmd_config = bytes.fromhex("ff c0 00 20 00 00 00 80") # モジュール現設定情報読み出し領域 (アドレス: 0x0080, 長さ: 32 byte = 0x20)
cmd_readwrite = bytes.fromhex("ff c0 00 01 00 00 01 00") # ROM 読み出し、書き込み指令領域 (アドレス: 0x0100, 長さ: 1 byte = 0x01)
cmd_control = bytes.fromhex("ff c0 00 08 00 00 01 80") # メモリ使用制御領域 (アドレス: 0x0180, 長さ: 8 byte = 0x08)
cmd_gatenet_status = bytes.fromhex("ff c0 00 03 00 00 01 88") # ステータスレジスタ ＃＃GATENET用 (アドレス: 0x0188, 長さ: 3 byte = 0x03)
cmd_gatenet_pulse = bytes.fromhex("ff c0 00 05 00 00 01 8b") # パルス ID カウンター ＃＃GATENET用 (アドレス: 0x018B, 長さ: 5 byte = 0x05)
cmd_gatenet_time = bytes.fromhex("ff c0 00 07 00 00 01 90") # 装置時刻相対カウンター ＃＃GATENET用 (アドレス: 0x0190, 長さ: 7 byte = 0x07)
cmd_sitcp_lld = bytes.fromhex("ff c0 00 08 00 00 01 98") # SiTCP 側の LLD, 時間制限 (アドレス: 0x0198, 長さ: 8 byte = 0x08)

class Status:
  def __init__(self, TARGET_IP, PORT):
    self.ip = TARGET_IP
    self.port = PORT
    self.cmd_dict = {
      "histgram"      : "ff c0 00 40 00 00 00 00", # ヒストグラム ROM 用バッファ (アドレス: 0x0000, 長さ: 64 byte = 0x40)
      "moduleInfo"    : "ff c0 00 40 00 00 00 40", # モジュール情報 ROM 用バッファ (アドレス: 0x0040, 長さ: 64 byte = 0x40)
      "moduleConf"    : "ff c0 00 20 00 00 00 80", # モジュール現設定情報読み出し領域 (アドレス: 0x0080, 長さ: 32 byte = 0x20)
      "readWrite"     : "ff c0 00 01 00 00 01 00", # ROM 読み出し、書き込み指令領域 (アドレス: 0x0100, 長さ: 1 byte = 0x01)
      "controll"      : "ff c0 00 08 00 00 01 80", # メモリ使用制御領域 (アドレス: 0x0180, 長さ: 8 byte = 0x08)
      "gatenetStatus" : "ff c0 00 03 00 00 01 88", # ステータスレジスタ ＃＃GATENET用 (アドレス: 0x0188, 長さ: 3 byte = 0x03)
      "gatenetPulse"  : "ff c0 00 05 00 00 01 8b", # パルス ID カウンター ＃＃GATENET用 (アドレス: 0x018B, 長さ: 5 byte = 0x05)
      "gatenetTime"   : "ff c0 00 07 00 00 01 90", # 装置時刻相対カウンター ＃＃GATENET用 (アドレス: 0x0190, 長さ: 7 byte = 0x07)
      "sitcpLLD"      : "ff c0 00 08 00 00 01 98", # SiTCP 側の LLD, 時間制限 (アドレス: 0x0198, 長さ: 8 byte = 0x08)
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
  
  def getAll(self):
    # text1 = self.histgram()
    # text2 = self.moduleInfo()
    # text3 = self.moduleConf()
    # text4 = self.readWrite()
    # text5 = self.controll()
    # text6 = self.gatenetStatus()
    # text7 = self.gatenetPulse()
    # text8 = self.gatenetTime()
    # text9 = self.sitcpLLD()
    texts = [
      self.histgram()[0],
      self.moduleInfo()[0],
      self.moduleConf()[0],
      self.readWrite()[0],
      self.controll()[0],
      self.gatenetStatus()[0],
      self.gatenetPulse()[0],
      self.gatenetTime()[0],
      self.sitcpLLD()[0]
    ]
    for text in texts:
      print(text)
  
  ### ヒストグラムROM用バッファ (0x00 - 0x3f) ###
  def histgram(self):
    text = "=== [0x00] Histogram ROM Buffer (PSD 1-8 Coeffs) ===\n"
    histogram_rom = self.sendUDP(self.cmd_dict["histgram"])
    for i in range(8):
        offset = i * 8
        psd_data = histogram_rom[offset:offset+8]
        scale = (psd_data[0] << 8) | psd_data[1]
        offset_val = (psd_data[2] << 8) | psd_data[3]
        balance = (psd_data[4] << 8) | psd_data[5]
        lld = (psd_data[6] << 8) | psd_data[7]
        text += f"  PSD {i+1}: Raw={psd_data.hex()} -> Scale:{scale}, Offset:{offset_val}, Balance:{balance}, LLD:{lld}\n"
    text += "-" * 50
    text += "\n"
    return text, None


  ### モジュール情報ROM用バッファ (0x40 - 0x7f) ###
  def moduleInfo(self):
    text = "=== [0x40] Module Information ROM ===\n"
    mod_info_rom = self.sendUDP(self.cmd_dict["moduleInfo"])
    MAC_address = mod_info_rom[0:6]
    KIF = mod_info_rom[6:8]
    KIE = mod_info_rom[8:10]
    ETO = mod_info_rom[10:12]
    DTO = mod_info_rom[12:14]
    MSL = mod_info_rom[14:16]
    RTO = mod_info_rom[16:18]
    comment = mod_info_rom[18:48]
    reserved = mod_info_rom[48:60]
    used_hour = mod_info_rom[60:64]

    comment_str = comment.decode('utf-8').rstrip('\x00')
    text += f" MAC_address : {':'.join(f'{b:02x}' for b in MAC_address).upper()}\n"
    text += f" Comment : {comment_str}\n"
    text += f" used_hour : {int.from_bytes(used_hour, byteorder='big')}\n"
    text += "-" * 50
    text += "\n"
    return text, {
      "KIF": KIF,
      "KIE": KIE,
      "ETO": ETO,
      "DTO": DTO,
      "MSL": MSL,
      "RTO": RTO,
      "comment": comment,
      "reserved": reserved,
      "used_hour": used_hour
    }


  ### モジュール現設定情報読み出し領域 (0x80 - 0x9b) ###
  def moduleConf(self):
    text = "=== [0x80] Current Configuration ===\n"
    config_rom = self.sendUDP(self.cmd_dict["moduleConf"])
    MAC_address = config_rom[0:6]
    KIF = config_rom[6:8]
    KIE = config_rom[8:10]
    ETO = config_rom[10:12]
    DTO = config_rom[12:14]
    MSL = config_rom[14:16]
    RTO = config_rom[16:18]
    IP_adress = config_rom[18:22]
    TCPP = config_rom[22:24]
    MSS = ((config_rom[24] & 0x0F) << 8) | config_rom[25]
    UDPP = config_rom[26:28]
    FE = config_rom[28]
    EV = ((config_rom[29] & 0x7F) << 16) | (config_rom[30] << 8) | config_rom[31]

    text += f" MAC_address  : {':'.join(f'{b:02x}' for b in MAC_address).upper()}\n"
    text += f" IP_adress   : {config_rom[18]}.{config_rom[19]}.{config_rom[20]}.{config_rom[21]}\n"
    text += f" TCP Port    : {int.from_bytes(TCPP, byteorder='big')}\n"
    text += f" UDP Port  : 0x{UDPP.hex()}"
    text += f" RTO (Retransmit TO) : 0x{RTO.hex()}\n"
    text += f" MSS (Max Seg Size)  : {MSS}\n"
    text += f" FIFO Overflow Count : {FE}\n"
    text += "-" * 50
    text += "\n"
    return text, {
      "KIF": KIF,
      "KIE": KIE,
      "ETO": ETO,
      "DTO": DTO,
      "MSL": MSL,
      "RTO": RTO,
      "IP_adress": IP_adress,
      "TCPP": TCPP,
      "MSS": MSS,
      "UDPP": UDPP,
      "FE": FE,
      "EV": EV,
    }

  ### ROM 読み出し、書き込み指令領域 (0x0100 - 0x0100) ###
  def readWrite(self):
    text = "=== [0x0100] ROM Read/Write Command ===\n"
    readwrite_rom = self.sendUDP(self.cmd_dict["readWrite"])
    rw_cmd = readwrite_rom[0]
    text += f"  Read/Write Command: 0x{rw_cmd:02x} ({rw_cmd})\n"
    text += "-" * 50
    text += "\n"
    return text, None


  ### メモリ使用制御領域 (0x0180 - 0x0187) ###
  def controll(self):
    text = "=== [0x0180] Memory Control ===\n"
    control_rom = self.sendUDP(self.cmd_dict["controll"])
    MR = control_rom[0:3]
    VC = control_rom[2:4]
    VD = control_rom[4:6]
    RR = control_rom[6:8]
    text += "-" * 50
    text += "\n"
    return text, {
      "MR": MR,
      "VC": VC,
      "VD": VD,
      "RR": RR
    }


  ### ステータスレジスタ ＃＃GATENET用 (0x0188 - 0x018a) ###
  def gatenetStatus(self):
    text = "=== [0x0188] GATENET Status Register ===\n"
    gatenet_status_rom = self.sendUDP(self.cmd_dict["gatenetStatus"])
    ST = gatenet_status_rom[0:2] #1:time clock供給開始, 0:time clock供給停止
    C = gatenet_status_rom[2]
    text += f" ST : 0x{ST.hex()}\n"
    text += f" C : 0x{ST.hex()}\n"
    text += "-" * 50
    text += "\n"
    return text, {
      "ST": ST,
      "C": C
    }


  ### パルス ID カウンター ＃＃GATENET用 (0x018B - 0x018f) ###
  def gatenetPulse(self):
    text = "=== [0x018B] GATENET Pulse ID Counter ===\n"
    gatenet_pulse_rom = self.sendUDP(self.cmd_dict["gatenetPulse"])
    K = gatenet_pulse_rom[0:5] #pulse ID counter
    text += f" K (pulse id counter) : {int.from_bytes(K, byteorder='big')}\n"
    text += "-" * 50
    text += "\n"
    return text, {
      "K": K,
    }


  ### 装置時刻相対カウンター ＃＃GATENET用 (0x0190 - 0x0196) ###
  def gatenetTime(self):
    text = "=== [0x0190] GATENET Time Counter ===\n"
    gatenet_time_rom = self.sendUDP(self.cmd_dict["gatenetTime"])
    S = (gatenet_time_rom[0] << 22) | (gatenet_time_rom[1] << 14) | (gatenet_time_rom[2] << 6) | (gatenet_time_rom[3] >> 2)
    SS = ((gatenet_time_rom[3] & 0x03) << 13) | (gatenet_time_rom[4] << 5) | (gatenet_time_rom[5] >> 3)
    US = ((gatenet_time_rom[5] & 0x07) << 8) | gatenet_time_rom[6]

    base_time = datetime(2008, 1, 1, 0, 0, 0) # 2008年1月1日基点計算
    sub_seconds = SS / 32768.0 # SS(32.768kHz) から「1秒未満の秒数」を計算
    micro_seconds = US * 0.025 # US(40MHz) から「マイクロ秒（μs）」を計算 (1カウント = 1 / 40MHz = 0.025 μs)
    total_elapsed_seconds = S + sub_seconds + (micro_seconds / 1000000.0)
    current_time = base_time + timedelta(seconds=total_elapsed_seconds) # 基点日時に経過時間を足す
    current_time_jst = current_time + timedelta(hours=9) # JSTに
    text += f" 時刻 (UTC) : {current_time.strftime('%Y-%m-%d %H:%M:%S')}.{current_time.microsecond:06d}\n"
    text += f" 時刻 (JST) : {current_time_jst.strftime('%Y-%m-%d %H:%M:%S')}.{current_time.microsecond:06d}\n"
    text += "-" * 50
    text += "\n"
    return text, {
      "S": S,
      "SS": SS,
      "US": US,
    }

    ### SiTCP 側の LLD, 時間制限 (0x0198 - 0x019f) ###
  def sitcpLLD(self):
    text = "=== [0x0198] SiTCP LLD / Time Limit ===\n"
    sitcp_rom = self.sendUDP(self.cmd_dict["sitcpLLD"])
    LLD = sitcp_rom[0:2]
    TMH = sitcp_rom[2:5]
    TML = sitcp_rom[5:8]
    text += f" LLD  : {int.from_bytes(LLD, byteorder='big')}\n"
    text += f" TMH  : {int.from_bytes(TMH, byteorder='big')}\n"
    text += f" TML  : {int.from_bytes(TML, byteorder='big')}\n"
    text += "-" * 50
    text += "\n"
    return text, {
      "LLD": LLD,
      "TMH": TMH,
      "TML": TML,
    }
  
TARGET_IP = "192.168.0.16"
PORT = 0x1234
Status(TARGET_IP, PORT).getAll()
