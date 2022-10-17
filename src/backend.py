#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=import-error,line-too-long,bad-whitespace,superfluous-parens
# pylint: disable=too-many-branches,too-many-statements,broad-except
#
# Copyright (C) 2017 by Eugene Yemelyanov <yemelgen@gmail.com>
# This code is under MIT license (see LICENSE.txt for details)
""" Simple RPI service """

import time
import socket
import json
import RPi.GPIO as GPIO
import serial

PIN = 40
TIMEOUT = 5
PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
ACCESS_LIST = [ '0000', '0001' ]

def change_screen( request ):
    """ change imgae """
    host = '127.0.0.1'
    port = 4000
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    attempt = 1
    attempts = 10

    while attempt < attempts:
        try:
            sock.connect( ( host, port ) )
            sock.send( request )
            sock.recv( 1024 )
            sock.close()
            print("The screen has been changed")
            return

        except Exception, err:
            print("ERROR: Could not change the screen: {}".format( err ) )
            attempt += 1
            time.sleep(3)
            if attempt > attempts:
                return

class Service( object ):
    def __init__( self ):
        """ Object constructor. """
        s = None
        port = PORT
        baudrate = BAUDRATE
        pin = PIN
        GPIO.cleanup()
        GPIO.setmode( GPIO.BOARD )
        GPIO.setwarnings( False )
        GPIO.setup( self.pin, GPIO.OUT, initial=1 )
        request = {}
        request['icon'] = 'closed.png'
        request['color'] = 'normal'
        request['title'] = u'Closed'
        request['message'] = u''
        change_screen( json.dumps( request ) )

    def open( self ):
        self.s = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=1 )
    def close( self ):
        self.s.close()

    def read( self ):
        self.data = ''
        while 1:
            if not self.sinWaiting():
                time.sleep(1)
                continue
            else:
                while s.inWaiting() > 0:
                    self.data += s.read(1)
                    break
    def check_access( self, params ):
        if params.get( 'id', '' ) in ACCESS_LIST:
            return { 'message': u'Welcome home!' }
        return { 'message': u'Get out!' }

    def request( self ):
        params = { 'id': self.data.strip() }
        response = self.check_access( params )
        if response or self.data.strip() in ACCESS_LIST:
            print( "The door is unlocked" )
            params = {}
            params['icon'] = 'open.png'
            params['color'] = 'green'
            params['title'] = u'Open'
            params['message'] = response.get('message', u'')
            change_screen( json.dumps( params ) )
            GPIO.output( self.pin, GPIO.LOW )
            time.sleep(TIMEOUT)

            print( "The door is locked" )
            params = {}
            params['icon'] = 'closed.png'
            params['color'] = 'normal'
            params['title'] = u'Closed'
            params['message'] = u''
            change_screen( json.dumps( params ) )

            GPIO.output( self.pin, GPIO.HIGH )
        else:
            print( "Access denied" )
            params = {}
            params['icon'] = 'closed.png'
            params['color'] = 'red'
            params['title'] = u'Denied'
            params['message'] = response.get('message', u'')
            change_screen( json.dumps( params ) )
            time.sleep(TIMEOUT)

            print( "The door is locked" )
            params = {}
            params['icon'] = 'closed.png'
            params['color'] = 'normal'
            params['title'] = u'Closed'
            params['message'] = u''
            change_screen( json.dumps( params ) )

    def dispatch( self ):
        """ Dispatcher of received data. """
        data = self.read()

        for c in data:
            if c == b'\x01':
                self.data = ''
            elif char == b'\x04':
                self.request()
            else:
                self.data += c

    def main( self ):
        """ Driver main """
        while 1:
            self.dispatch()

def main():
    """ main """
    service = Service()
    while True:
        if service.open():
            break
        else:
            print("ERROR: Could not open the module endpoint")
            time.sleep(TIMEOUT)
    service.main()

if __name__ == '__main__':
    main()
