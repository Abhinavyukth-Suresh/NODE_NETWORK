"""    THE FROG-LEAP ROUTING NETWORK (FRONET)
#interconnected communication between different systems in a network within sub net   """

import socket
import os
import sys
import subprocess
import pickle
import numpy as np
import requests
import threading
import importlib
from os.path import basename
import pdb

__version__ = "0.0.5"

def portHashing(address):
    return int(address.split('.')[-1])+Node.baseport

def networkStatus():
    try:
        socket.create_connection(("1.1.1.1", 53)) 
        return True                              
    except OSError:
        pass
    return False

def create_node(node):
    return node()

################################   NODE NETWORK BASE_CLASS   ##################################

class Node():
    baseport = 12000
    TIMEOUT = 0.85
    PROTOCOL_000_TIMEOUT = 0.15
    MAX_NODES = 20 #60
    
    def __init__(self):
        self.address = socket.gethostbyname(socket.gethostname())
        self.port = int(self.address.split('.')[-1])+Node.baseport
        self.port_id = int(self.address.split('.')[-1])
        self.baseAddress = '.'.join(self.address.split('.')[:-1])+'.'
        self.nodes = dict()
        self.netstat = networkStatus()
        self.server_recv_size = 4096
        self.RootNode = False
        self.RootNodeAddr = None
        self.NextNodeAddr = None
        self.NodeVec = np.random.random()
        self.TCPServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.TCPClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.TCPServer.bind((self.address,self.port))
        self.PROTOCOLS = {
                    "000":self.PROTOCOL_000_SUBROUTINE,
                    "001":self.PROTOCOL_001_SUBROUTINE,
                    "002":None,
                    "201":self.PROTOCOL_201_SUBROUTINE,
                    "211":self.PROTOCOL_211_SUBROUTINE
                    }
        self.PROTOCOL_000_SUBROUTINE(pass_to=True,thread=True)
        self.SERVER_SUBROUTINE()

    def SERVER_SUBROUTINE(self):
        try:
            run = True
            while run:
                conn,addr = self.TCPServer.listen(Node.MAX_NODES)
                threading.Thread(target=self.SERVER_HANDLE_SUBROUTINE,args=(conn,addr,)))
        except Exception as e:
            return 0

    def SERVER_HANDLE_SUBROUTINE(self,conn,addr):
        [header,body] = pickle.loads(conn.recv(4096))
        self.PROTOCOLS[header['protocol']](conn,header=header,data=body)

    def POST_PROTOCOL_BASEHANDLER(self,addr,msg,recv_size=4096,byte=False):
        if not byte:msg = pickle.dumps(msg)
        self.UDPClient.send(msg)
        data,addr = self.UDPClient.recvfrom(recv_size)
        data = pickle.loads(data)
        return data[0],data[1] \
