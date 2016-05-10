#!/usr/bin/python

# Using pexpect, get the running config and save it with a timestamp

# Note that there is no error-correction or anything fancy here

import pexpect, time

userName   = 'Username'
password   = 'Password'
IP         = '10.0.0.20'

sshCommand = 'ssh -l ' + userName + ' ' + IP + ' \
                  -o UserKnownHostsFile=/dev/null \
                  -o StrictHostKeyChecking=no'
c = pexpect.spawn(sshCommand)

c.expect('Password:')
c.sendline(password)
c.expect('>')
c.sendline('en')
c.expect('#')
c.sendline('show hostname')
c.expect('#')
shoHost = c.before
c.sendline('show run | no-more')
c.expect('#')
shoRun = c.before

lines = shoHost.splitlines()
words = lines[2].split()
hostName = words[1]

# pexpect output includes command and prompt
# so we need to remove them
first = shoRun.find('\n')
last  = shoRun.rfind('\n')
shoRun = shoRun[first+1:last]

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
fileName = hostName + '_' + timestamp
# Write output to file
print 'Saving output to ' + fileName
configFile = open(fileName, 'w')
configFile.write( shoRun )
configFile.close()
