import socket
import os
import numpy as np
import threading

from matplotlib import pyplot as plt

from .UDPreadRom import UDPreadRom
from .UDPwriteRom import UDPwriteRom
from ..dataProcessing.EDRread import EDRread

class NEUNET:
  def __init__(self):
    self.IP = "192.168.0.16"
    self.UDPport = 0x1234
    self.TCPport = 23
    self.NeunetUR = UDPreadRom(self.IP, self.UDPport)
    self.NeunetUW = UDPwriteRom(self.IP, self.UDPport)
    self.EDRread = EDRread()
    self.running = False
    
  def setIP(self, new_ip):
      self.IP = new_ip
      self.NeunetUR.ip = new_ip
      self.NeunetUW.ip = new_ip
      
  def config(self):
    text = self.NeunetUR.getAll()
    print(text)
    return None
  
  def measure(self, filePath, KP):
    self.NeunetUW.startMes()
    count_5b = 0
    self.running = True
    cmd = bytes.fromhex("a3 00 00 00 00 07 a1 20")
    with open(filePath, "ab") as f:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((self.IP, self.TCPport))
          
        while count_5b < KP:
          sock.sendall(cmd)
          header = sock.recv(4)
          length = int.from_bytes(header, "big")*2
          if not (length > 0 and length%8 ==0 ):
            print("length error")
            continue
          payload = sock.recv(4+length)
          if any(h not in (0x5A, 0x5B, 0x5C) for h in payload[::8]):
            print("data mismutch")
            continue
          count_5b += payload[::8].count(0x5B)
          f.write(payload)
          f.flush()
          print(f"\rcurrent KP: {count_5b}", end="", flush=True)
    self.running = False
    print("finish RPMT")
    return None
  
  def graph(self, filePath, graphPath):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    plt.ion()
    cbar = None
    
    while plt.fignum_exists(fig.number) and self.running:
      if not os.path.exists(filePath) or os.path.getsize(filePath) == 0:
        plt.pause(0.05)
        continue 
      try:
        tofBinTime = 100e-6
        t0_pulse, neutrons, tof_data, total_count = self.EDRread.EDRread(filePath, tofBinTime = tofBinTime)
        positions = neutrons[:, 0:2]
        times = neutrons[:,2]
            
        ax1.cla()
        ax1.set_xlabel("x position")
        ax1.set_ylabel("y position")
        ax1.set_title("Neutron distribution (2D LIVE)")
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')

        if len(positions) > 0:
          if cbar is not None:
            cbar.remove()
          hb = ax1.hist2d(
              positions[:, 0], positions[:, 1],
              bins=100, range=[[0, 1], [0, 1]],
              cmap='inferno', cmin=1
          )
          
        text_str = f"t0 pulse: {t0_pulse}\nTotal: {total_count}"
        ax1.text(
            0.98, 0.98, text_str, ha='right', va='top', fontsize=10, color='white',
            transform=ax1.transAxes, bbox=dict(facecolor='black', alpha=0.5, pad=3)
        )
        
        ax2.cla()
        ax2.set_ylabel("Counts")
        ax2.set_xlabel("Time (sec)")
        ax2.set_title("Neutron TOF spectrum [LIVE]")
        ax2.grid(True, alpha=0.3)

        if len(times) > 1:
            bins = np.arange(times.min(), times.max() + tofBinTime, tofBinTime)
            plt.hist(times, bins=bins, histtype='step', color='blue')
            ax2.set_xlim(times.min(), times.max())
      except Exception as e:
        print(e)
      plt.pause(0.05)
    plt.ioff()
    if graphPath is not None:
      plt.savefig(graphPath)
    plt.close()
    
  def measureGraph(self, filePath, KP, graphPath=None):
    measure_thread = threading.Thread(
        target=self.measure,
        args=(filePath, KP),
        daemon=True
    )
    measure_thread.start()
    self.graph(filePath, graphPath)
        