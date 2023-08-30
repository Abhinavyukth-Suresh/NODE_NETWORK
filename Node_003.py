import socket
import numpy as np
import pickle
import os
import threading
import requests
import time
import subprocess
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication,QLineEdit,QMainWindow,QPushButton,QToolBar
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

__version__ = "0.0.2"

with open(__file__,"r") as w:
    DATA = w.read()
    
class Node(object):
    baseport = 12000
    protocol_001_clTimeout = 0.1
    BaseProtocolTimeOut = 2
    
    def __init__(self):
        self.http_url = "https://www.google.com/" #temprorily
        self.httpServerAccess = False
        self.run = True
        self.max_nodes = 10
        self.address = socket.gethostbyname(socket.gethostname())
        self.base_address = '.'.join(self.address.split('.')[:-1])
        self.port = Node.baseport + int(self.address.split('.')[-1])
        self.nodeID = int(self.address.split('.')[-1])
        self.nodes = dict() 
        self.node_info = []
        self.netstat = self.SUBROUTINE_PROTOCOL_000()
        self.nodeVec = np.random.random()
        self.RootNode = False
        self.RootNodeAddr = None
        self.NoRootNode = True
        self.conode = (self.address,self.netstat,self.nodeVec)
        self.UDPServer = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.UDPClient = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.UDPServer.bind((self.address,self.port))
        self.n_nodes = 0
        self.browser = None
        self.PROTOCOLS = {
            "000":self.SUBROUTINE_PROTOCOL_000,
            "001":self.SUBROUTINE_HANDLESERVERCALL_PROTOCOL001,
            "003":self.PROTOCOL_003,

            "010":self.PROTOCOL_010,
            "011":self.PROTOCOL_011,
            "012":self.PROTOCOL_012,
            "014":self.PROTOCOL_014,
            }
        self.UDPServerThread = threading.Thread(target=self.UDPSERVER_CALL_ROUTINES)
        self.UDPServerThread.start()

        self.BrowserCheck = threading.Thread(target=self.SUBROUTINE_006)
        self.BrowserCheck.start()
        if (not self.netstat)&self.NoRootNode:
            self.ReTryNetworkThread = threading.Thread(target=self.SUBROUTINE_004)
            self.ReTryNetworkThread.start()
        self.SUBROUTINE_PROTOCOL_001(self.address)
        self.update_req = 1#False
        self.updated_data = "None"
        


        
    def UDPSERVER_CALL_ROUTINES(self):
        try:
            print(self.address,self.port)
            while self.run:
                data,addr = self.UDPServer.recvfrom(4096)
                data = pickle.loads(data)
                [header,_] = data
                print("data recieved",header)
                self.PROTOCOLS[header["protocol"]](data,addr)
        except OSError:
            return 0
            
    def SUBROUTINE_PROTOCOL_000(self):
        try:
            socket.create_connection(("1.1.1.1", 53)) #google.com ::may change to -
            return True                               # - http server address
        except OSError:
            pass
        return False

    def HANDLE_REQUEST(self,data,addr):
        [header,_] = data
        threading.Thread(target=self.PROTOCOLS[header["protocol"]],args=(data,addr,))
        
    def SUBROUTINE_HANDLESERVERCALL_PROTOCOL001(self,data,addr):
        [header,body] = data
        
        #SUBROUTINE PROGRAM UPDATE
        if header['code']==3: #sending updated node
            msg = [{"protocol":"001","code":3},DATA]
            bytes_msg = pickle.dumps(msg)
            self.UDPServer.sendto(bytes_msg,addr)

        
        [conodes,netstat,nodeVec,version] = body
        #SUBROUTINE PROGRAM UPDATE
        if version>__version__:
            msg = [{"protocol":"001","code":2},0]
            bytes_msg = pickle.dumps(msg)
            self.UDPServer.sendto(bytes_msg,addr)
            msg = self.UDPServer.recvfrom(24000)
            while msg[1]!=addr:
                msg = self.UDPServer.recvfrom(24000)
            msg = [{"protocol":"001","code":1},__version__]
            bytes_msg = pickle.dumps(msg)
            data = pickle.loads(msg[0])
            self.updated_data = data[1]
            with open(__file__,"w") as w:
                w.write(data[1])
            #restart
            
            self.update_req = True
            
        msg = [{"protocol":"001","code":1},__version__]
        bytes_msg = pickle.dumps(msg)
        self.UDPServer.sendto(bytes_msg,addr)

        node = (addr[0],netstat,nodeVec)
        self.UPDATE_NODE_PROTOCOL({addr[0]:node})
        self.UPDATE_NODE_PROTOCOL(conodes)
        if not (self.address==header["init"]):
            t = threading.Thread(target=self.SUBROUTINE_PROTOCOL_001,args=(header["init"],))
            t.start()
        try:
            del self.nodes[self.address]
        except KeyError:
            pass
        self.n_nodes = len(self.nodes)
        return self.SUBROUTINE_002()
        
    def SUBROUTINE_PROTOCOL_001(self,init_addr):
        self.UDPClient.settimeout(Node.protocol_001_clTimeout)
        msg = [{"protocol":"001","code":1,"init":init_addr},[self.nodes,self.netstat,self.nodeVec,__version__]]
        bytes_msg = pickle.dumps(msg)
        i = self.nodeID+1
        nex = True
        while nex:
            i = i%self.max_nodes
            addr = self.base_address+'.'+str(i)
            port = Node.baseport + i
            try:
                self.UDPClient.sendto(bytes_msg,(addr,port))
                [header,version] = pickle.loads(self.UDPClient.recvfrom(2048)[0])
                if header["code"]==2:
                    msg = [{"protocol":"001","code":2,"return":True},DATA]
                    bytes_msg = pickle.dumps(msg)
                    self.UDPClient.sendto(bytes_msg,(addr,port))
                    self.UDPClient.recvfrom(4096)
                elif header["code"]==1:
                    if version > __version__:
                        msg = [{"protocol":"001","code":3,"return":True},0]
                        bytes_msg = pickle.dumps(msg)
                        self.UDPClient.sendto(bytes_msg,(addr,port))
                        data = pickle.loads(self.UDPClient.recvfrom(24096)[0])
                        with open(__file__,"w") as w:
                            w.write(data)
                        #restart
                nex = False
            except OSError as e:
                    pass
            i+=1
        self.UDPClient.settimeout(Node.BaseProtocolTimeOut)


    def SUBROUTINE_002(self):
        self.RootNode = False
        nodes = np.array(list(self.nodes))
        network = np.array([i[1] for i in list(self.nodes.values())])
        nodeVec = np.array([i[2] for i in list(self.nodes.values())])
        sel_node = nodes[network>0]
        sel_Vec = nodeVec[network>0]
        max_sel = 0
        if not np.array_equal(np.array([]),sel_Vec):
            max_sel = np.max(sel_Vec)
            if (max_sel<self.nodeVec)&self.netstat:
                self.RootNode = True
                self.RootNodeAddr = self.address,self.port
                self.NoRootNode = False
                return self.SUBROUTINE_003()
            node = sel_node[np.argmax(sel_Vec)]
            self.RootNodeAddr = node,PortHashing(node)
            self.NoRootNode = False

    def SUBROUTINE_003(self):

        #NOT IMPLEMENTED ERROR
        if requests.get(self.http_url).status_code == 200:
            self.httpServerAccess

    def SUBROUTINE_004(self): 
        while (self.NoRootNode)&self.run:
            self.netstat = self.SUBROUTINE_PROTOCOL_000()
            if self.netstat:
                return self.SUBROUTINE_005()

    def SUBROUTINE_005(self):
        self.run = False
        self.UDPServer.close()
        return self.__init__()





'''              
#send file,recv file
#broadcast
'''
def PortHashing(addr,baseport=Node.baseport):
    return baseport + int(addr.split('.')[-1])
    
t = time.time()
n = Node()
print(time.time()-t)

if n.update_req:
    data = n.updated_data
    del n
    #exec(data)
    os.system("python "+repr(__file__))
    
