import sys
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtNetwork import QHostAddress, QTcpServer

class Server(QDialog):
    def __init__(self):
        super().__init__()
        self.tcpServer = None

    def sessionOpened(self):
        self.tcpServer = QTcpServer(self)
        PORT = 8000
        address = QHostAddress('127.0.0.1')
        if not self.tcpServer.listen(address, PORT):
            print("cant listen!")
            self.close()
            return
        self.tcpServer.newConnection.connect(self.dealCommunication)

    def dealCommunication(self):
        # Получаем новый сокет с которого подключились
        clientConnection = self.tcpServer.nextPendingConnection()

        # Создаем экземпляр QByteArray
        block = QByteArray()
        # Класс QDataStream помогаем перевести поток байтов в QIODevice
        out = QDataStream(block, QIODevice.ReadWrite)
        # Устанавливаем версию потока QDataStream
        out.setVersion(QDataStream.Qt_5_0)
        # Очищаем буфер
        out.writeUInt16(0)

        # Ждем пока соединение не будет готово для чтения
        clientConnection.waitForReadyRead()
        # Читаем входящие данные
        instr = clientConnection.readAll()
        # Декодируем байты из потока
        message = bytes(instr).decode('utf-8')

        # Теперь используем QDataStream и записываем масив байтов в него
        mess = message.encode('utf-8')
        out.writeUInt16(mess)
        out.device().seek(0) #Переводим курсор в начало
        out.writeUInt16(block.size() - 2) #Вычисляется размер строки

        # Отправляем QByteArray.
        clientConnection.write(block)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = Server()
    server.sessionOpened()
    sys.exit(server.exec_())