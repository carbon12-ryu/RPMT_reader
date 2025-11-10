from matplotlib import pyplot as plt
import numpy as np

class Graph:
  def drawMapGraph(self, positions, mapGraphPath, ROI=None):
    plt.figure(figsize=(6,6))
    hb = plt.hist2d(
      positions[:,0],
      positions[:,1],
      bins=300,
      range=[[0,1],[0,1]],
      cmap='inferno',
      cmin=1
      )
    if ROI is not None:
      plt.scatter(
        ROI[:,0],
        ROI[:,1],
        s=5,
        color='red',
        alpha=0.5,
        label='ROI'
      )
    plt.xlabel("x position")
    plt.ylabel("y position")
    plt.title("Neutron distribution (2D histogram)")
    plt.colorbar(hb[3], label='Counts')
    plt.grid(True, alpha=0.3)
    plt.axis("equal")
    plt.savefig(mapGraphPath)
    
  def drawTofGraph(self, times, tofGraphPath, tofBinTime):
    bins = np.arange(times.min(), times.max()+tofBinTime, tofBinTime)

    plt.figure(figsize=(8,5))
    plt.hist(times, bins=bins, histtype='step', color='blue')
    plt.ylabel("Counts")
    plt.xlabel("Time (sec)")
    plt.title("Neutron TOF spectrum")
    plt.grid(True)
    plt.savefig(tofGraphPath)