#!/usr/bin/python

# Written by GAD on 11/16/13 for the Advanced Class Lab

# This script is designed to run a single command through the eAPI
# It was first written to run "write", and was exanded to allow
# for the inclusion of an enable password. 
# It can be altered simply by changing the variables in the first few lines. 

# Usage: WriteMem.py <ip address> <enable-password>

# The command that this script runs: 
Command    = "show version"

# Print output? Some commands need it, some don't. For example, if 
# the goal is to capture the output of "show run", then the output
# will be needed. If the goal is to "write", then thr output likely isn't. 
# Choices are "Y" and "N"
PrintOutput = "Y"

# Username and password configured on the switch for eAPI
ScriptUser = "Username"
ScriptPass = "Password"

# Imports
import sys
import socket
import errno
from jsonrpclib import Server
##-------- Change this file for Rack-specific Variables ------##
from SiteVariables import *
##------------------------------------------------------------##

# Check validity of arguments: 

if len(sys.argv) > 1:
   sys.exit("Too many arguments - Exiting")

# This one reports on all switches, numbers 1-20

print
print "Switch      Device Type          Serial#     Memory  EOS"
print "-------------------------------------------------------------"
for SwitchNumber in range(1, NumStudents + 1):
   IP = "10.0.0." + str(SwitchNumber)

   if PrintOutput == "Y":
      print "Student-" + str(SwitchNumber).zfill(2) + ": ", 

   #Connect to Switch via eAPI
   switch = Server( "https://" + ScriptUser + ":" + ScriptPass + "@" + IP + "/command-api")

   # capture Connection problem messages
   # Map of erronos is here: http://www.python.org/doc//current/library/errno.html
   try:
      response = switch.runCmds( 1, [ Command ] )
   except KeyboardInterrupt:
       print "Caught Keyboard Interrupt - Exiting"
       sys.exit()
   except socket.error,ERR :
       ErrorCode = ERR[0]
       if ErrorCode == errno.ECONNREFUSED:
          print "    [Error " + str(ErrorCode) + "] Connection Refused! (Probably eAPI not configured)"
       elif ErrorCode == errno.ECONNREFUSED:
          print "    [Error] Connection Refused! (Probably eAPI not configured)"
       elif ErrorCode == errno.EHOSTUNREACH:
          print "    [Error] No Route to Host    (No Pwr | Rebooting | Aboot)"
       elif ErrorCode == errno.ECONNRESET:
          print "    [Error " + str(ErrorCode) + "] Connection RST by peer (Restart eAPI)"
       else:
          # Unknwon error - report number and error string (should capture all)
          print "    [Error " + str(ErrorCode) + "] " + ERR[1]
          #raise ERR;
   else:
      if PrintOutput == "Y":
        print response[0][ "modelName" ].ljust(20),
        print response[0][ "serialNumber" ],
        print response[0][ "memTotal" ], 
        print response[0][ "version" ] 

