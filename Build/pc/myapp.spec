# -*- mode: python -*-

from kivy_deps import sdl2, glew

block_cipher = None

# list of modules to exclude from analysis
excludes_a = ['Tkinter', 'picamera', 'gi', 'cv2', 'enchant']


a = Analysis(['..\\..\\Code\\engine.py'],
             pathex=['F:\\works\\calcio\\project\\Build\\pc',
             '..\\..\\MyHiddenImports'],
             binaries=None,
             datas=None,
             hiddenimports=['MyHiddenImports'],
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes_a,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
         cipher=block_cipher)

a.datas += [('form.kv', '../../Code/form.kv', 'DATA')]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,          
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name='reservation',
          debug=True,
          strip=False,
          upx=True,
          console=True)