from PyQt5 import QtWidgets, QtCore
import pymysql
from PyQt5.QtCore import QIODevice, QDataStream, QDate
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket

import login
import DirectorPC
import SellerPC

#Окно авторизации
class Login(QtWidgets.QMainWindow, login.Ui_LoginWindow):
    def __init__(self):
        super(Login, self).__init__()
        self.setupUi(self)

        self.lineName.setPlaceholderText("Введіть ім'я та прізвище") #Устанавливаю текст через плейхолдер потому что он
                                                                    #исчезает и не мешает заполнять данные
        self.linePassword.setPlaceholderText("Введіть пароль")

        self.buttonLogin.clicked.connect(self.log)

    def log(self):#Авторизация
        name = self.lineName.text() #передаю вводимый текст в name
        passw = self.linePassword.text()

        try:
            connection = pymysql.connect(
                host="localhost",
                port=3306,
                user="root",
                password="1Q$pass!",
                database="chat_db",
                cursorclass=pymysql.cursors.DictCursor
            )

            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"select names, password from workers where names='{name}'")
                    worker = cursor.fetchall()

                    if passw == worker[0]['password']:
                        self.posCheck(name)  # переходим к проверке должности
                    else:
                        print("Wrong name or user password")

            finally:
                connection.close()

        except Exception as ex:
            print("Connect failed")
            print(ex)

    def posCheck(self, name):

        try:
            connection = pymysql.connect(
                host="localhost",
                port=3306,
                user="root",
                password="1Q$pass!",
                database="chat_db",
                cursorclass=pymysql.cursors.DictCursor
            )

            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"select position from workers where names='{name}'")
                    position = cursor.fetchall()
                    pos = position[0]["position"]
                    if pos == "director":
                        self.open_director(name, pos)
                    elif pos == "seller":
                        self.open_seller(name, pos)
                    else:
                        print("Wrong name or user does not exist")

            finally:
                connection.close()

        except Exception as ex:
            print("Connect failed")
            print(ex)

    def open_director(self, name, position):
        self.messenger = Director(name, position) #открываю чат директора
        self.messenger.show() #показываю это окно
        self.hide() #закрываю окно текущего класса (логин)

    def open_seller(self, name, position):
        self.messenger = Seller(name, position)
        self.messenger.show()
        self.hide()

#Чат директора секции
class Director(QtWidgets.QMainWindow, DirectorPC.Ui_DirectorWindow):
    def __init__(self, name, position):
        super(Director, self).__init__()
        self.setupUi(self)

        self.textEditSection.setPlaceholderText("Введіть текст...")

        self.labelNLPDir.setText(f"{name} ({position})")
        self.currentUser = self.labelNLPDir.text()

        # Создаем сокет tcpSocket
        self.tcpSocket = QTcpSocket(self)
        self.blockSize = 0  # Очищаем буфер

        # Подключение к серверу
        self.makeRequest()
        self.tcpSocket.waitForConnected(1000)  # Ждем подключение иначе ошибка

        # При получении данных вызывается обработчик get_message
        self.tcpSocket.readyRead.connect(self.get_message)

        self.ButtonSection.clicked.connect(self.send_message)
        self.ButtonDirSec.clicked.connect(self.send_message)

        self.tcpSocket.error.connect(self.displayError)  # Вывести ошибку если не подключилось

    def get_message(self):
        getmes = QDataStream(self.tcpSocket)
        getmes.setVersion(QDataStream.Qt_5_0)
        if self.blockSize == 0:
            if self.tcpSocket.bytesAvailable() < 2:
                return #Вернул None
            self.blockSize = getmes.readUInt16() #readUInt16 возвращает размер блока qunit16
        if self.tcpSocket.bytesAvailable() < self.blockSize:
            return #Вернул None
        # Выводим сообщение в консоль.
        mess = (getmes.readString()).decode('utf-8')

        dt = QDate.currentDate()
        date = dt.toString() #Отримуємо поточну дату
        time = dt.toString() #Отримуємо поточний час

        item = QtWidgets.QListWidgetItem()
        item.setText(f"{self.currentUser} {date} {time}\n{mess}")
        self.listSection.addItem(item)

    def send_message(self):
        message = self.textEditSection.toPlainText() #Беремо повідомлення з вводу
        mess = message.encode('utf-8') #Кодуємо
        self.tcpSocket.write(mess) #Відправляємо у сокет

    def makeRequest(self):
        HOST = '127.0.0.1'
        PORT = 8000
        self.tcpSocket.connectToHost(HOST, PORT, QIODevice.ReadWrite)

    def displayError(self, socketError):
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        else:
            print(self, "The following error occurred: %s." % self.tcpSocket.errorString())

#Чат продавца
class Seller(QtWidgets.QMainWindow, SellerPC.Ui_SellerWindow):
    def __init__(self, name, position):
        super(Seller, self).__init__()
        self.setupUi(self)

        self.textEditSellerSec.setPlaceholderText("Введіть текст...")

        self.labelNLPSeller.setText(f"{name} ({position})")
        self.currentUser = self.labelNLPSeller.text()

        # Создаем сокет tcpSocket
        self.tcpSocket = QTcpSocket(self)
        self.blockSize = 0  # Очищаем буфер

        # Подключение к серверу
        self.makeRequest()
        self.tcpSocket.waitForConnected(1000)  # Ждем подключение иначе ошибка

        # При получении данных вызывается обработчик get_message
        self.tcpSocket.readyRead.connect(self.get_message)

        self.ButtonSellerSec.clicked.connect(self.send_message)
        self.ButtonSellerDir.clicked.connect(self.send_message)

        self.tcpSocket.error.connect(self.displayError)  # Вывести ошибку если не подключилось

    def get_message(self):
        getmes = QDataStream(self.tcpSocket)
        getmes.setVersion(QDataStream.Qt_5_0)
        if self.blockSize == 0:
            if self.tcpSocket.bytesAvailable() < 2:
                return #Вернул None
            self.blockSize = getmes.readUInt16() #readUInt16 возвращает размер блока qunit16
        if self.tcpSocket.bytesAvailable() < self.blockSize:
            return #Вернул None
        # Выводим сообщение в консоль.
        mess = (getmes.readString()).decode('utf-8')

        dt = QDate.currentDate()
        date = dt.toString() #Отримуємо поточну дату
        time = dt.toString() #Отримуємо поточний час

        item = QtWidgets.QListWidgetItem()
        item.setText(f"{self.currentUser} {date} {time}\n{mess}")
        self.listSellerSec.addItem(item)

    def send_message(self):
        message = self.textEditSellerSec.toPlainText() #Беремо повідомлення з вводу
        mess = message.encode('utf-8') #Кодуємо
        self.tcpSocket.write(mess) #Відправляємо у сокет

    def makeRequest(self):
        HOST = '127.0.0.1'
        PORT = 8000
        self.tcpSocket.connectToHost(HOST, PORT, QIODevice.ReadWrite)

    def displayError(self, socketError):
        if socketError == QAbstractSocket.RemoteHostClosedError:
            pass
        else:
            print(self, "The following error occurred: %s." % self.tcpSocket.errorString())


if __name__ == "__main__":
    App = QtWidgets.QApplication([])
    window = Login()
    window.show()
    App.exec_()
