"""Consulta a visibilidade da NSWindow do SDL na thread de apresentação."""
from ctypes import CDLL, CFUNCTYPE, c_char_p, c_ulong, c_void_p

# NSWindowOcclusionStateVisible indica que pelo menos parte da janela aparece.
VISIVEL = 1 << 1
_objc = CDLL("/usr/lib/libobjc.A.dylib")
_objc.sel_registerName.argtypes = (c_char_p,)
_objc.sel_registerName.restype = c_void_p
_occlusion_state = _objc.sel_registerName(b"occlusionState")
_estado = CFUNCTYPE(c_ulong, c_void_p, c_void_p)(("objc_msgSend", _objc))


def janela_visivel(handle):
    return bool(_estado(handle, _occlusion_state) & VISIVEL)
