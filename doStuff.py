#!/usr/bin/pythonRoot

# bring in the libraries
import RPi.GPIO as gpio
import datetime
from flup.server.fcgi import WSGIServer
import sys, urlparse
import subprocess #added for the ir sensor
import logging
LOG_FILENAME = 'example.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

# set up our GPIO pins
gpio.setmode(gpio.BCM)
gpio.setup(18, gpio.OUT)
gpio.setup(24, gpio.OUT)

pinList=[18,24]

#the beginning of the lirc call
remoteControlCall="irsend send_once verizon key_"
acRemoteCall = "irsend send_once airconditioner key_"

#for now this does nothing but in futurre used for set up of auto on/off
dateTime = datetime.datetime.now()

# all of our code now lives within the app() function which is called for each http request we receive
def app(environ, start_response):
  # start our http response
  start_response("200 OK", [("Content-Type", "text/html")])
  # look for inputs on the URL
  parameters = urlparse.parse_qs(environ["QUERY_STRING"])
  yield ('&nbsp;') # flup expects a string to be returned from this function
  # if there's a url variable named 'q'

  #runs a for loop turning on/off all pins used as defined by pinList
  #******************************************************************
  #                  On = false       Off = true
  #                  Because of polarity of Relay
  #******************************************************************
  if "q" in parameters:
    if parameters["q"][0] == "allOn":
      for x in pinList:
        gpio.output(x, False)
    elif parameters["q"][0] == "allOff":
      for x in pinList:
          gpio.output(x, True)


    if parameters["q"][0] == "lightOn":
      gpio.output(18, False)   # Turn it on
    elif parameters["q"][0] == "lightOff":
      gpio.output(18, True)  # Turn it off


    if parameters["q"][0] == "heatOn":
      gpio.output(24, False)
    elif parameters["q"][0] == "heatOff":
      gpio.output(24, True)

#depending on the button pressed on the remote a call will be passed through and concatenated with the rest of the command and then passsed into subprocess

#***************************************************************************************
#ISSUE!!! NEED TO FIGURE OUT HOW TO STILL USE STRING COMMANDS LIKE "power" or "last"
#
#        ****FIXED with try/except
#***************************************************************************************
  if "remoteCommand" in parameters:
    try:
      remoteCommandInt = int(parameters["remoteCommand"][0])
      remoteCommandstr = str(parameters["remoteCommand"][0])
      logging.debug("remoteCommandInt: %s", remoteCommandInt)
      if remoteCommandInt>9:
        counter=0;
        while counter < (len(remoteCommandstr)):
          logging.debug("passsing again")
          newCall =  remoteControlCall  + remoteCommandstr[counter]
          logging.debug("the call: %s", newCall)
          subprocess.call(newCall, shell = True)
          counter += 1
      else:
        newCall =  remoteControlCall + parameters["remoteCommand"][0]
        subprocess.call(newCall, shell = True)
    except ValueError:
      newCall =  remoteControlCall + parameters["remoteCommand"][0]
      subprocess.call(newCall, shell = True)

  logging.debug("the number: %s", remoteCommandInt)

  #***************************************************************************************
  #
  #            AC Remote
  #
  #***************************************************************************************
var acCall

  if "ac" in parameters:
      acCall = str(parameters["remoteCommand"][0])
      subprocess.call(acCall, shell = True)


#by default, Flup works out how to bind to the web server for us, so just call it with our app() function and let it get on with it
WSGIServer(app).run()
