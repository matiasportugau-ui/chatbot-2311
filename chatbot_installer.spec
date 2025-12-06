# -*- mode: python ; coding: utf-8 -*-
"""
Archivo de configuración PyInstaller para BMC Chatbot
Genera un ejecutable standalone de Windows
"""

block_cipher = None

a = Analysis(
    ['chat_interactivo.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Incluir archivos de datos si los hay
        # ('config.json', '.'),
        # ('matriz_precios.json', '.'),
    ],
    hiddenimports=[
        'sistema_cotizaciones',
        'utils_cotizaciones',
        'decimal',
        'io',
        'sys',
        'os',
        'time',
        're',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BMC_Chatbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mantener consola para ver mensajes
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar un icono .ico aquí si tienes uno
)

