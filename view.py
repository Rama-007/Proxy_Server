import socket
import threading
import signal
import sys
import time
import base64
import ssl
import urllib2
for i in range(5000,20000):
	starttime=time.time()
	opener = urllib2.build_opener(
                urllib2.HTTPHandler(),
                urllib2.HTTPSHandler(),
                urllib2.ProxyHandler({'http': 'http://127.0.0.1:'+str(i)}))
	urllib2.install_opener(opener)
	data = urllib2.urlopen('https://www.youtube.com/watch?v=PIuyzyR-S6I').read()
	print data