pyinstaller --clean --icon=icon.ico --add-binary "xdelta.exe;." --add-binary "sign_np.exe;." --distpath . -F tool.py
