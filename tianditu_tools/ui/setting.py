# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setting.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SettingDialog(object):
    def setupUi(self, SettingDialog):
        SettingDialog.setObjectName("SettingDialog")
        SettingDialog.resize(582, 312)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        SettingDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(SettingDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(SettingDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_keyset = QtWidgets.QWidget()
        self.tab_keyset.setObjectName("tab_keyset")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_keyset)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox = QtWidgets.QGroupBox(self.tab_keyset)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.mLineEdit_key = QgsPasswordLineEdit(self.groupBox)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.mLineEdit_key.setFont(font)
        self.mLineEdit_key.setClearButtonEnabled(False)
        self.mLineEdit_key.setShowLockIcon(False)
        self.mLineEdit_key.setObjectName("mLineEdit_key")
        self.horizontalLayout.addWidget(self.mLineEdit_key)
        self.saveButton = QtWidgets.QPushButton(self.groupBox)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 10)
        self.horizontalLayout.setStretch(2, 2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.keyComboBox = QtWidgets.QComboBox(self.groupBox)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.keyComboBox.setFont(font)
        self.keyComboBox.setObjectName("keyComboBox")
        self.horizontalLayout_2.addWidget(self.keyComboBox)
        self.checkBox_key_rand = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_key_rand.setObjectName("checkBox_key_rand")
        self.horizontalLayout_2.addWidget(self.checkBox_key_rand)
        self.pushButton_copy = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_copy.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_copy.setObjectName("pushButton_copy")
        self.horizontalLayout_2.addWidget(self.pushButton_copy)
        self.pushButton_delete = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_delete.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.horizontalLayout_2.addWidget(self.pushButton_delete)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 10)
        self.horizontalLayout_2.setStretch(4, 2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.subdomainComboBox = QtWidgets.QComboBox(self.groupBox)
        self.subdomainComboBox.setMinimumSize(QtCore.QSize(80, 0))
        self.subdomainComboBox.setBaseSize(QtCore.QSize(200, 0))
        self.subdomainComboBox.setCurrentText("")
        self.subdomainComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertAtTop)
        self.subdomainComboBox.setObjectName("subdomainComboBox")
        self.horizontalLayout_3.addWidget(self.subdomainComboBox)
        self.checkBox_domain_rand = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_domain_rand.setObjectName("checkBox_domain_rand")
        self.horizontalLayout_3.addWidget(self.checkBox_domain_rand)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setOpenExternalLinks(True)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.info_status = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(8)
        self.info_status.setFont(font)
        self.info_status.setStyleSheet("color: rgb(128, 128, 128);")
        self.info_status.setText("")
        self.info_status.setObjectName("info_status")
        self.verticalLayout_2.addWidget(self.info_status)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.tabWidget.addTab(self.tab_keyset, "")
        self.tab_map = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_map.sizePolicy().hasHeightForWidth())
        self.tab_map.setSizePolicy(sizePolicy)
        self.tab_map.setObjectName("tab_map")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_map)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_5.addLayout(self.verticalLayout_6)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.btn_checkupdate = QtWidgets.QPushButton(self.tab_map)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_checkupdate.sizePolicy().hasHeightForWidth())
        self.btn_checkupdate.setSizePolicy(sizePolicy)
        self.btn_checkupdate.setObjectName("btn_checkupdate")
        self.horizontalLayout_6.addWidget(self.btn_checkupdate)
        self.label_checkstatus = QtWidgets.QLabel(self.tab_map)
        self.label_checkstatus.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(8)
        self.label_checkstatus.setFont(font)
        self.label_checkstatus.setObjectName("label_checkstatus")
        self.horizontalLayout_6.addWidget(self.label_checkstatus)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.verticalLayout_5.setStretch(0, 5)
        self.verticalLayout_5.setStretch(1, 1)
        self.tabWidget.addTab(self.tab_map, "")
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(SettingDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SettingDialog)

    def retranslateUi(self, SettingDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingDialog.setWindowTitle(_translate("SettingDialog", "设置"))
        self.groupBox.setTitle(_translate("SettingDialog", "Key 设置"))
        self.label.setText(_translate("SettingDialog", "添加 Key:"))
        self.mLineEdit_key.setPlaceholderText(_translate("SettingDialog", "输入天地图key"))
        self.saveButton.setText(_translate("SettingDialog", "保存"))
        self.label_2.setText(_translate("SettingDialog", "选择 Key:"))
        self.checkBox_key_rand.setText(_translate("SettingDialog", "随机"))
        self.pushButton_copy.setText(_translate("SettingDialog", "复制"))
        self.pushButton_delete.setText(_translate("SettingDialog", "删除"))
        self.label_3.setText(_translate("SettingDialog", "子域 Subdomain:"))
        self.checkBox_domain_rand.setToolTip(_translate("SettingDialog", "<html><head/><body><p><span style=\" font-size:10pt;\">添加底图时随机选择子域名，可减轻服务器压力，</span>提高可用性。</p></body></html>"))
        self.checkBox_domain_rand.setText(_translate("SettingDialog", "随机"))
        self.label_4.setText(_translate("SettingDialog", "<html><head/><body><p><a href=\"https://console.tianditu.gov.cn/api/key\"><span style=\" font-weight:600; text-decoration: underline; color:#808080;\">点击此处前往天地图申请 Key</span></a></p><p><span style=\" color:#808080;\">Key 类型建议选择为“</span><span style=\" text-decoration: underline; color:#808080;\">浏览器端</span><span style=\" color:#808080;\">” 或者 “</span><span style=\" text-decoration: underline; color:#808080;\">Android平台</span><span style=\" color:#808080;\">”</span></p><p><span style=\" color:#808080;\">如果工程同步到QField中使用，选择“</span><span style=\" text-decoration: underline; color:#808080;\">Android平台</span><span style=\" color:#808080;\">”</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_keyset), _translate("SettingDialog", "天地图设置"))
        self.btn_checkupdate.setText(_translate("SettingDialog", "检查更新"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_map), _translate("SettingDialog", "地图管理"))
from qgspasswordlineedit import QgsPasswordLineEdit
