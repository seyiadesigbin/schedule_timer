# PyInstaller build spec for ScheduleTimer.
# Build with:  .venv\Scripts\python -m PyInstaller ScheduleTimer.spec --noconfirm
# Output:      dist\ScheduleTimer.exe

from PyInstaller.utils.hooks import collect_dynamic_libs

a = Analysis(
    ['main.py'],
    pathex=[],
    # The NDI runtime DLL sits next to the NDIlib extension module and is loaded at runtime, so it must be
    # collected explicitly
    binaries=collect_dynamic_libs('NDIlib'),
    datas=[('resources', 'resources')],
    hiddenimports=['NDIlib'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ScheduleTimer',
    icon='icon.ico',
    console=False,
    upx=False,
)
