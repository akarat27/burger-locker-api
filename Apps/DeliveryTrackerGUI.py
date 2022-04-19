import base64
import sys
import logging
import json
from PyQt5 import QtCore, QtGui, QtNetwork
from PyQt5.QtWidgets import (QApplication, QMessageBox, QGroupBox,QGridLayout,
 QPushButton,QMainWindow,QVBoxLayout,QWidget,QLabel,QFormLayout,QStyleFactory,QPlainTextEdit,
 QFileDialog,)
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
        # win = globals()['ex'] #ex
        # win.setProgramStatus("State : Found a new order.")

    def on_disconnected(self):
        print("Client Disconnected")
        # win = globals()['ex'] #ex
        # win.setProgramStatus("State : Waiting for the next order.")

    def on_readyRead(self):
        msg = self.socket.readAll()
        #print(type(msg), msg.count())
        #print("Client Message:", msg)
        logging.info('POS:RECEIVEDATA,'+ ' ' + str(msg.count()) + ' bytes')
        msgByte = msg.data()
        #print(type(msgByte))
        msgStr = msgByte.decode('ascii')
        #print(msgStr)
        capture = json.loads(msgStr)
        print(capture)
        #print(globals()['ex'])
        #print(dir(globals()['ex']))
        if capture['channel'] is not None:
            win = globals()['ex'] #ex
            win.setPrinter(configs.printer["name"])
            win.setChannel(capture['channel'])
            win.setOrder(capture['order'])
            win.setSdm(capture['sdm'])
            win.setTranTime(capture['datetime'])
            logging.info('POS:RECEIVEDATA,'+ ' Channel ' + capture['channel'] + ',' + capture['order'] + ',' + capture['sdm']  )

            #make locker for request
            response = lockerClient.get('/',verify=False)
            print(response.text)
            #self.clearLabel()
            logging.info('LOCKERAPI:SEND,' + ' completed')
        else:
            logging.info('POS:RECEIVEDATA, Could not verify the channel of input data.')

    def clearLabel(self):
        win = globals()['ex'] #ex
        win.setPrinter("Waiting")
        win.setChannel("N/A")
        win.setOrder("N/A")
        win.setSdm("N/A")
        win.setChannel("N/A")
        win.setTranTime("N/A")

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

############### GUI #################
def on_export_clicked():
    alert = QMessageBox()
    alert.setWindowTitle('Meesage')
    alert.setText('Exporting log file is done!')

    win = globals()['ex']
    #print(win.logTextBox.widget)
    #print(win.logTextBox.export())

    filename = QFileDialog.getSaveFileName(win, 'Save Log', '',
                                             "Text Files (*.txt);;All Files (*)", 
                                             options=QFileDialog.DontUseNativeDialog)
    if filename == '':
       print("No file") 
    else:
       #print(filename)
       if filename[1] == 'Text Files (*.txt)' and filename[0][-4:] != '.txt':
           filename = filename[0] + '.txt'
       else:
           filename = filename[0]
       with open(filename, 'w') as fp:
            fp.writelines(win.logTextBox.export()) 
            alert.exec()
    

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
    
    def export(self):
        return self.widget.toPlainText()

class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        self.setWindowTitle("DeliveryTracker (Minor version 1.0) Copy right 2022")
        self.resize(650, 200)
        self.setFixedSize(650, 200)
        #self.setGeometry(900, 500, 400, 200)

        self.mainWidget = QWidget(self)
        # You can format what is printed to text box
        self.logTextBox = QTextEditLogger(self)
        #self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)
        
        #modified
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()

        self.mainLayout = QGridLayout(self.mainWidget)
        #self.mainLayout.addLayout(self.formlayout, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        self.mainLayout.addWidget(self.topRightGroupBox, 1, 1)

        #self.cw.setLayout(self.formlayout)
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        logging.info('MinorPrintServer has started.')
        logging.info('Waiting on next order ...')
        

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

    # def changeStyle(self, styleName):
    #     QApplication.setStyle(QStyleFactory.create(styleName))
    #     self.changePalette()

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Cuptured Order")
        # Create labels
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

        self.formlayout = QFormLayout() # self.cw
        self.formlayout.addRow(self.printerLabel1, self.printerLabel2)
        #self.formlayout.addRow(self.statusLabel1, self.statusLabel2)
        self.formlayout.addRow(self.channelLabel1, self.channelLabel2)
        self.formlayout.addRow(self.orderLabel1, self.orderLabel2)
        self.formlayout.addRow(self.sdmLabel1, self.sdmLabel2)
        self.formlayout.addRow(self.tranTimeLabel1, self.tranTimeLabel2)

        self.widget1 = QWidget()
        self.widget1.setLayout(self.formlayout)
        self.widget1.setMinimumSize(200,150)

        # flatPushButton = QPushButton("Flat Push Button")
        # flatPushButton.setFlat(True)

        layout = QVBoxLayout()
        layout.addWidget(self.widget1)
        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)   


    def createTopRightGroupBox(self):
        # self.statusLayout = QGridLayout()
        # self.statusLayout.addWidget(self.topLeftGroupBox, 1, 0)
        # self.statusLayout.addWidget(self.topRightGroupBox, 1, 1)

        self.topRightGroupBox = QGroupBox("Status")

        self.flatPushButton = QPushButton("Export")
        #flatPushButton = QPushButton(self.get_tray_icon(),"loadme")
        #self.flatPushButton.setFlat(True)
        self.flatPushButton.clicked.connect(on_export_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.logTextBox.widget)
        layout.addWidget(self.flatPushButton)
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)   

    def get_tray_icon(self):
        base64_data = '''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'''

        pm = QtGui.QPixmap()
        pm.loadFromData(base64.b64decode(base64_data))
        i = QtGui.QIcon()
        i.addPixmap(pm)
        return i
    
    def setProgramStatus(self, text):
        self.programStatus.setText(text)
    
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