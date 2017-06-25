import socket
import threading
import signal
import sys
import time
import base64
import ssl
import urllib2

config =  {
            "HOST_NAME" : "127.0.0.1",
            "BIND_PORT" : 20000,
            "MAX_REQUEST_LEN" : 1024,
            "CONNECTION_TIMEOUT" : 5
          }

cache = []
ctime = []
mtime = []
cache1 = []
ctime1 = []
cache2 = []
ctime2 = []
lock = threading.Lock()
class Server:
    

    def __init__(self, config):
        signal.signal(signal.SIGINT, self.shutdown)    
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   
        self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT'])) 
        self.serverSocket.listen(10)    
        self.__clients = {}


    def listenForClient(self):

        while True:
            (clientSocket, client_address) = self.serverSocket.accept()  
            d = threading.Thread(name=self._getClientName(client_address), target=self.proxy_thread, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()
        self.shutdown(0,0)


    def proxy_thread(self, conn, client_addr):
        

        request = conn.recv(config['MAX_REQUEST_LEN'])
        with open('http_log.txt', "w+") as f:
            f.write(request)
            f.close()
        print "hiiiiiiiiiii"
        ptime = time.time()
        #print ptime
        method_type = request.split()[0]
        ftime = time.ctime(ptime)
        ftime = ftime.split()
        ftime.append(ftime[4])
        ftime[4] = 'GMT'
        ftime = ' '.join(ftime)
        #print ftime

        ####basic authorization
        index=-1
        auth_flag=0
        black_flag=0
        cache_flag=0
        auth=request.split();
        for i,j in enumerate(auth):
            if j=="Proxy-Authorization:" :
                index=i+2
                break
        if index!=-1:
            f = open('authentication.txt', 'r')
            for line in f:
                line=line.split('\n')[0]
                hash_value=base64.encodestring(line)
                if hash_value==(auth[index]+'\n') :
                    auth_flag=1
                    break
            f.close()
        print auth_flag

        #### blacklisting
        f=open('blacklist.txt','r')
        content=f.readlines()
        content = [x.strip() for x in content]
        print content
        f.close()
        
        ####changing request line
        first_line = request.split('\n')[0]                   # parse the first line
        new_line = request.split('\n')
        new_first_line=new_line[0].split(" ")
        new1_first_line=new_first_line[1].split("/")
        final_line=new_first_line[0]+" /"+new1_first_line[3]+" "+new_first_line[2]
        #request1='\n'.join(request.split('\n')[2:])
        #request1=final_line+"\n"+request.split('\n')[1]+"\n"+"If-Modified-Since: Mon Apr  10 02:27:02 GMT 2017\n"+request1
        request1='\n'.join(request.split('\n')[1:])
        request1=final_line+"\n"+request1
        url = first_line.split(' ')[1]  
        filename = url.split('/')[3]                      # get url
        print url
        if filename=='':
            opener = urllib2.build_opener(
                urllib2.HTTPHandler(),
                urllib2.HTTPSHandler(),
                urllib2.ProxyHandler({'http': 'http://127.0.0.1:20000'}))
            urllib2.install_opener(opener)
            http_pos = url.find("://")          # find pos of ://
            if (http_pos==-1):
                temp = url
            else:
                temp = url[(http_pos+3):]
            with open('https_log.txt', "w+") as f:
                f.write('https://'+temp)
                f.close()
            data = urllib2.urlopen('https://'+temp).read()
            with open('https_log.txt', "w+") as f:
                f.write(data)
                f.close()
            conn.send(data)
            conn.close()
        else:
            lock.acquire()
            if url in cache1 and method_type == 'GET':
                index1 = cache1.index(url)
                if ptime - ctime1[index1] < 300:
                    if url in cache2:
                        index2 = cache2.index(url)
                        if url in cache:
                            cindex = cache.index(url)
                            ctime1[index1] = ctime2[index2]
                            ctime2[index2] = ctime[cindex]
                            ctime[cindex] = ptime
                        else:
                            cache_flag = 2
                            if len(cache) == 3:
                                cache.pop(0)
                                ctime.pop(0)
                                mtime.pop(0)
                            cache.append(url)
                            ctime.append(ptime)
                            mtime.append(ftime)
                    else:
                        cache2.append(url)
                        ctime2.append(ptime)
                else:
                    if url in cache2:
                        index2 = cache2.index(url)
                        if ptime - ctime2[index2] < 300:
                            if url in cache:
                                cindex = cache.index(url)
                                ctime1[index1] = ctime2[index2]
                                ctime2[index2] = ctime[cindex]
                                ctime[cindex] = ptime
                            else:
                                ctime1[index1] = ctime2[index2]
                                ctime2[index2] = ptime
                        else:
                            #if url in cache:
                            #   continue
                            #else:
                            if url not in cache:
                                ctime1[index1] = ptime
                                cache2.pop(index2)
                                ctime2.pop(index2)
                    else:
                        ctime1[index1] = ptime
            else:
                if method_type == 'GET':
                    cache1.append(url)
                    ctime1.append(ptime)
            if url in cache and cache_flag == 0 and method_type == 'GET':
                cache_flag = 1
                findex = cache.index(url)
                request1='\n'.join(request.split('\n')[2:])
                request1=final_line+"\n"+request.split('\n')[1]+"\n"+"If-Modified-Since: "+mtime[findex]+"\n"+request1
                #request1 = request1 + "\n" + "If-Modified-Since: " + mtime[findex] + "\n"
            lock.release()
            http_pos = url.find("://")          
            if (http_pos==-1):
                temp = url
            else:
                temp = url[(http_pos+3):]       

            port_pos = temp.find(":")           

            
            webserver_pos = temp.find("/")
            if webserver_pos == -1:
                webserver_pos = len(temp)

            webserver = ""
            port = -1
            if (port_pos==-1 or webserver_pos < port_pos):      # default port
                port = 80
                webserver = temp[:webserver_pos]
            else:                                               # specific port
                port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
                webserver = temp[:port_pos]
            
            for i in range(0,len(content)):
                if content[i]==str(port) and auth_flag==0:
                    black_flag=1
            totaldata = ''
            print black_flag
            print auth_flag
            if black_flag == 0 or auth_flag == 1 :
                try:
                    print request1
                    # create a socket to connect to the web server
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(config['CONNECTION_TIMEOUT'])
                    s.connect((webserver, port))
                    s.sendall(request1)                           # send request to webserver
                    while 1:
                        data = s.recv(config['MAX_REQUEST_LEN'])          # receive data from web server
                        if (len(data) > 0):
                            totaldata = totaldata + data                               # send to browser
                        else:
                            break
                    s.close()
                    if cache_flag == 0:
                        conn.send(totaldata)
                        with open('http_log.txt', "w+") as f:
                            f.write(totaldata)
                            f.close()
                    elif cache_flag == 2:
                        with open(filename, "w") as f:
                            f.write(totaldata)
                        conn.send(totaldata)
                        with open('http_log.txt', "w+") as f:
                            f.write(totaldata)
                            f.close()
                    elif cache_flag == 1:
                        if '200' in totaldata.split():
                            with open(filename,"w") as f:
                                f.write(totaldata)
                                conn.send(totaldata)
                            with open('http_log.txt', "w+") as f:
                                f.write(totaldata)
                                f.close()
                        elif '304' in totaldata.split():
                            print "Cache-hit"
                            with open(filename,"r") as f:
                                data = f.read()
                                conn.send(data)
                            with open('http_log.txt', "w+") as f:
                                f.write(data)
                                f.close()
                    conn.close()
                except socket.error as error_msg:
                    print 'ERROR: ',client_addr,error_msg
                    if s:
                        s.close()
                    if conn:
                        conn.close()
            else:
                conn.send('HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<!doctype html>\n<html>\n<body>\n<h1>Cannot access this domain<h1>\n</body>\n</html>\n')
                with open('http_log.txt', "w+") as f1:
                    f1.write('HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<!doctype html>\n<html>\n<body>\n<h1>Cannot access this domain<h1>\n</body>\n</html>\n')
                    f1.close()
                conn.close()
                sys.exit(0)


    def _getClientName(self, cli_addr):
        return "Client"


    def shutdown(self, signum, frame):
        self.serverSocket.close()
        sys.exit(0)


if __name__ == "__main__":
    server = Server(config)
    server.listenForClient()