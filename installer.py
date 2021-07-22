import os
import app

if __name__ == '__main__':

    from PyInstaller.__main__ import run

    opts = [
        '-F',
        '-w',
        # '-D',
        '--name=%sv%s' % (app.NAME,app.VERSION),
        '--clean',
        '-y',
        'main.py'
    ]

    run(opts)