
#!/usr/bin/python
#
# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN! We do not want the LCD to send anything to the Pi @ 5v
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V
# 16: LCD Backlight GND


#import
import RPi.GPIO as GPIO
import time
import os
from datetime import datetime
from multiprocessing import Process

# Define GPIO to LCD mapping
LCD_RS = 26
LCD_E  = 19
LCD_D4 = 13 
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 11

# Define GPIO for button Controls
NEXT = 27
PAUSE = 20
PLAY = 21
PREV = 17
OFF = 4
VOLDWN = 9
VOLUP = 10

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

def main():
  # Main program block
  GPIO.cleanup()
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4 
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  
  GPIO.setup(NEXT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Next Channel button
  GPIO.setup(PAUSE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Stop button
  GPIO.setup(PLAY, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Start button
  GPIO.setup(PREV, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Previous Channel button
  GPIO.setup(OFF, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # OFF button
  GPIO.setup(VOLDWN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Volume down button
  GPIO.setup(VOLUP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Volume up button
  
  # Initialise display
  lcd_init()
  # Send some test
  lcd_byte(LCD_LINE_1, LCD_CMD)
  lcd_string("RPi",2)
  lcd_byte(LCD_LINE_2, LCD_CMD)
  lcd_string("Wifi Radio",2) 
  
  os.system("mpc repeat on")
  
  func()

def func():
  while 1:
          if ( GPIO.input(PREV) == True):
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Previous",2)
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("Station",2)
                time.sleep(0.5)
                os.system("mpc prev")
                while True:
                  scroll()

          if ( GPIO.input(PAUSE) == True):
                os.system("mpc stop")
                while True:
                  pause()
                
          if ( GPIO.input(PLAY) == True):
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Play",2)
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("",2)
                time.sleep(0.5)
                os.system("mpc play")
                while True:
                  scroll()
                  
          if ( GPIO.input(NEXT) == True):
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Next",2)
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("Station",2)
                time.sleep(0.5)
                os.system("mpc next")
                while True:
                  scroll()
                  
          if ( GPIO.input(OFF) == True):
                os.system("mpc stop")
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Shutting down...",1)
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("................",3)
                time.sleep(1.5)
                os.system("sudo halt") #Turn off system

          if ( GPIO.input(VOLDWN) == True):
                os.system("mpc volume -5")
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Volume down",2)
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("-",2)
                time.sleep(0.5)
                while True:
                 scroll()
                 
          if ( GPIO.input(VOLUP) == True):
                os.system("mpc volume +5")
                lcd_byte(LCD_LINE_1, LCD_CMD)
                lcd_string("Volume",2)
                lcd_byte(LCD_LINE_2, LCD_CMD)
                lcd_string("+",2)
                time.sleep(0.5)
                while True:
                 scroll()

  GPIO.cleanup()

def scroll():
  f=os.popen("mpc current")
  station = ""
  for i in f.readlines():
   station += i
   str_pad = " " * 16  
   station = str_pad + station[:-1]  
   for i in range (0, len(station)):  
    dateAndTime = datetime.now().strftime('%b %d  %H:%M')
    lcd_byte(LCD_LINE_1, LCD_CMD)  
    lcd_text = station[i:(i+16)]
    lcd_string(lcd_text,1)  
    time.sleep(0.5)  
    lcd_byte(LCD_LINE_1, LCD_CMD)  
    lcd_string(str_pad,1)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string(dateAndTime,2)
    if ( GPIO.input(OFF) == True) or ( GPIO.input(PREV) == True) or ( GPIO.input(PAUSE) == True) or ( GPIO.input(PLAY) == True) or ( GPIO.input(NEXT) == True) or ( GPIO.input(VOLDWN) == True) or ( GPIO.input(VOLUP) == True):
      func()
      
def pause():
    lcd_byte(LCD_LINE_1, LCD_CMD)
    lcd_string("Paused",2)
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("",2)
    if ( GPIO.input(OFF) == True) or ( GPIO.input(PLAY) == True):
      func()
    if ( GPIO.input(PREV) == True):
      os.system("mpc prev")
      os.system("mpc play")
      func()
    if ( GPIO.input(NEXT) == True):
      os.system("mpc next")
      os.system("mpc play")
      func()
      
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD)
  lcd_byte(0x32,LCD_CMD)
  lcd_byte(0x28,LCD_CMD)
  lcd_byte(0x0C,LCD_CMD)  
  lcd_byte(0x06,LCD_CMD)
  lcd_byte(0x01,LCD_CMD)  

def lcd_string(message,style):
  # Send string to display
  # style=1 Left justified
  # style=2 Centred
  # style=3 Right justified

  if style==1:
    message = message.ljust(LCD_WIDTH," ")  
  elif style==2:
    message = message.center(LCD_WIDTH," ")
  elif style==3:
    message = message.rjust(LCD_WIDTH," ")

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)      

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)   

if __name__ == '__main__':
  main()