import numpy as np

class Csv:
  def eventCsv(self, eventCsvPath, neutrons, t0_pulse):
    np.savetxt(
      eventCsvPath,
      neutrons,
      delimiter=",",
      header=f"total KP \n{t0_pulse}\nx,y,time[s]",
      comments="",
      fmt="%.6f"
      )
    
  def tofCsv(self, tofCsvPath, tof_data, t0_pulse, tofBinTime):
    np.savetxt(
      tofCsvPath,
      tof_data,
      delimiter=",",
      header=f"total KP \n{t0_pulse}\nbin time[s]\n{tofBinTime}\ntime[s],counts",
      comments="",
      fmt="%.6f"
      )