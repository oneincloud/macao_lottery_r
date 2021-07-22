# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoginForm.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginForm(object):
    def setupUi(self, LoginForm):
        LoginForm.setObjectName("LoginForm")
        LoginForm.resize(255, 140)
        LoginForm.setMinimumSize(QtCore.QSize(255, 140))
        LoginForm.setMaximumSize(QtCore.QSize(255, 140))
        self.formLayout = QtWidgets.QFormLayout(LoginForm)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(LoginForm)
        self.label.setMinimumSize(QtCore.QSize(0, 36))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(13)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.editUsername = QtWidgets.QLineEdit(LoginForm)
        self.editUsername.setMinimumSize(QtCore.QSize(0, 36))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(13)
        self.editUsername.setFont(font)
        self.editUsername.setObjectName("editUsername")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.editUsername)
        self.label_2 = QtWidgets.QLabel(LoginForm)
        self.label_2.setMinimumSize(QtCore.QSize(0, 36))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(13)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.editPassword = QtWidgets.QLineEdit(LoginForm)
        self.editPassword.setMinimumSize(QtCore.QSize(0, 36))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(13)
        self.editPassword.setFont(font)
        self.editPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.editPassword.setObjectName("editPassword")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.editPassword)
        self.btnSubmit = QtWidgets.QPushButton(LoginForm)
        self.btnSubmit.setMinimumSize(QtCore.QSize(0, 36))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(13)
        self.btnSubmit.setFont(font)
        self.btnSubmit.setObjectName("btnSubmit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.btnSubmit)

        self.retranslateUi(LoginForm)
        self.btnSubmit.clicked.connect(LoginForm.doSubmit)
        QtCore.QMetaObject.connectSlotsByName(LoginForm)

    def retranslateUi(self, LoginForm):
        _translate = QtCore.QCoreApplication.translate
        LoginForm.setWindowTitle(_translate("LoginForm", "登录"))
        self.label.setText(_translate("LoginForm", "账号："))
        self.label_2.setText(_translate("LoginForm", "密码："))
        self.btnSubmit.setText(_translate("LoginForm", "登 录"))
