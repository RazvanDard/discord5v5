import winreg

def get_system_fonts():
    font_names = []
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts") as key:
        index = 0
        while True:
            try:
                font_info = winreg.EnumValue(key, index)
                font_name = font_info[0]
                font_names.append(font_name)
                index += 1
            except WindowsError:
                break
    return font_names

system_fonts = get_system_fonts()

for font in system_fonts:
    print(font)
