#!/usr/bin/python2.7

#
# This script is intended to be used on a RaspberryPi.
#
# It logs multiple "weather" informations to a SQLite3 database :
# - the temperature from a DS18B20 sensor
# - the humidity from a DHT11 sensor, thanks to dht11.c
#   (stange encoding of data, so we need this to read the output...)
# - the CPU temperature of your Raspberry Pi
#
# Don't forget to create a SQLite database file beforehand with this command :
# sqlite3 name_of_database_file.db
#
#
# If you want to read the humidity from a cheap DHT11 sensor,
# you'll need to use a C program(dht11.c) available on this repo. 
# Attention : DHT11 must be wired to the correct wiringPi PIN,
# change it in dht11.c if necessary
# (original blog post : http://www.rpiblog.com/2012/11/interfacing-temperature-and-humidity.html)
#
# To compile it, you'll need WiringPi:
# $ git clone git://git.drogon.net/wiringPi
# $ cd wiringPi
# $ ./build
#
# Then compile dht11.c with:
# $ gcc -o dht11 dht11.c -L/usr/local/lib -lwiringPi
#

import sys, time, syslog
from datetime import datetime, timedelta
import sqlite3
import commands
import subprocess

# Change this to your username
DATABASE_LOCATION = "/home/pi/weather/database.db"
DHT11_SENSOR_LOCATION = "/home/pi/weather/dht11"
# Change this to the path of your temp. sensor
device_file = "/sys/bus/w1/devices/28-0000041cee62/w1_slave"


conn = sqlite3.connect(DATABASE_LOCATION,
                       detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
 
# Create database cursor and create tables if they don't exist
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS temperature (datetime TIMESTAMP, temp FLOAT)')
c.execute('CREATE TABLE IF NOT EXISTS cpu_temperature (datetime TIMESTAMP, temp FLOAT)')
c.execute('CREATE TABLE IF NOT EXISTS humidity (datetime TIMESTAMP, humidity INTEGER)')


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(1)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
#        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

def read_humidity():
    lines = subprocess.Popen("sudo " + DHT11_SENSOR_LOCATION, stdout=subprocess.PIPE, shell=True).stdout.read()
    while (lines == "Invalid Data!!\n"):
        time.sleep(4)
        lines = subprocess.Popen("sudo " + DHT11_SENSOR_LOCATION, stdout=subprocess.PIPE, shell=True).stdout.read()
    hum_pos = lines.find('H = ')
    if hum_pos != -1:
        hum = lines[hum_pos+4:hum_pos+6]
        return int(hum)


if __name__ == "__main__":
    temp = read_temp()
    now = datetime.now()
    curTime = time.time();
    c.execute('INSERT INTO temperature VALUES(?, ?)', (curTime, temp))
    cputemp = commands.getstatusoutput('cat /sys/class/thermal/thermal_zone0/temp')
    cputemp = round(float(cputemp[1]) / 1000, 2)
    c.execute('INSERT INTO cpu_temperature VALUES(?, ?)', (curTime, cputemp))
    humidity = read_humidity()
    c.execute('INSERT INTO humidity VALUES(?, ?)', (curTime, humidity))
    conn.commit()
