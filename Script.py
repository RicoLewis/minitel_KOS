"""
TODO :
Ajouter un comteur de position x pour éviter les doubles saut de ligne
"""

import time
import sys
import socket
import serial
import binascii

timeout=socket._GLOBAL_DEFAULT_TIMEOUT

ser = serial.Serial()
ser.baudrate = 1200
ser.bytesize = 7
ser.parity = 'E'
ser.port = 'COM6'

IAC = False		#Bool de commande IAC Byte  - 255
DO = False		#Bool de commande DO Byte   - 253
WILL = False	#Bool de commande WILL Byte - 251
SB = False		#Bool de commande SB Byte   - 250
NL = False		#Bool de Mise en page Byte  - 238
DC = False		#Bool de depl curseur Byte  - 134
CR = False		#Bool de commande CR Byte   - 13
ECHO = False	#Bool de commande ECHO Byte - 1
SBi = 0			#Int d'etat de la cmde de subnegociation
NLi = 0			#Int d'etat de la cmde de mise en page
x = 0
y = 0
HexString = ""

def Telnet (b):
	global IAC, WILL, SB, DO, ECHO, CR, NL
	global SBi, NLi,x ,y
	global HexString
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
			print ">SB"#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
			FILE.write('-SB-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		elif b == 251:							#WILL - Indicates the desire to begin performing, or confirmation that you are now performing, the indicated option.
			WILL = True
			print ">WILL"#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
			FILE.write('-WILL-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		elif b == 253:							#DO - Indicates the request that the other party perform, or confirmation that you are expecting the other party to perform, the indicated option.
			DO = True
			print ">DO"#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
			FILE.write('-DO-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		IAC = False
		return None
	#----------------------------------------FONCTIONS SB-------------------------------------------------------+
	elif SB:
		if b == 24:								#Terminal Type
			SBi = 24
			FILE.write('-SBi-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		elif b == 240:							#SE - End of subnegotiation parameters.
			if SBi == 24:
				sock.send(b"\xFF\xFA\x18\x00\x4D\x49\x4E\x49\x54\x45\x4C\xFF\xF0")
				         #   255-250-024-000- M - I - N - I - T - E - L -
				FILE.write('-SE-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
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
			print ">ECHO"#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
			FILE.write('-ECHO-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		WILL = False
		return None
	elif NL:
		if b == 128 and NLi == 0:
			NLi = 1
			FILE.write('-NL1-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		elif b == 134 and NLi == 1:				#Deplacement curseur
			DC = True
			NLi = 2
			FILE.write('-NL2-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		elif b == 130 and NLi == 1:				#NEW-PAGE
			NLi = 0
			NL = False
			ser.write(b"\x1B\x5B\x32\x4A")			#cmde d'effacement ecran Minitel
			ser.write(b"\x1B\x5B\x31\x3B\x31\x48")		#cmde de deplacement curseur Minitel Pos x1y1
		elif NLi == 2:
			x = b
			NLi = 3
			FILE.write('-NL3-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		elif NLi == 3:
			y = b
			#HexString = "1b5b"+str(y+31)+"3b"+str(x+31)+"48"
			HexString = "1b5b"+str(hex(y+49)[2:])+"3b"+str(hex(x+49)[2:])+"48"
			ser.write(binascii.unhexlify(HexString))
			NL = False
			NLi = 0
			FILE.write('-NL4-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
			FILE.write(HexString)#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		return None
	elif b == 238:
		NL = True
		print ">NL"#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		FILE.write('-NL-')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
	else :		
		if CR:
			if b == 10:							#Line Feed
				CR = False
				ser.write(b"\x0D\x1B\x5B\x42")		#CR + cmde de deplacement curseur Minitel vers le bas
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
ser.write(b"\x11")				#cmde d'affichage du curseur Minitel
ser.write(b"\x1B\x5B\x32\x4A")			#cmde d'effacement ecran Minitel
ser.write(b"\x1B\x5B\x31\x3B\x31\x48")		#cmde de deplacement curseur Minitel Pos x1y1

timeout=socket._GLOBAL_DEFAULT_TIMEOUT

sock = socket.create_connection(("127.0.0.1", 5410), timeout)

CMD = False
data = False

FILE=open("G:\\output.txt", "a")		#Fichier de LOG

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
			FILE.write(str(b))#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
			FILE.write('.')#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
			#print "Telnet : "
			#print b
			if Telnet(b) != None :
				ser.write(chr(b))
				print b#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
				
	
	while ser.inWaiting() > 0:
		b = ord(ser.read(1))
		print "ser : "#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		print b#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LOG
		if CMD :
			if b == 65:
				sock.send(b'\x0D')
				CMD = False
		elif b == 19 :
			CMD = True
		else :
			sock.send(chr(b))

FILE.close()
