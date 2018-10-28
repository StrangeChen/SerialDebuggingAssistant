# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets,QtSerialPort
from PyQt5.QtWidgets import QMessageBox,QMainWindow,QToolTip
from PyQt5.QtCore import QThread,QTimer
from PyQt5.QtGui import QCursor
from ui_mainwidow import Ui_MainWindow
from Receive import Receive

OFF = False
ON = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__uartState = OFF
        self.__serialPort = QtSerialPort.QSerialPort()
        self.__receiveThread = QThread(self)
        self.__uartReceive = Receive(self.__serialPort)
        self.__uartReceive.moveToThread(self.__receiveThread)
        # self.__receiveTimer = QTimer()
        self.uart_init()

        self.ui.pushButton_uart_sw.clicked.connect(self.change_uart_state)
        self.ui.pushButton_uart_rfresh.clicked.connect(self.refresh_uart_info)
        self.ui.comboBox_com.currentTextChanged.connect(self.change_combox_tooltip)
        self.ui.radioButton_show_ascii.toggled.connect(self.display_ascii)
        self.ui.radioButton_show_hex.toggled.connect(self.display_hex)



    def uart_init(self):
        self.__uartState = OFF
        self.ui.comboBox_com.clear()

        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.ui.comboBox_com.addItem(info.portName() + ":" + info.description())

        self.ui.comboBox_com.setCurrentIndex(0)
        self.ui.comboBox_com.setToolTip(self.ui.comboBox_com.currentText())

    def change_uart_state(self):
        if self.__uartState:
            self.__serialPort.close()
            #self.__receiveTimer.stop()
            self.__uartState = OFF
            self.ui.pushButton_uart_sw.setText("打开串口")
            self.ui.comboBox_com.setEnabled(True)
        else:
            self.__serialPort.setPortName(self.ui.comboBox_com.currentText().split(':')[0])
            self.__serialPort.setBaudRate(int(self.ui.comboBox_baud.currentText()))
            self.__serialPort.setFlowControl(QtSerialPort.QSerialPort.NoFlowControl)
            self.__serialPort.setDataBits(QtSerialPort.QSerialPort.Data8)
            self.__serialPort.setStopBits(QtSerialPort.QSerialPort.OneStop)
            self.__serialPort.setParity(QtSerialPort.QSerialPort.NoParity)
            self.__serialPort.setReadBufferSize(10)

            # print(self.__serialPort.open(QtSerialPort.QSerialPort.ReadWrite))

            if self.__serialPort.open(QtSerialPort.QSerialPort.ReadWrite):
                self.__uartState = ON
                # self.__receiveTimer.start()
                # self.__receiveThread.start()
                # 常规模式
                self.__serialPort.readyRead.connect(self.receive_uart_data)

                self.ui.pushButton_uart_sw.setText("关闭串口")
                self.ui.comboBox_baud.setEnabled(False)
                self.ui.comboBox_com.setEnabled(False)
            else:
                QMessageBox.critical(self,"Error","Fail to turn on this device!")
                print(self.__serialPort.error())

    def refresh_uart_info(self):
        if self.__uartState == ON:
            QToolTip.showText(QCursor.pos(),"Please turn off the current device first.")
        else:
            self.uart_init()

    def change_combox_tooltip(self):
        self.ui.comboBox_com.setToolTip(self.ui.comboBox_com.currentText())

    def receive_uart_data(self):
        if self.__serialPort.isReadable():
            data = self.__serialPort.readAll()
            if data.isEmpty():
                return
            self.ui.plainTextEdit_rx.moveCursor(QtGui.QTextCursor.End)

            if self.ui.radioButton_show_ascii.isChecked():
                self.ui.plainTextEdit_rx.insertPlainText(str(data, encoding='gbk'))
            else:
                hexText = data.toHex().toUpper()
                for i in range(0,hexText.length(),2):
                    self.ui.plainTextEdit_rx.insertPlainText(' '+str(hexText.mid(i,2),encoding='gbk'))

    def display_ascii(self,checked):
        if checked:
            hexText = self.ui.plainTextEdit_rx.toPlainText().replace(" ","").encode('gbk')
            print(hexText)
            strText = ""
            for i in range(0,len(hexText),2):
                strText += chr(int(hexText[i:i+2],16))
           # print(strText)
            self.ui.plainTextEdit_rx.setPlainText(strText)

    def display_hex(self,checked):
        pass

    def clean_display(self):
        pass

    def save_receive_data(self):
        pass

