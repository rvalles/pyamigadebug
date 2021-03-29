# -*- mode: python ; coding: utf-8 -*-
import glob
dirs = [('docs', 'docs')]
asmfiles=['asm/debugloop.o', 'asm/crc32.o', 'asm/memsend.o', 'asm/memrecv.o', 'asm/floppyxfer.o']
asmglobs = ['asm/bootblock*.desc', 'asm/bootblock*.dd']
files=[]
for path in asmglobs:
    files.extend([(asmfile, "asm/") for asmfile in glob.glob(path)])
files.extend([(asmfile, "asm/") for asmfile in asmfiles])
files.extend(dirs)
print(files)
block_cipher = None
a = Analysis(['amigaXfer.py'],
             pathex=['C:\\Users\\user\\Desktop\\git\\pyamigadebug'],
             binaries=[],
             datas=files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='amigaXfer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='amigaXfer')
