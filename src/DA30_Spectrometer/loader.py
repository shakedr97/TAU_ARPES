import chardet
from cffi import FFI
import os
print('import cffi worked')

def get_home_dir(path):
    home = 'TAU_ARPES'
    start = path.find(home)
    return path[:start + len(home)]

path_to_header = os.path.join(get_home_dir(os.getcwd()), 'SESWrapper', 
    'seswrapper_2.7.7_Win64', 'seswrapper_2.7.7_Win64', 'LabVIEW', 'headers', 'seswrapper.h')

path_to_dll = os.path.join(get_home_dir(os.getcwd()), 'SESWrapper', 
    'seswrapper_2.7.7_Win64', 'seswrapper_2.7.7_Win64', 'SESWrapper.dll') 

ffi = FFI()
with open(path_to_header) as f:
    ffi.cdef(f.read())

dll = ffi.dlopen(path_to_dll)