import sys
import json
from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtWidgets import (QApplication, QMessageBox, QPushButton,QMainWindow,QVBoxLayout,QWidget,QLabel,QFormLayout)
from PyQt5.QtCore import Qt
from Apps.PrintLocal import *
import threading
import ctypes
from Minor import configs
from Minor.http_api import RequestsApi
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
import subprocess

locker_base_url =  "https://mfg-grab-api.minordigital.com" #"http://api-dev.keyspace.tech:3000"
# github = RequestsApi("https://api.github.com", headers={"Authorization": "token abcdef"})
# r = github.get("/user", headers={"Accept": "application/json"})
# print(r.text)

lockerClient = RequestsApi(locker_base_url)

# class Messenger(object):
#     def __init__(self):
#         super(Messenger, self).__init__()
#         self.TCP_HOST = "127.0.0.1"  # QtNetwork.QHostAddress.LocalHost
#         self.TCP_SEND_TO_PORT = 7011
#         self.pSocket = None
#         self.listenServer = None
#         self.pSocket = QtNetwork.QTcpSocket()
#         self.pSocket.readyRead.connect(self.slotReadData)
#         self.pSocket.connected.connect(self.on_connected)
#         self.pSocket.error.connect(self.on_error)

#     def slotSendMessage(self):
#         self.pSocket.connectToHost(self.TCP_HOST, self.TCP_SEND_TO_PORT)

#     def on_error(self, error):
#         if error == QtNetwork.QAbstractSocket.ConnectionRefusedError:
#             print(
#                 'Unable to send data to port: "{}"'.format(
#                     self.TCP_SEND_TO_PORT
#                 )
#             )
#             print("trying to reconnect")
#             QtCore.QTimer.singleShot(1000, self.slotSendMessage)

#     def on_connected(self):
#         cmd = "Hi there!"
#         print("Command Sent:", cmd)
#         ucmd = unicode(cmd, "utf-8")
#         self.pSocket.write(ucmd)
#         self.pSocket.flush()
#         self.pSocket.disconnectFromHost()

#     def slotReadData(self):
#         print("Reading data:", self.pSocket.readAll())
#         # QByteArray data = pSocket->readAll();


class Client(QtCore.QObject):
    def SetSocket(self, socket):
        self.socket = socket
        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_connected)
        self.socket.readyRead.connect(self.on_readyRead)
        print(
            "Client Connected from IP %s" % self.socket.peerAddress().toString()
        )

    def on_connected(self):
        print("Client Connected Event")

    def on_disconnected(self):
        print("Client Disconnected")

    def on_readyRead(self):
        msg = self.socket.readAll()
        print(type(msg), msg.count())
        print("Client Message:", msg)
        msgByte = msg.data()
        #print(type(msgByte))
        msgStr = msgByte.decode('ascii')
        #print(msgStr)
        capture = json.loads(msgStr)
        #print(capture)
        #print(globals()['ex'])
        #print(dir(globals()['ex']))
        win = globals()['ex'] #ex
        win.setPrinter(configs.printer["name"])
        win.setChannel(capture['channel'])
        win.setOrder(capture['order'])
        win.setSdm(capture['sdm'])
        win.setChannel(capture['channel'])
        win.setTranTime(capture['datetime'])

        #make locker for request
        response = lockerClient.get('/',verify=False)
        print(response.text)


