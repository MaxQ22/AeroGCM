# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

import mpl_toolkits.basemap
import os

#Collect the data from the basemap and airportsdata package
datas = collect_data_files('mpl_toolkits')
datas += collect_data_files('airportsdata')

block_cipher = None

a = Analysis(['src\\AeroGCM.py'],
             pathex=[''],
             binaries=[],
             datas=datas,
             hiddenimports=['mpl_toolkits.basemap_data.epsg'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='AeroGCM',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False  #As this is a GUI app, do not show the console
           )
