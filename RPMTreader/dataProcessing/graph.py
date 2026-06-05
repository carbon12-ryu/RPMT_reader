from matplotlib import pyplot as plt
import numpy as np

class Graph:
  def drawMapGraph(
    self, 
    positions,
    mapGraphPath,
    t0_pulse,
    total_count,
    ROI=None,
    timeROImin = None,
    timeROImax = None,
    ):
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
      
    text = f"t0 pulse: {t0_pulse}\nTotal: {total_count}"
    if ROI is not None:
      text = f"t0 pulse: {t0_pulse}\nTotal in ROI: {total_count}"
    if (timeROImin is not None) or (timeROImax is not None):
      text = text + f"\nTime ROI is {timeROImin}~{timeROImax}"
    plt.text(
      0.98, 0.98,
      text,
      ha='right', va='top',
      fontsize=10,
      color='white',
      transform=plt.gca().transAxes,
      bbox=dict(facecolor='black', alpha=0.5, pad=3)
  )
    plt.xlabel("x position")
    plt.ylabel("y position")
    plt.title("Neutron distribution (2D histogram)")
    plt.colorbar(hb[3], label='Counts')
    plt.grid(True, alpha=0.3)
    plt.axis("equal")
    plt.savefig(mapGraphPath)
    
  def drawTofGraph(
    self,
    times,
    tofGraphPath,
    t0_pulse,
    total_count,
    tofBinTime
    ):
    bins = np.arange(times.min(), times.max()+tofBinTime, tofBinTime)

    plt.figure(figsize=(8,5))
    plt.hist(times, bins=bins, histtype='step', color='blue')
    text = f"t0 pulse: {t0_pulse}\nTotal: {total_count}"
    plt.text(
      0.98, 0.98,  # 右上に相対位置で配置
      text,
      ha='right', va='top',
      fontsize=10,
      color='white',
      transform=plt.gca().transAxes,
      bbox=dict(facecolor='black', alpha=0.5, pad=3)
    )
    plt.ylabel("Counts")
    plt.xlabel("Time (sec)")
    plt.title("Neutron TOF spectrum")
    plt.grid(True)
    plt.savefig(tofGraphPath)