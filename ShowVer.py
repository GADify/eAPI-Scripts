#!/usr/bin/env python

import curses
import time
import random
from threading import Thread
from jsonrpclib import Server
import errno
import socket

##-------- Change this file for Rack-specific Variables ------##
from SiteVariables import *
##------------------------------------------------------------##

def GetVersion(x):
   verLoc = 19
   IP = "10.0.0." + str(x)
   switch = Server( "https://" + ScriptUser + ":" + ScriptPass + "@" + IP + "/command-api" )
   # Results in Host Unreach never happening, but [ . ] means same thing 
   #         without waiting
   socket.setdefaulttimeout(3)
   try:
      response = switch.runCmds( 1, [ "show version" ] )
   except socket.error,ERR :
       ErrorCode = ERR[0]
       if ErrorCode == errno.ECONNREFUSED:
          win.addstr(x, verLoc -6, "        [ Err " + str(ErrorCode) + ": No eAPI ]          ")
          refresh() 
       elif ErrorCode == errno.EHOSTUNREACH:
          # Never hit with lower socket timeout
          win.addstr(x, verLoc, "Err " + str(ErrorCode) + ": Pwr off or Aboot ]          ")
          refresh() 
       elif ErrorCode == errno.ECONNRESET:
          win.addstr(x, verLoc, "Err " + str(ErrorCode) + ": Con RST ]          ")
          refresh() 
   else:
      win.addstr(x, verLoc, response[0]["version"] + " ]")
      memTotal = response[0]["memTotal"]
      memFree  = response[0]["memFree"]
      percentUsed = 100 - round((float(memFree) / float(memTotal)) * 100, 1)
      win.addstr(x, verLoc+24, str(percentUsed) + "% ]" )
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

   for x in range(NumStudents):   
      win.addstr(x+1,1,"Student-" + str(x+1).zfill(2) + "  EOS:[ . ]         Mem Used: [ . ]")
   win.addstr(22,0,"          [ . ] = Switch probably rebooting")
   refresh() 

   for x in range(20):
      t = Thread(target=GetVersion, args=(x+1,))
      t.start()

   curses.endwin()

try:
   curses.wrapper(main)
except KeyboardInterrupt:
   curses.endwin()
   print "Caught Keyboard Interrupt - Exiting"
   sys.exit()
