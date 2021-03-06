#!/usr/bin/env python

#Implement some very basic CC1101 functionality via SPI on the RaspberryPI
#Requires RPi.GPIO(https://pypi.python.org/pypi/RPi.GPIO) and spidev(https://pypi.python.org/pypi/spidev)
#Written by Elazar Broad

#The register configuration has been exported from TI's SmartRF Studio (v7)
#I highly recommend you utilize this tool to build your configuration as opposed to doing it by hand.

import spidev
import RPi.GPIO as GPIO
from array import array


#Registers
WRITE_BURST = 0x40
READ_BURST = 0xC0

REG_STROBE_RESET = 0x30
REG_STROBE_TX = 0x35
REG_STROBE_IDLE = 0x36
REG_STROBE_SFTX = 0x3B

REG_STATUS_TXBYTES = 0x3A

REG_PATABLE = 0x3E
REG_FIFO_TX = 0x3F


#GPIO Pins
PIN_CS = 24 #RPi GPIO CE0
PIN_GD0 = 7

#####################
# CRC enable = false 
# Base frequency = 433.924988 
# Sync word qualifier mode = 16/16 sync word bits detected 
# Modulated = true 
# Channel spacing = 199.951172 
# Device address = 0 
# TX power = 10 
# Preamble count = 3 
# Manchester enable = true 
# Modulation format = 2-FSK 
# Packet length = 255 
# RX filter BW = 58.035714 
# PA ramping = false 
# Data rate = 2.39897 
# Data format = Normal mode 
# Whitening = false 
# Carrier frequency = 433.924988 
# Packet length mode = Variable packet length mode. Packet length configured by the first byte after sync word 
# CRC autoflush = false 
# Address config = No address check 
# Channel number = 0 
# Deviation = 5.157471 
# Rf settings for CC1101
CC1101_CONFIG = [
    0x29,  # IOCFG2              GDO2 Output Pin Configuration
    0x2E,  # IOCFG1              GDO1 Output Pin Configuration
    0x06,  # IOCFG0              GDO0 Output Pin Configuration
    0x47,  # FIFOTHR             RX FIFO and TX FIFO Thresholds
    0xD3,  # SYNC1               Sync Word, High Byte
    0x91,  # SYNC0               Sync Word, Low Byte
    0xFF,  # PKTLEN              Packet Length
    0x04,  # PKTCTRL1            Packet Automation Control
    0x01,  # PKTCTRL0            Packet Automation Control
    0x00,  # ADDR                Device Address
    0x00,  # CHANNR              Channel Number
    0x06,  # FSCTRL1             Frequency Synthesizer Control
    0x00,  # FSCTRL0             Frequency Synthesizer Control
    0x10,  # FREQ2               Frequency Control Word, High Byte
    0xB0,  # FREQ1               Frequency Control Word, Middle Byte
    0x7E,  # FREQ0               Frequency Control Word, Low Byte
    0xF6,  # MDMCFG4             Modem Configuration
    0x83,  # MDMCFG3             Modem Configuration
    0x0A,  # MDMCFG2             Modem Configuration
    0x12,  # MDMCFG1             Modem Configuration
    0xF8,  # MDMCFG0             Modem Configuration
    0x15,  # DEVIATN             Modem Deviation Setting
    0x07,  # MCSM2               Main Radio Control State Machine Configuration
    0x30,  # MCSM1               Main Radio Control State Machine Configuration
    0x18,  # MCSM0               Main Radio Control State Machine Configuration
    0x16,  # FOCCFG              Frequency Offset Compensation Configuration
    0x6C,  # BSCFG               Bit Synchronization Configuration
    0x03,  # AGCCTRL2            AGC Control
    0x40,  # AGCCTRL1            AGC Control
    0x91,  # AGCCTRL0            AGC Control
    0x87,  # WOREVT1             High Byte Event0 Timeout
    0x6B,  # WOREVT0             Low Byte Event0 Timeout
    0xFB,  # WORCTRL             Wake On Radio Control
    0x56,  # FREND1              Front End RX Configuration
    0x10,  # FREND0              Front End TX Configuration
    0xE9,  # FSCAL3              Frequency Synthesizer Calibration
    0x2A,  # FSCAL2              Frequency Synthesizer Calibration
    0x00,  # FSCAL1              Frequency Synthesizer Calibration
    0x1F,  # FSCAL0              Frequency Synthesizer Calibration
    0x41,  # RCCTRL1             RC Oscillator Configuration
    0x00,  # RCCTRL0             RC Oscillator Configuration
    0x59,  # FSTEST              Frequency Synthesizer Calibration Control
    0x7F,  # PTEST               Production Test
    0x3F,  # AGCTEST             AGC Test
    0x81,  # TEST2               Various Test Settings
    0x35,  # TEST1               Various Test Settings
    0x09  # TEST0               Various Test Settings
]

def CC1101_readBurst(registerAddress, len):
	#GPIO.output(PIN_CS, GPIO.LOW)
	spi.xfer([registerAddress | READ_BURST,])
	ret = spi.readbytes(len)
	#GPIO.output(PIN_CS, GPIO.HIGH)
	return ret

def CC1101_writeStrobe(registerAddress):
	GPIO.output(PIN_CS, GPIO.LOW)
	spi.xfer([registerAddress,])
	GPIO.output(PIN_CS, GPIO.HIGH)

def CC1101_writeBurst(registerAddress, data):
	GPIO.output(PIN_CS, GPIO.LOW)
	spi.xfer([registerAddress | WRITE_BURST,])
	spi.xfer(data)
	GPIO.output(PIN_CS, GPIO.HIGH)


def CC1101_init():
	#PA table
	CC1101_writeBurst(REG_PATABLE, [0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0]) #Set PA table to 10dBm

	#Write the config, starting from 0
	CC1101_writeBurst(0x00, CC1101_CONFIG)


def CC1101_tx(txData):
	#Go idle before we write to the TX FIFO buffer
	CC1101_writeStrobe(REG_STROBE_IDLE)

	#Write to the data to be transmitted to the TX FIFO buffer
	CC1101_writeBurst(REG_FIFO_TX, txData)

	#Transmit
	CC1101_writeStrobe(REG_STROBE_TX)

	CC1101_waitGD0(GPIO.LOW)
	
	#Veriy that the data was transmitted
	ret = CC1101_readBurst(REG_STATUS_TXBYTES, 1)
	ret = ret[0] & 0x7F
	if ret == 0:
		return 1
	return 0

def CC1101_waitGD0(state):
	while GPIO.input(PIN_GD0) != state:
		sleep(0.01)





#Setup GPIO
GPIO.setmode(GPIO.BOARD)

GPIO.setup(PIN_CS, GPIO.OUT)
GPIO.output(PIN_CS, GPIO.HIGH)

GPIO.setup(PIN_GD0, GPIO.IN)


#Open SPI device
spi = spidev.SpiDev()
spi.open(0, 0)

#Init the CC1101 chip, write configuration
CC1101_init()

#Transmit some data
dataToSend = "Hello!"
dataToSend = array('b', dataToSend)
dataToSend = list(dataToSend)

if CC1101_tx(dataToSend):
	print "Data transmitted successfully!"
else:
	print "Transmit failed!"

spi.close()
GPIO.cleanup()
