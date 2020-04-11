pyinstaller --clean --icon=icon.ico --add-binary "xdelta.exe;." --add-binary "sign_np.exe;." --add-binary "armips.exe;." --distpath . -F --hidden-import="pkg_resources.py2_warn" tool.py
