## RaspberryPi temperature and humidity logger

This project is a little script I made (I know it's ugly) to log the ambient temperature, humidity and CPU temperature of my RPi.    
It uses a DS18B20 sensor for the temperature (good precision) and a cheap DHT11 sensor for the humidity.    
It also logs the CPU temperature of the RPi

## How to use it ?

Just add a crontab entry (`crontab -e`) like this one :    
*/30 * * * * /home/pi/weather/log_weather.py

To run it every 30 minutes (you can of course modify the delay between each request to your likings).

See the log_weather.py file for more informations.

