import sys

is_25 = sys.version.startswith('2.5')
is_26 = sys.version.startswith('2.6')
if is_25:
    import _consolepos25 as _consolepos
elif is_26:
    import _consolepos26 as _consolepos

getpos = _consolepos.getpos
gotoxy = _consolepos.gotoxy
