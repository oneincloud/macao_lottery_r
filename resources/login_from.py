from PyQt5.Qt import QWidget,QMessageBox,pyqtSignal,QThread,QMouseEvent,QPoint,QAction,QIcon,QLineEdit
from PyQt5.QtCore import Qt
from resources.ui.LoginForm_UI import Ui_LoginForm

class LoginForm(QWidget,Ui_LoginForm):

    logined = pyqtSignal()

    def __init__(self,parent = None):
        super(LoginForm,self).__init__(parent)
        self.setupUi(self)

    def doSubmit(self):
        '''
        提交登录
        :return:
        '''
        username = self.editUsername.text()
        password = self.editPassword.text()

        username = username.strip()
        password = password.strip()

        if username == '' or password == '':
            QMessageBox.critical(self,'出错了','账号或密码不能为空')
            return

        if len(username) < 5:
            QMessageBox.information(self,'提示','账号不正确')
            return

        if password != '123456':
            QMessageBox.information(self,'提示','登录密码不正确')
            return

        self.logined.emit()