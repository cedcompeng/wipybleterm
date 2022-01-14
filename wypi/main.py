import pycom
from network import Bluetooth
from machine import Timer
from machine import UART
import time

VERSION = "Version 1.08"

keypressed = 'X'
update = False

uart = UART(0,baudrate=115200)

def ble_connection(characteristic):
  events = characteristic.events()
  if events & Bluetooth.CLIENT_CONNECTED:
    uart.write("[CONNECTED]\r\n")
    pycom.heartbeat(False)
    pycom.rgbled(0x009900)
  elif events & Bluetooth.CLIENT_DISCONNECTED:
    uart.write("[DISCONNECTED]\r\n")
    pycom.heartbeat(True)
    update = False

def characteristic1_handler(characteristic, data=''):
  global keypressed
  global update
  events = characteristic.events()
  if events & (Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT):
    characteristic.value(keypressed)
    if events & Bluetooth.CHAR_SUBSCRIBE_EVENT:
      update = True

def characteristic2_handler(characteristic, data=''):
  global uart
  global update
  events = characteristic.events()
  if events & Bluetooth.CHAR_WRITE_EVENT:
    val = characteristic.value()
    uart.write(val)
    if val == 13:
      uart.write(10)
    elif val == 10:
      uart.write(13)


bluetooth = Bluetooth()
bluetooth.set_advertisement(name='WiPy', manufacturer_data="Pycom", service_uuid=0xEC00)
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=ble_connection)
bluetooth.advertise(True)
service1 = bluetooth.service(uuid=0xEC00, isprimary=True, nbr_chars=1)
characteristic1 = service1.characteristic(uuid=0xEC0E, value='0')
characteristic1.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=characteristic1_handler)
service2 = bluetooth.service(uuid=0xEC01, isprimary=True, nbr_chars=1)
characteristic2 = service2.characteristic(uuid=0xEC0F, value='1')
characteristic2.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=characteristic2_handler)

uart.write("\r\n\n")
uart.write(VERSION)
uart.write("\r\n")
uart.write("BLE Service started!\r\n")

while True:
  time.sleep(0.2)
  if uart.any():
    keypressed = uart.read(1)
    if update:
      characteristic1.value(keypressed)
    uart.write(keypressed)
    if keypressed == 13:
      uart.write(10)
    elif keypressed == 10:
      uart.write(13)
