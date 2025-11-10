from .EDRread import EDRread as _EDRreadClass
from .eventCsvReader import EventCsvReader

_EDRreader = _EDRreadClass()
_EventCsvReader = EventCsvReader()
EDRread = _EDRreader.EDRread
positionRectROI = _EventCsvReader.positionRectROI

__all__ = [
  'EDRread',
  'positionRectROI'
  ]