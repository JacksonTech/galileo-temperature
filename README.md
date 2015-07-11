# galileo-temperature

galileo-temperature is a tiny Python daemon that grabs temperature data from a TMP36 temperature sensor circuit attached to an Intel Galileo Board 2 via an analog input pin.

I wrote it to graph the temperature of the (partially un-air-conditioned) room where my research project's computer equipment is housed.

# Demo
You can check out a live feed of the data from this project [here.](http://athena.ecs.csus.edu/~jacksocj/tdata/room.html) (If you see a white page, it means my server is down again!)

# How it works

The hardware side of the project is a [TMP36 temperature sensor](https://learn.adafruit.com/tmp36-temperature-sensor/using-a-temp-sensor) attached to an Intel Galileo Board 2. The board has an onboard analog-to-digital converter connected to its Arduino-compatible analog input pins. You can use one of the analog input pins (I used A0 for simplicity) to read in the voltage level from the TMP36. The relationship between the voltage from the TMP36 and temperature is linear, and it's easy to convert the voltage into a temperature. [The TMP36 page has the formula.](https://learn.adafruit.com/tmp36-temperature-sensor/using-a-temp-sensor)

On the software side, the Galileo board is running the Intel-provided Yocto Linux image on a SD card. In Linux, you have to set up a multiplexer to access the Galileo's analog input pins. [Sergey Kiselev](http://www.malinov.com/Home/sergey-s-blog/intelgalileo-programminggpiofromlinux) has an excellent writeup on how to set up the GPIO filesystem in /proc for reading from the pins. 

The daemon reads voltages from the TMP36 as a 12-bit number every 15 seconds. It then converts the digitized value into a temperature. This temperature is placed into at least one of four Python lists that store historical data for 15 minutes, an hour, a day, and a week. These lists drop the oldest temperature with every insert once they fill up. The daemon then allows access to these lists via HTTP, serving them up as JSON. The daemon also occasionally writes the current lists to disk in case the daemon is interrupted, but does not log long-term historical data yet.

# Requirements
* Intel Galileo Board 2
* Yocto Linux (or whatever you can get running on the Galileo)
* Python 2.7 (with JSON support)

# Setting it up
## Hardware
1. Get an Intel Galileo Board 2.
2. Build the TMP36 circuit [as shown here](https://learn.adafruit.com/tmp36-temperature-sensor/using-a-temp-sensor) and connect it to A0.

## Software
1. Get your Galileo set up with the Yocto Linux image from Intel. (The walkthrough for this is beyond the scope of this document!)
2. Place temperature.sh in /etc/init.d and make it executable:
	chmod +x /etc/init.d/temperature.sh
3. Edit the time zone in temperature.sh if necessary.
4. Enable the temperature.sh script:
	update-rc.d temperature.sh defaults
5. Place galileo-temperature.py in /opt and make it executable:
	chmod +x /opt/galileo-temperature.py
6. Reboot, then check to make sure the daemon is running with 
	ps

Once it's set up, you can access the daemon at port 8080 at your Galileo board's IP address. The following URLs serve up data:

* /temp 	(serves temperature in celsius)
* /tdata15 	(serves last 15 minutes' worth of temperatures in JSON)
* /tdataHour	(serves last hours' worth of temperatures in JSON)
* /tdataDay	(serves last days' worth of temperatures in JSON)
* /tdataWeek	(serves last weeks' worth of temperatures in JSON)

Other URLs will do nothing.

You can then use these JSON feeds with a cool graphing library like (MetricsGraphics)[http://metricsgraphicsjs.org].

# Disclaimer
This code was written in a tiny slice of free time during a very hectic semester. It's very much brute-force and I haven't touched it since besides adding comments. There are many ways it can be cleaned up and improved (e.g., by using Python's collections.deque instead of abusing lists to make them circular, and having a non-terrible init script) when I make more free time.

Todo:
* Make the startup script not blindly assume the proper /proc files exist to set up the analog input pins.
* Figure out exactly where the Galileo is getting its time zone information from so the startup script doesn't have to force TZ.
* Log historical data.
* Provide monthly temperature information.

My instance of the daemon is running on a Galileo that is only accessable from another machine in a DMZ. I don't know how secure the daemon is! There is probably a small risk of your Galileo getting pwned. Proceed with caution.

# License
Copyright (C) 2015 Cody Jackson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
