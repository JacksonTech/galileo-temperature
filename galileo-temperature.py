#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Temperature sensor data logging application for the Galileo board.

# Copyright (C) 2015 Cody Jackson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import threading
import socket
import json
import datetime
import os

# Set this to be the directory where you want your data files 
# to be stored.
workDir = "/home/root/data"

# Simple HTTP handler thread.
# Listens on port 8080 by default.
class netThread(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind((socket.gethostname(), 8080))

        def run(self):
                self.sock.listen(5)

				# request handling loop
                while True:
                        try:
                                (csocket, caddr) = self.sock.accept()
				# get the URL from the HTTP request
                                request = csocket.recv(4096).split(" ")
                                if len(request) > 1:
                                        file = request[1]

                                        if file == "/tdata15":
                                                csocket.send(json.dumps(tdata15))
                                        elif file == "/tdataHour":
                                                csocket.send(json.dumps(tdataHour))
                                        elif file == "/tdataDay":
                                                csocket.send(json.dumps(tdataDay))
                                        elif file == "/tdataWeek":
                                                csocket.send(json.dumps(tdataWeek))
                                        elif file == "/temp":
                                                csocket.send("%.2f\n" % temp)
                                # else case: do nothing
                        except IOError:
                                print "Error, closing socket."
                        finally:
                                try:
                                        csocket.close()
                                except Exception:
                                        pass

# Helper function to dump current data to data directory
def save(name, data):                             
        o = open(os.path.join(workDir, name), "w")        
        o.write(json.dumps(data))                                   
        o.close()                                         
            
# Helper function to load in data from the data directory.
# Returns the data for the file as a list.                                              
def load (name):                                          
        data = []                                         
        try:                                              
                o = open(os.path.join(workDir, name), "r")
                data = json.loads(o.read())
        except IOError:                   
                print "Didn't load ", name
        finally:                 
                try:             
                        o.close()
                except Exception:
                        pass      
        return data        
                           
# Entry Point                                               
if __name__ == "__main__":        
	# lists to store round-robin information.
	# these are used as deques (data goes on, data pops off other
	# end if the size limit is reached).
	# (Yes, collections.deque is better)
        tdata15 = []                                        
        tdataHour = []                    
        tdataDay = []                     
        tdataWeek = []                    
              
        # number of data points read                            
        count = 0                         
                                    
	# restore old data if possible
        tdata15 = load("tdata15.json")                              
        tdataHour = load("tdataHour.json")
        tdataDay = load("tdataDay.json")                                                 
        tdataWeek = load("tdataWeek.json")                                               

	# start request handler
        th = netThread()                                                                 
        th.start()                                                                       
                
        # temperature-sensing loop.
        # Reads and processes a temperature every 15 seconds.                                                                             
        while True:                 
			# read from analog pin
                        t = open("/sys/bus/iio/devices/iio:device0/in_voltage0_raw", "r")
                        tdata = t.readline()                                             
                        t.close()                                                        
                                                                                                                                                                               
                        # equation from from https://learn.adafruit.com/tmp36-temperature-sensor/using-a-temp-sensor
                        # but altered to account for 12-bit precision in ADC for Galileo 2                
                        temp = ((int(tdata) * 5000.0/4096) - 500) / 10                                    
                                                                                                                                                                         
                        # format date for JSON graphing library (metricgraphics)                                                                            
                        d = {"date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "value": temp}
                                                  
			# Only store 15 minutes worth of information
                        if len(tdata15) >= 60:                                     
                                tdata15.pop(0)                                     
                        tdata15.append(d)

			# only write hourly data per minute, and only store 2 hours
                        if count % 4 == 0:                 
                                if len(tdataHour) > 2 * 60:
                                        tdataHour.pop(0)  
                                tdataHour.append(d)                             
                                                                                
                        # only write daily data per 15 minutes, and store 2 days
                        if count % (4 * 15) == 0:             
                                if len(tdataDay) > 2 * 24 * 4:
                                        tdataDay.pop(0)
                                tdataDay.append(d)                      
                                                                        
                        # and weekly data per hour, storing up to 7 days
                        if count % (4 * 60) == 0:               
                                if len(tdataWeek) > 7 * 24:     
                                                tdataWeek.pop(0)
                                tdataWeek.append(d)                          
                                                            
                                # also save data hourly      
                                                                 
                                save("tdata15.json", tdata15)    
                                save("tdataHour.json", tdataHour)
                                save("tdataDay.json", tdataDay)  
                                save("tdataWeek.json", tdataWeek)
                                                                     
                        count += 1   
                        time.sleep(15)
