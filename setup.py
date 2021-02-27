import glob
from cx_Freeze import setup, Executable
# Dependencies are automatically detected, but it might need
# fine tuning.
dirs = ['docs']
asmfiles=['asm/crc32.o', 'asm/memsend.o', 'asm/memrecv.o', 'asm/floppyxfer.o']
asmglobs = ['asm/bootblock*.desc', 'asm/bootblock*.dd']
files=[]
for path in asmglobs:
    files.extend([(asmfile, asmfile) for asmfile in glob.glob(path)])
files.extend([(asmfile, asmfile) for asmfile in asmfiles])
files.extend(dirs)
build_options = {
    'packages': ["serial", "wx"],
    'excludes': ["tkinter"],
#    'replace_paths':
    'include_files': files,
    'include_msvcr': True,
    #'compressed': True,
    'optimize': 2
    }
import sys
base = 'Win32GUI' if sys.platform=='win32' else None
executables = [
    Executable('amigaXfer.py', base=base)
]
setup(name='amigaXfer',
      version = '1.0.0.dev2',
      description = 'Data transfer and tools for an Amiga on the serial port.',
      options = {'build_exe': build_options},
      executables = executables)