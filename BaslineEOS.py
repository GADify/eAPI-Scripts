#!/usr/bin/python
# Written by GAD on 3/7/16 for simplified Lab Baselining

# Imports
import os.path, sys, socket, socket, errno, jsonrpclib, xmlrpclib
import time, curses, random
from threading import Thread

##-------- Change this file for Rack-specific Variables ------##
from SiteVariables import *
##------------------------------------------------------------##

# Check validity of arguments: 

numArgs = len(sys.argv)
if numArgs < 2:
   sys.exit("EOS Version required (ex: EOS-4.15.5M.swi) - Exiting")
if numArgs == 2:
   EOSVer = sys.argv[1] 
if numArgs > 2:
   sys.exit("Too many arguments - Exiting")

location = "/web/Lab/http/EOS/"
fileName = location + EOSVer

print "Chosen file: " + EOSVer

if not os.path.isfile(fileName):
  sys.exit(EOSVer + " not found.")

## This command is terrifically invasive. It cleares the config and reloads, forcing ZTP to run 
## Check to make sure we really want to do this. 

Forced = "no"
print
print 
print "This script does the following to all Student-xx switches in the lab: "
print "   1) Del all versions of EOS on flash:"
print "   2) Copies " + EOSVer + " to flash:"
print "   3) Sets the boot-config to " + EOSVer
print "   4) Issues the 'write erase' command (deletes startup-config)"
print "   5) Reloads the switch"
print
print "This will result in a default config running on " + EOSVer
print
print "NOTE: This can take a couple of minutes per switch!"
Forced = raw_input("This script installs and sets the boot-config to "+ EOSVer + ", \nthen write-erase/reloads: \n\nType 'yes' to continue: ")
if Forced != "yes":
   print
   print
   print "Command Canceled"
   print
   sys.exit()

# Test if given code exists on (this) server.

FileLocation = "/web/Lab/http/EOS/"
FileName = FileLocation + EOSVer
FileServer = "http://10.0.0.100/EOS/"

try:
   open(FileName)
except IOError:
   print
   sys.exit("EOS Version " + EOSVer + " Does not exist on this server. Exiting.\n\n")


def BaselineEOS(switchNumber):
      location = 28 
      IP = "10.0.0." + str(switchNumber)
   
      #print "Switch " + str(switchNumber).zfill(2) + ": ", 
   
      #Connect to Switch via eAPI
      target = "https://" + ScriptUser + ":" + ScriptPass + "@" + IP + "/command-api"
      switch = jsonrpclib.Server( target )
   
      # capture Connection problem messages
      # Map of erronos is here: http://www.python.org/doc//current/library/errno.html
      try:
         response = switch.runCmds( 1, 
            [ "enable" , 
              "configure",
              "delete EOS*.swi",
              "copy " + FileServer + EOSVer + " flash:",
              "boot system flash:" + EOSVer, 
              "write erase now", 
              "reload now"
            ], "text")

      except KeyboardInterrupt:
         print "Caught Keyboard Interrupt - Exiting"
         sys.exit()

      except socket.error,ERR :
          # Socket Errors
          ErrorCode = ERR[0]
          if ErrorCode == errno.ECONNREFUSED:
             win.addstr(switchNumber, location -15, "        [ Err " + str(ErrorCode) + ": No eAPI ]          ")
             refresh()
          elif ErrorCode == errno.EHOSTUNREACH:
             # Never hit with lower socket timeout
             win.addstr(switchNumber, location -15, "        [ Err " + str(ErrorCode) + ": Pwr off | Aboot ]  ")
             refresh()
          elif ErrorCode == errno.ECONNRESET:
             win.addstr(switchNumber, location -15, "        [ Err " + str(ErrorCode) + ": Con RST ]          ")
             refresh()

      except jsonrpclib.ProtocolError:
         # Capture eAPI errors
         result = jsonrpclib.loads( jsonrpclib.history.response )
         print result["error"]["message"]
         for error in result["error"]["data"][-1]["errors"]:
            print error

      except (xmlrpclib.ProtocolError, xmlrpclib.ResponseError), errormsg:
         # Capture XML Error (usually bad password)
         message = str(errormsg)
         message = message.replace(ScriptUser, "user")
         message = message.replace(ScriptPass, "pass")
         print message

      else:
         win.addstr(switchNumber, location, "[ Done ]")
         refresh()

screen = curses.initscr()
height, width = screen.getmaxyx()
win = curses.newwin(height, width, 0, 0)
#curses.use_default_colors()
#curses.start_color()
#CYAN_TEXT = 1
#curses.init_pair(CYAN_TEXT, curses.COLOR_CYAN, curses.COLOR_BLACK)

def refresh():
   # The sleep fixes threads mashing other threads cursor positions
   secs = random.uniform(0,0.5)
   time.sleep(secs)
   win.addstr(22,0,"")
   screen.refresh()
   win.refresh()
   # Since called in threads, each thread must endwin()
   curses.endwin()

def main(screen):

   for x in range(20):
      win.addstr(x+1,1,"Student-" + str(x+1).zfill(2) + "  Init Baseline: [  ..  ] ")
   win.addstr(22,0,"   Baseline takes ~1m.  'Done' means reboot initiated.")
   win.addstr(23,0,"   New Baseline code will be " + EOSVer)
   refresh()


   for switchNumber in range(1, NumStudents + 1):
      t = Thread(target=BaselineEOS, args=(switchNumber,))
      t.start()

   curses.endwin()

try:
   curses.wrapper(main)
except KeyboardInterrupt:
   curses.endwin()
   print "Caught Keyboard Interrupt - Exiting"
   sys.exit()
