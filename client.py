import os
import sys
from select import select
import random
import time
timeout=7
timeout1=9
if len(sys.argv) < 4:
    print "Usage: python client.py <CLIENT_PORTS_RANGE> <PROXY_PORT> <END_SERVER_PORT>"
    print "Example: python client.py 20010 20000 19990-19999"
    raise SystemExit

CLIENT_PORT = sys.argv[1]
PROXY_PORT = sys.argv[2]
SERVER_PORT = sys.argv[3]

D = {0: "GET", 1:"POST"}
t=''
f=''
while True:
    filename = "%d.data" % (int(random.random()*9)+1)
    METHOD = D[int(random.random()*len(D))]
    t=''
    f=''
    val=int(raw_input("Enter 1 for https and any value for http: "))
    if val==1:
    	print("Enter address: ")
    	addr=raw_input()
    	os.system("curl --request GET --proxy 127.0.0.1:%s --local-port %s %s " % (PROXY_PORT, CLIENT_PORT, addr ))
    	time.sleep(10)
    	continue
    print "\nDo you want authentication: y/n"
    rlist, _, _ = select([sys.stdin], [], [], timeout)
    if rlist:
    	s = sys.stdin.readline()
    	print s.split('\n')[0]
    	if(s.split('\n')[0]=="y"):
    		print "Enter Username password"
    		rlist, _, _ = select([sys.stdin], [], [], timeout1)
    		if rlist:
    			t = sys.stdin.readline()
    			t=t.split('\n')[0]
    			f=t.split(' ')
   	if(len(f)==2):
   		os.system("curl --request %s --proxy %s:%s@127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s " % (METHOD, f[0], f[1], PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename ))
   		time.sleep(10)
   		continue
   	else:
   		print "wrong format not authenticated"
    	os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s " % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename ))
    time.sleep(10)
