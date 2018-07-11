import math
import time
import MySQLdb
import sys
import os
import RPi.GPIO as GPIO
from datetime import datetime
import Adafruit_DHT
from datetime import datetime

sensor = Adafruit_DHT.DHT11 #Model sensor for humidity and temperature
pin = 11

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN) #Pin for moisture sensor
global rain


def WriteToDB(rain,temp,humid):
	
	#This is the time stamp that displays current time
	t = datetime.now()
	date = t.strftime('%m/%Y/%d %H:%M:%S')
	print date
	
	#Open Database connection and throw error code with description if not successful.
	try:
		db = MySQLdb.connect("IPaddress","username","password","databasename" )
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		return
	
	#Ready cursor for SQL commands.
	cursor = db.cursor()
	
	#Write to database
	#If new var is created this statment must be updated.
	cursor.execute("INSERT INTO sensordata(sensestamp, rainfall, temperature, humidity) VALUES (%s,%s,%s,%s)", (date,rain,temp,humid))
	
	#Commit new changes to database.
	db.commit()
	
	#Close database
	db.close()
	
#Infinite loop for checking rain status every 10 seconds.
try:
	while True:
		humid, temp = Adafruit_DHT.read_retry(sensor, pin) #Check humid and temp from sensor
		print 'Temp: {0:0.1f} C Humidity: {1:0.1f} %'.format(temp, humid) #Print both as floating point to console
		rainstate = GPIO.input(23)  #Check reading from rain drop sensor at pin 23.
		if (rainstate == 0):
			rain = "Raining!"
			print rain
		else:
			rain = "None"
			print rain
		WriteToDB(rain,temp,humid)
		time.sleep(30) #Wait 30 seconds, then repeat.
except KeyboardInterrupt:
	print "Quit by CTRL+C"
	GPIO.cleanup()
	
				