class Server(QtCore.QObject):
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self)
        self.TCP_LISTEN_TO_PORT = 7011
        self.server = QtNetwork.QTcpServer()
        self.server.newConnection.connect(self.on_newConnection)

    def on_newConnection(self):
        while self.server.hasPendingConnections():
            print("Incoming Connection...")
            self.client = Client(self)
            self.client.SetSocket(self.server.nextPendingConnection())

    def StartServer(self):
        if self.server.listen(
            QtNetwork.QHostAddress.Any, self.TCP_LISTEN_TO_PORT
        ):
            print(
                "TCP Server is listening on port: {}".format(
                    self.TCP_LISTEN_TO_PORT
                )
            )
        else:
            print("TCP Server couldn't wake up")


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        self.setWindowTitle("DeliveryTracker (Minor version 1.0) Copy right 2022")
        self.resize(300, 100)
        self.setFixedSize(300, 100)
        #self.setGeometry(900, 500, 400, 200)

        self.cw = QWidget(self)

        self.printerLabel1 = QLabel("Printer : ")
        self.printerLabel2 = QLabel("")

        # self.statusLabel1 = QLabel("Printer log status : ")
        # self.statusLabel2 = QLabel("")

        self.channelLabel1 = QLabel("Channel : ")
        #self.channelLabel1.setAlignment(Qt.AlignLeft)
        self.channelLabel2 = QLabel("")
        #self.channelLabel2.setAlignment(Qt.AlignLeft)

        self.orderLabel1 = QLabel("Order : ")
        self.orderLabel2 = QLabel("")

        self.sdmLabel1 = QLabel("SDM : ")
        self.sdmLabel2 = QLabel("")

        self.tranTimeLabel1 = QLabel("Tran time : ")
        self.tranTimeLabel2 = QLabel("")

        self.formlayout = QFormLayout(self.cw)
        self.formlayout.addRow(self.printerLabel1, self.printerLabel2)
        #self.formlayout.addRow(self.statusLabel1, self.statusLabel2)
        self.formlayout.addRow(self.channelLabel1, self.channelLabel2)
        self.formlayout.addRow(self.orderLabel1, self.orderLabel2)
        self.formlayout.addRow(self.sdmLabel1, self.sdmLabel2)
        self.formlayout.addRow(self.tranTimeLabel1, self.tranTimeLabel2)

        self.cw.setLayout(self.formlayout)
        self.setCentralWidget(self.cw)

        # self.uiConnect = QPushButton("Connect")
        #
        # # layout
        # self.layout = QVBoxLayout()
        # self.layout.addWidget(self.uiConnect)
        # self.widget = QWidget()
        # self.widget.setLayout(self.layout)
        # self.setCentralWidget(self.widget)

        # Connections
        #self.uiConnect.clicked.connect(self.setup)

    def setup(self):
        self.server = Server()
        self.server.StartServer()

        #self.tcp = Messenger()
        #self.tcp.slotSendMessage()

    def setPrinter(self, text):
        self.printerLabel2.setText(text)

    def setPrintJobStatus(self, text):
        self.statusLabel2.setText(text)

    def setChannel(self,text):
        #print(self.channelLabel2)
        self.channelLabel2.setText(text)
    def setOrder(self,text):
        #print(self.orderLabel2)
        self.orderLabel2.setText(text)
    def setSdm(self,text):
        #print(self.sdmLabel2)
        self.sdmLabel2.setText(text)
    def setTranTime(self,text):
        #print(self.tranTimeLabel2)
        self.tranTimeLabel2.setText(text)

##########################################
######## Thread of start Print Job #######
##########################################

class thread_with_exception(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def loopForPrint(self):
        prt = PrintLocal()
        # prt.stop_threads = False
        prt.printjob_listener()

    def run(self):

        # target function of the thread class
        try:
            self.loopForPrint()
            #while True:
            #    print('running ' + self.name)
        finally:
            print('PrintJob Event has ended')

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

##########################################
######## MAIN APPLICATION          #######
##########################################
def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)

if __name__ == "__main__":
    
    #CHECKING THE KEY BEFORE STARTUP
    key = "TLUKyqJD58LnXv286GeYVwQIHgnbeHUK_Xs9lA93FGA="
    rows = dbclient.getKey()
    encryted_uuid = rows[0][0]  #print(rows[0][0])
    errorToken = ''
    try:
        decrypted_uuid = decrypt(bytes.fromhex(encryted_uuid),key).decode()
        hwid = str(subprocess.check_output('wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip()
        if hwid != decrypted_uuid:
            print(errorToken + 'Key installed is invalid for MINOR')
            sys.exit()
        else:
            pass
            # print(decrypted_uuid)
            # print(hwid)
    except ValueError:
        errorToken = 'InvalidToken'
        print(errorToken + '.Key installed is invalid for MINOR')
        sys.exit()
    except InvalidToken:
        errorToken = 'InvalidToken'
        print(errorToken + '.Key installed is invalid for MINOR')
        sys.exit()

    #STARTING TREAD
    t1 = thread_with_exception('Thread PrintJOB') #Thread 1
    t1.start()

    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    ex.setup() # to start server ,PORT 7011
    app.exec_()


    time.sleep(2)
    t1.raise_exception()
    t1.join()

    #print(dir())
    #print(globals())
    #print(locals())

    sys.exit()

#######################################################
#main()
    # stop_threads = False
    # thread1 = threading.Thread(target=loopForPrint)
    # thread1.start()