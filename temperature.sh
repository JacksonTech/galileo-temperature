#!/bin/sh
### BEGIN INIT INFO
# Provides:			tempdaemon
# Required-Start:		$remote_fs $time
# Required-Stop:		$remote_fs $time
# Default-Start:		2 3 4 5
# Default-Stop:			0 1 6
# Short-Description:		Starts Galileo temperature daemon
### END INIT INFO

pidfile=/var/run/galileo-temperature.pid
launcher=/opt/galileo-temperature.py

start()
{
    echo "Starting galileo-temperature"
    
    # May need to change this!
    export TZ="UTC+7"
    
    # Set up GPIO for analog pin 0 input
    # Many thanks to http://www.malinov.com/Home/sergey-s-blog/intelgalileo-programminggpiofromlinux
    echo -n "37" > /sys/class/gpio/export
    echo -n "out" > /sys/class/gpio/gpio37/direction
    echo -n "0" > /sys/class/gpio/gpio37/value
	
    start-stop-daemon -q -S -m -p $pidfile -b -x $launcher
}

stop()
{
    echo "Stopping galileo-temperature"
    start-stop-daemon -q -K -p $pidfile -s USR1
    rm $pidfile -f
    rm $pidsreset -f
}

die()
{
    exit 1
}

case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  restart)
        $0 stop
        $0 start
        ;;
  *)
        echo "Usage: temperature.sh { start | stop | restart }" >&2
        exit 1
        ;;
esac

exit 0

