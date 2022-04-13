'''
Created on Feb 19, 2021

@author: bayden
'''

import socket
from cserverops import Cserverops
from cprotocol import Cprotocol

if __name__ == '__main__':
    # create the server socket
    #  defaults family=AF_INET, type=SOCK_STREAM, proto=0, filno=None
    serversoc = socket.socket()
    
    # bind to local host:50000
    port = 50001
    serversoc.bind(("localhost",port))
                   
    # make passive with backlog=5
    serversoc.listen(5)
    
    # wait for incoming connections
    n = 0
    while n < 100:
        print("Listening on ", port)
        
        # accept the connection
        commsoc, raddr = serversoc.accept()
        
        # run the serverops
        sops = Cserverops()
        sops.sproto = Cprotocol(commsoc)
        sops.connected = True
        sops.run()
        n = n + 1
        

    # close the server socket
    serversoc.close()