import os
import json
import matplotlib.pyplot as plt
import numpy as np

from RPMTreader.graph import Graph
from RPMTreader.csv import Csv

class EDRread:
  def __init__(self):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(base_dir, "settings", "EDRsettings.json")
    with open(settings_path, "r") as f:
      self.settings= json.load(f)
      
    self.drawMapGraph = Graph().drawMapGraph
    self.drawTofGraph = Graph().drawTofGraph
    self.eventCsv = Csv().eventCsv
    self.tofCsv = Csv().tofCsv
    
  def EDRread(self, 
              filePath, 
              mapGraphPath=None,
              tofGraphPath=None,
              eventCsvPath=None,
              tofCsvPath=None,
              xSwap = False,
              ySwap = False,
              xySwap = False,
              tofBinTime = 10e-6,
              ):
    data = np.fromfile(filePath, dtype=np.uint8).reshape(-1, 8)

    headers = data[:,0]
    t0_pulse = np.sum(headers == 91)

    # extract neutron events
    mask_90 = headers == 90
    events = data[mask_90]
    
    # convert binary to T, P , PL, PR
    T  = (
      events[:,3].astype(np.uint32) 
      + (events[:,2].astype(np.uint32) << 8) 
      + (events[:,1].astype(np.uint32) << 16)
      )
    P  = events[:,4]
    bits = (
      (events[:,5].astype(np.uint32) << 16) 
      | (events[:,6].astype(np.uint32) << 8) 
      | events[:,7].astype(np.uint32)
      )
    PL = (bits >> 12) & 0xFFF
    PR = bits & 0xFFF

    PSD = P & 0x7
    module = (P >> 3) & 0x1F
    time = T*(1/self.settings["clockFreq"])

    time_prev  = np.roll(time, 1)
    PSD_prev = np.roll(PSD, 1)
    PL_prev = np.roll(PL, 1)
    PR_prev = np.roll(PR, 1)

    # pulse pair (vertial and horizontal) in effectiveTime will be assumed as neutron count
    mask = (
      (np.abs(time - time_prev) <= self.settings["effectiveTime"])&
      (np.abs(PSD - PSD_prev) <= 1) &
      (self.settings["PL_min"]< PL) & (PL < self.settings["PL_max"]) &
      (self.settings["PR_min"]< PR) & (PR < self.settings["PR_max"]) &
      (self.settings["PL_min"]< PL_prev) & (PL_prev < self.settings["PL_max"]) &
      (self.settings["PR_min"]< PR_prev) & (PR_prev < self.settings["PR_max"])
    )
    
    nx = PL_prev[mask] / (PL_prev[mask] + PR_prev[mask])
    ny = PL[mask] / (PL[mask] + PR[mask])
    nt = time[mask]
      
    swap_mask = PSD[mask] == 1 
    ny[swap_mask], nx[swap_mask] = nx[swap_mask], ny[swap_mask]
    
    if xSwap:
      nx = 1-nx
      
    if ySwap:
      ny = 1-ny
      
    if xySwap:
      nx, ny = ny, nx
      
    counts, bin_edges = np.histogram(nt, bins=np.arange(nt.min(), nt.max()+tofBinTime, tofBinTime))
    time_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    tof_data = np.column_stack((time_centers, counts))
      
    neutrons = np.column_stack([nx, ny, nt])
    neutrons = np.array(neutrons)
    
    total_count = len(neutrons)
    
    if mapGraphPath is not None:
      self.drawMapGraph(
        neutrons[:,0:2],
        mapGraphPath,
        t0_pulse,
        total_count
        )
      
    if tofGraphPath is not None:
      self.drawTofGraph(
        neutrons[:,2],
        tofGraphPath,
        t0_pulse,
        total_count,
        tofBinTime
        )
  
    if eventCsvPath is not None:
      self.eventCsv(
        eventCsvPath,
        neutrons,
        t0_pulse
      )
      
    if tofCsvPath is not None:
      self.tofCsv(
        tofCsvPath,
        tof_data,
        t0_pulse,
        tofBinTime
      )
    
    return t0_pulse, neutrons, tof_data, total_count

