import time
import sys
import socket
import serial

timeout=socket._GLOBAL_DEFAULT_TIMEOUT

ser = serial.Serial()
ser.baudrate = 1200
ser.bytesize = 7
ser.parity = 'E'
ser.port = 'COM6'

IAC = False	#Bool de commande IAC Byte  - 255
DO = False	#Bool de commande DO Byte   - 253
WILL = False	#Bool de commande WILL Byte - 251
SB = False	#Bool de commande SB Byte   - 250
NL = False	#Bool de Mise en page Byte  - 238
CR = False	#Bool de commande CR Byte   - 13
ECHO = False	#Bool de commande ECHO Byte - 1
SBi = 0		#Int d'état de la cmde de subnégociation
NLi = 0		#Int d'état de la cmde de mise en page


def Telnet (b):
	global IAC, WILL, SB, DO, ECHO, CR, NL
	global SBi, NLi
	if IAC == False and b == 255:
		IAC = True			
		print ">IAC"
		FILE.write('-IAC-')
		return None
	#----------------------------------------FONCTIONS IAC-------------------------------------------------------+
	elif IAC and SB == False:			
		if b == 250:							#SB - Subnegotiation of the indicated option follows.
			SB = True
			SBi = 0
			print ">SB"
			FILE.write('-SB-')
		elif b == 251:							#WILL - Indicates the desire to begin performing, or confirmation that you are now performing, the indicated option.
			WILL = True
			print ">WILL"
			FILE.write('-WILL-')
		elif b == 253:							#DO - Indicates the request that the other party perform, or confirmation that you are expecting the other party to perform, the indicated option.
			DO = True
			print ">DO"
			FILE.write('-DO-')
		IAC = False
		return None
	#----------------------------------------FONCTIONS SB-------------------------------------------------------+
	elif SB:
		if b == 24:								#Terminal Type
			SBi = 24
			FILE.write('-SBi-')
		elif b == 240:							#SE - End of subnegotiation parameters.
			if SBi == 24:
				sock.send(b"\xFF\xFA\x18\x00\x4D\x49\x4E\x49\x54\x45\x4C\xFF\xF0")
				         #   255-250-024-000- M - I - N - I - T - E - L -
				FILE.write('-SE-')
			SB = False
			IAC = False
		return None
	#----------------------------------------FONCTIONS DO-------------------------------------------------------+
	elif DO:
		if b == 31:								#Window Size
			sock.send(b"\xFF\xFB\x1F")			#255-251-31
			sock.send(b"\xFF\xFA\x1F\x00\x28\x00\x18")
			sock.send(b"\xFF\xF0")				#255-240
		DO = False
		return None
	#----------------------------------------FONCTIONS WILL-----------------------------------------------------+
	elif WILL:
		if b == 1:								#ECHO
			sock.send(b"\xFF\xFB\x01")			#255-251-1
			WILL = False
			print ">ECHO"
			FILE.write('-ECHO-')
		WILL = False
		return None
	elif NL:
		if b == 128:
			NLi = 1
		if b == 134 and NLi == 1:				#RETOUR ARRIERE
			NLi = 0
			NL = False
			#ser.write(b"\x0D\x1B\x5B\x42")
		if b == 130 and NLi == 1:				#NEW-PAGE
			NLi = 0
			NL = False
			ser.write(b"\x1B\x5B\x32\x4A")
			ser.write(b"\x1B\x5B\x31\x3B\x31\x48")
		return None
	elif b == 238:
		NL = True
		print ">NL"
		FILE.write('-NL-')
	else :		
		if CR:
			if b == 10:							#Line Feed
				CR = False
				ser.write(b"\x0D\x1B\x5B\x42")
			return None
		elif b == 1:
			return None
		elif b == 13:							#Carriage Return
			CR = True
			return None
		else :
			return b

		







time.sleep(3)


ser.open()
ser.write(b"\x1B\x5B\x32\x4A")
ser.write(b"\x1B\x5B\x31\x3B\x31\x48")

timeout=socket._GLOBAL_DEFAULT_TIMEOUT

sock = socket.create_connection(("127.0.0.1", 5410), timeout)

CMD = False
data = False

FILE=open("G:\\output.txt", "a")

while True:
	try:
		bufferT = sock.recv(1024)
	except socket.error, e:
		err = e.args[0]
		if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
			continue
		else:
			print e
			sys.exit(1)
	else:
		for t in bufferT:
			b = ord(t)
			FILE.write(str(b))
			FILE.write('.')
			#print "Telnet : "
			#print b
			if Telnet(b) != None :
				ser.write(chr(b))
				print b
				
	
	while ser.inWaiting() > 0:
		b = ord(ser.read(1))								# defini b en tant que valeur decimale du byte recus
		print "ser : "
		print b
		if CMD :
			if b == 65:
				sock.send(b'\x0D')
				CMD = False
		elif b == 19 :
			CMD = True
		else :
			sock.send(chr(b))

FILE.close()
