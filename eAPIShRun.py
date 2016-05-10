#!/usr/bin/python

import time
from jsonrpclib import Server

userName   = 'Username'
password   = 'Password'
IP         = '10.0.0.20'

switch = Server( "https://" + userName + ":" + password + "@" + IP + "/command-api" )

shoRun = switch.runCmds( 1, [ "enable", "show running-config" ] , 'text')
shoHost = switch.runCmds( 1, [ "show hostname" ] )

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
fileName = shoHost[0]["hostname"] + '_' + timestamp
print 'Saving output to ' + fileName
ConfigFile = open(fileName, 'w')
ConfigFile.write( shoRun[1]["output"] )
ConfigFile.close()
