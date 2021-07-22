import six
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements
import sys
from PyQt5.Qt import QApplication
from resources.login_from import LoginForm
from resources.main_window import MainWindow

mainWin = None

def starg_main():
    global mainWin

    mainWin = MainWindow()
    mainWin.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    # loginFrom = LoginForm()
    # loginFrom.logined.connect(lambda :loginFrom.close())
    # loginFrom.logined.connect(lambda :starg_main())
    # loginFrom.show()

    starg_main()

    sys.exit(app.exec_())