#############################   NETWORK INITIALZING SUBROUTINES   ##############################

    #NETWORK INSTANTIATION PROTOCOL SUBROUTINE    
    def PROTOCOL_000_SUBROUTINE(self,pass_to=False,conn=None,header=None,data=None,thread=True):
        if thread:
            thread = threading.Thread(target=self.PROTOCOL_000_SUBROUTINE,args=(pass_to,addr,header,data,False,))
            thread.start()
            return 0
        
        #TCP CLIENT
        if pass_to:
            if self.NextNodeAddr is None:
                i = self.port+1
                if addr is None:addr = self.address #self initialized chain
                #else:addr = addr
                msg = [{"protocol":"000","init":addr,"code":0},[self.nodes,self.netstat,self.NodeVec,__version__]]
                byte_msg = pickle.dumps(msg)
                i=self.port_id+1;del msg;
                self.TCPClient.settimeout(Node.PROTOCOL_000_TIMEOUT)
                while i!=self.port_id:
                    try:
                        print("port :",i,self.port_id)
                        address = self.baseAddress + str(i)
                        header,[nodes,netstat,vec,version] = picke.loads()
                        self.nodes.update({address:[address,netstat,vec]})
                        self.nodes.update(nodes)
                        if self.address in self.nodes:
                            del self.nodes[self.address]
                        if version>__version__:
                            msg = [{"protocol":"000","init":self.address,"code":1},0]
                            _,body = self.POST_PROTOCOL_BASEHANDLER(msg=msg,addr=address,recv_size=30_000)
                            with open(str(__file__),'w') as f:
                                f.write(body)
                            ###     AUTO UPDATE    ###
                            return self.SUBROUTINE_101()
                        
                        self.UDPClient.settimeout(Node.TIMEOUT)
                        return self.SUBROUTINE_002()
                    except Exception as e:
                        print("protocol 000 exception:",e)
                    
                    i=(i+1)%Node.MAX_NODES
                self.TCPClient.settimeout(Node.TIMEOUT)
                return 0
            else:
                if header is None:header =  {"init":self.address}
                msg = [{"protocol":"000","init":header["init"],"code":0},[self.nodes,self.netstat,self.NodeVec,__version__]]
                byte_msg = pickle.dumps(msg)
                self.UDPClient.sendto(byte_msg,(self.NextNodeAddr,portHashing(self.NextNodeAddr)))
            return 0
        
        #SERVER HANDLE
        elif header["code"]==0:
            msg = [{"protocol":"000","init":addr[0],"code":0},[self.nodes,self.netstat,self.NodeVec,__version__]]
            byte_msg = pickle.dumps(msg)
            self.UDPServer.sendto(byte_msg,addr)
            [nodes,ns,nv,v] = data
            self.nodes.update({addr[0]:[addr[0],ns,nv]})
            self.nodes.update(nodes)
            if self.address in self.nodes:
                del self.nodes[self.address]
            if header["init"]!=self.address:
                return self.PROTOCOL_000_SUBROUTINE(addr=addr[0],header=header,pass_to=True)
            return 0

        #SEND UPDATE
        elif header["code"]==1:
            with open(str(__file__),'r') as f:
                text = f.read()

            msg = [{"protocol":"000","init":addr[0],"code":1},text]
            byte_msg = pickle.dumps(msg)
            self.UDPServer.sendto(byte_msg,addr)
            return 0

    #SUBROUTINE DECENTRAIZED ROOT NODE DESIGNATION
    def SUBROUTINE_002(self):
        #NextNodeAddr INIT
        nodes = np.array(list(self.nodes))
        node_list = list(self.nodes)
        ids = [int(i.split('.')[-1]) for i in nodes]
        idsc = ids.copy()
        idsc.sort()
        ids_arr = np.array(idsc)
        gr = ids_arr>self.port_id
        if np.any(gr):
            self.NextNodeAddr = self.baseAddress+str(ids_arr[gr][0])
        else:
            self.NextNodeAddr = self.baseAddress+str(idsc[0])
        #Root Node INIT
        self.RootNode = False
        network = np.array([i[1] for i in list(self.nodes.values())])
        nodeVec = np.array([i[2] for i in list(self.nodes.values())])
        sel_node = nodes[network>0]
        sel_Vec = nodeVec[network>0]

        if not np.array_equal(np.array([]),sel_Vec):
            max_sel = np.max(sel_Vec)
            if (max_sel<self.NodeVec)&self.netstat:
                self.RootNode = True
                self.RootNodeAddr = self.address,self.port
                return 0
            node = sel_node[np.argmax(sel_Vec)]
            self.RootNodeAddr = node,portHashing(node)
        return 0

    #SUBROUTINE AUTO UPDATE
    def SUBROUTINE_101(self): 
        self.UDPServer.close()
        self.UDPClient.close()
        mainmodname = basename(__file__)[:-3]
        module = importlib.import_module(mainmodname)
        importlib.reload(module)
        globals().update(vars(module))
        self.__init__()
        pdb.set_trace() ##debugger
        return 1

    #SUBROUTINE REST NETWORK
    def SUBROUTINE_100(self):
        self.UDPServer.close()
        self.UDPClient.close()
        self.__init__()
        return 0

    #NETWORK SHUTDOWN 
    def PROTOCOL_001_SUBROUTINE(self,addr,header={"init":"0"},data=0):
        msg = [{"protocol":"001","init":header["init"]},data]
        byte_msg = pickle.dumps(msg)
        self.UDPServer.sendto(byte_msg,addr)
        if self.NextNodeAddr is None:
            return 1
        self.UDPClient.sendto(byte_msg,(self.NextNodeAddr,portHashing(self.NextNodeAddr)))
        self.UDPClient.recvfrom(2048)
        self.UDPServer.close()
        self.UDPClient.close()
        return 1

################################   DATA TRANSFER PROTOCOLS   ##################################


    
################################   EXECUTION PROTOCOLS   ##################################


#############################   END NODE NETWORK ROUTINE DEF   ################################

#RUNNING NETWORK ON ->(*THIS) SYSTEM
if __name__ == '__main__':
    n = Node()   
