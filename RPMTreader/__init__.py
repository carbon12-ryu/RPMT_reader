from .EDRread import EDRread as _EDRreadClass

_EDRreader = _EDRreadClass()
EDRread = _EDRreader.EDRread

__all__ = ['EDRread']