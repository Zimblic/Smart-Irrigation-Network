import RPi.GPIO as GPIO
import MySQLdb
import smtplib
import time
import threading
from flask import Flask, render_template, request
app = Flask(__name__)

#SMTPlib setup for text notifications:
#sent_from = 'Put email address here'
#to = 'receiving number here

#subject = 'Raspberry SMTP'

#txtserver = smtplib.SMTP('smtp.gmail.com', 587)
#txtserver.ehlo()
#txtserver.starttls()
#txtserver.login('email', 'passwd')

def readDB():
	global data, rain, temp
	try: #Attempt database connection. 
		db = MySQLdb.connect("IPaddress","username","password","databasename")
		curs=db.cursor()
		curs.execute("SELECT * FROM sensordata ORDER BY sensestamp DESC LIMIT 5")
		data = curs.fetchall()
		curs.execute("SELECT rainfall FROM sensordata ORDER BY sensestamp DESC")
		rain = curs.fetchone()
		curs.execute("SELECT temperature FROM sensordata ORDER BY sensestamp DESC")
		temp = curs.fetchone()
		print temp
		print rain
		
		db.close
	except MySQLdb.Error: #If connection fails, input NaN into each variable.
		rain = 'NaN'
		data = 'NaN'
		temp = 'NaN'
		pass	
GPIO.setmode(GPIO.BCM)

# Dictionary for pin number, name, and pin state:
pins = {
	6 : {'name' : 'Frontyard (6)', 'state' : GPIO.LOW, 'totaltime' : 0, 'starttime' : 0},
    22 : {'name' : 'Backyard (22)', 'state' : GPIO.LOW, 'totaltime' : 0, 'starttime' : 0},
    4 : {'name' : 'Farm (4)', 'state' : GPIO.LOW, 'totaltime' : 0, 'starttime' : 0},
    26 : {'name' : 'Garden (26)', 'state' : GPIO.LOW, 'totaltime' : 0, 'starttime' : 0}
   } 
try:
	# Set every pin as output set to low:
	for pin in pins:
	   GPIO.setup(pin, GPIO.OUT)
	   GPIO.output(pin, GPIO.LOW)
	
	@app.route("/") #URL decorator - '/' directory
	def main():
		# For each pin, read the pin state and store it in the pins dictionary:
		for pin in pins:
			pins[pin]['state'] = GPIO.input(pin)
		# Pass the template data into the template main.html and return it to the user
		#return render_template('main.html', **templateData)
		readDB()
		templateData = {
			'pins' : pins,
			'rain' : rain,
			'temp' : temp,
			'data' : data
		}
		return render_template('main.html', **templateData)

	#Function that requests a URL with the pin number and action in it:
	@app.route("/<changePin>/<action>")
	def useraction(changePin, action):
		readDB()
		global endtime
		# Convert the pin from the URL into an integer:
		changePin = int(changePin)
		# Get the device name for the pin being changed:
		deviceName = pins[changePin]['name']
		# If the action part of the URL is "on," execute the code indented below:
		if action == "on" and rain[0] != "Raining!":
				pins[changePin]['starttime'] = time.time()
				# Set the pin high:
				GPIO.output(changePin, GPIO.HIGH)
				# Save the status message to be passed into the template:
				message = "Turned " + deviceName + " on for X minutes."
				#SMTP message send for on:
				#txtserver.sendmail(sent_from, to, deviceName + ' is now on.')
					
		if action == "off":
			endtime = time.time()
			elapsedtime = endtime - pins[changePin]['starttime']
			elapsedtime = round(elapsedtime, 2)
			GPIO.output(changePin, GPIO.LOW)
			message = "Turned " + deviceName + " off."
			pins[changePin]['totaltime'] = pins[changePin]['totaltime'] + elapsedtime
			#SMTP message send for off:
			#txtserver.sendmail(sent_from, to, deviceName + ' is now off.')

		#If moisture sensor detects rain, reset all pins to off and kill relay power.
		if rain[0] == "Raining!": 
			for pin in pins:
				GPIO.output(pin,GPIO.LOW)
		else:
			pass
		# For each pin, read the pin state and store it in the pins dictionary:		
		for pin in pins:
			pins[pin]['state'] = GPIO.input(pin)
			
		# Along with the pin dictionary, put the message into the template data dictionary:
		templateData = {
			'pins' : pins,
			'rain' : rain,
			'temp' : temp,
			'data' : data
		}
		return render_template('main.html', **templateData)
		
	if __name__ == "__main__":
			app.run(host='0.0.0.0', port=80, debug=True)
except:
	GPIO.cleanup()
	print "Code ended by CTRL + C or error occured"
finally:
	GPIO.cleanup()
	print "Clean exit"

