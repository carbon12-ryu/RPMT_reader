import socket
import time

from .UDPreadRom import UDPreadRom
from .UDPwriteRom import UDPwriteRom

class NEUNET:
  def __init__(self):
    self.IP = "192.168.0.16"
    self.UDPport = 0x1234
    self.TCPport = 23
    self.NeunetUR = UDPreadRom(self.IP, self.UDPport)
    self.NeunetUW = UDPwriteRom(self.IP, self.UDPport)
    
  def config(self):
    text = self.NeunetUR.getAll()
    print(text)
    return None
  
  def measure(self, filePath, KP):
    self.NeunetUW.startMes()
    count_5b = 0
    cmd = bytes.fromhex("a3 00 00 00 00 07 a1 20")
    with open(filePath, "ab") as f:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((self.IP, self.TCPport))
          
        while count_5b < KP:
          t0 = time.perf_counter()
          sock.sendall(cmd)
          t1 = time.perf_counter()
          header = sock.recv(4)
          length = int.from_bytes(header, "big")*2
          payload = sock.recv(4+length) if length > 0 else b""
          t2 = time.perf_counter()
          count_5b += payload[::8].count(0x5B)
          t3 = time.perf_counter()
          f.write(payload)
          t4 = time.perf_counter()
          # print(
          #     f"\rsend={(t1-t0)*1000:.3f}ms "
          #     f"recv={(t2-t1)*1000:.3f}ms "
          #     f"count={(t3-t2)*1000:.3f}ms "
          #     f"write={(t4-t3)*1000:.3f}ms",
          #     end=""
          # )
          print(f"\rcurrent KP: {count_5b}", end="", flush=True)
    return None
          
# filePath = os.path.join(os.getcwd(), "test.edr")
# NEUNET().measure(filePath=filePath, KP=100)