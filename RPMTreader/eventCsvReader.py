import numpy as np
import csv

from RPMTreader.graph import Graph
from RPMTreader.csv import Csv

class EventCsvReader:
  def __init__(self):
    self.drawMapGraph = Graph().drawMapGraph
    self.drawTofGraph = Graph().drawTofGraph
    self.eventCsv = Csv().eventCsv
    self.tofCsv = Csv().tofCsv
    
  def _ROI(
    self,
    eventCsvPath,
    mask_func,
    ROI,
    mapGraphPath = None,
    tofGraphPath = None,
    tofCsvPath = None,
    timeROImin = None,
    timeROImax = None,
    tofBinTime = 10e-6
  ):
    with open(eventCsvPath, newline='') as f:
      reader = csv.reader(f)
      rows = list(reader)
    t0_pulse = int(rows[1][0])

    data_list = rows[3:]
    neutrons = np.array(data_list, dtype=float)
    x = neutrons[:, 0]
    y = neutrons[:, 1]
    t = neutrons[:, 2]
    
    mask = mask_func(x, y)
    
    if (timeROImin is None) != (timeROImax is None):
        raise ValueError("Both timeROImin and timeROImax must be specified together or both left as None")

    if timeROImin is not None and timeROImax is not None:
        time_mask = (t >= timeROImin) & (t <= timeROImax)
        mask = mask & time_mask
        
    masked_neutrons = neutrons[mask]
    
    nt = masked_neutrons[:,1]
    counts, bin_edges = np.histogram(nt, bins=np.arange(nt.min(), nt.max()+tofBinTime, tofBinTime))
    time_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    tof_data = np.column_stack((time_centers, counts))
    
    total_count = len(masked_neutrons)
    
    if mapGraphPath is not None:
      if timeROImin is not None and timeROImax is not None:
        time_masked_neutrons = neutrons[time_mask]
        self.drawMapGraph(
          time_masked_neutrons[:,0:2],
          mapGraphPath,
          t0_pulse,
          total_count,
          ROI=ROI,
          timeROImin = timeROImin,
          timeROImax = timeROImax,
          )
      else:
        self.drawMapGraph(
          neutrons[:,0:2],
          mapGraphPath,
          t0_pulse,
          total_count,
          ROI=ROI,
          timeROImin = timeROImin,
          timeROImax = timeROImax,
          )
      
    if tofGraphPath is not None:
      self.drawTofGraph(
        masked_neutrons[:,2],
        tofGraphPath,
        t0_pulse,
        total_count,
        tofBinTime
        )
      
    if tofCsvPath is not None:
      self.tofCsv(
        tofCsvPath,
        tof_data,
        t0_pulse,
        tofBinTime
      )
      
    return t0_pulse, masked_neutrons, tof_data, total_count
    
  def rectROI(
    self,
    eventCsvPath,
    xmin,
    xmax,
    ymin,
    ymax,
    **kwargs
    ):
    def mask_func(x, y):
      return ((x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax))

    n_per_edge = 1000
    bottom_x = np.linspace(xmin, xmax, n_per_edge, endpoint=False)
    bottom_y = np.full(n_per_edge, ymin)
    right_x = np.full(n_per_edge, xmax)
    right_y = np.linspace(ymin, ymax, n_per_edge, endpoint=False)
    top_x = np.linspace(xmax, xmin, n_per_edge, endpoint=False)
    top_y = np.full(n_per_edge, ymax)
    left_x = np.full(n_per_edge, xmin)
    left_y = np.linspace(ymax, ymin, n_per_edge, endpoint=False)

    bottom = np.column_stack((bottom_x, bottom_y))
    right  = np.column_stack((right_x, right_y))
    top    = np.column_stack((top_x, top_y))
    left   = np.column_stack((left_x, left_y))

    ROI = np.vstack((bottom, right, top, left))
    
    return self._ROI(eventCsvPath, mask_func, ROI, **kwargs)
  
  def circleROI(
    self,
    eventCsvPath,
    xcenter,
    ycenter,
    radius,
    **kwargs
    ):
    def mask_func(x, y):
      return (x-xcenter)**2+(y-ycenter)**2 <= radius**2
    
    n_points = 1000
    theta = np.linspace(0, 2*np.pi, n_points, endpoint=True)
    circle_x = xcenter + radius * np.cos(theta)
    circle_y = ycenter + radius * np.sin(theta)
    ROI = np.column_stack((circle_x, circle_y))
    
    return self._ROI(eventCsvPath, mask_func, ROI, **kwargs)