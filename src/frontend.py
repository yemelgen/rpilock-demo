#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=import-error,line-too-long,bad-whitespace,superfluous-parens
# pylint: disable=too-many-branches,too-many-statements
#

# Copyright (C) 2017 by Eugene Yemelyanov <yemelgen@gmail.com>
# This code is under MIT license (see LICENSE.txt for details)
"""
Simple rpi display program using pygame
You can use at as a login shell on your RPI
"""

import time
import socket
import os
import json
import pygame

MAXBUF = 1024

class Lock( object ):
    """ Lock class """
    data = b''
    sock = None
    def __init__( self ):
        """ Object constructor """
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        os.putenv('SDL_NOMOUSE', '1')
        os.putenv('SDL_FBDEV','/dev/fb0')

        pygame.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)
        self.tfont = pygame.font.SysFont( 'DejaVu Sans Mono', 120, bold=True )
        self.mfont = pygame.font.SysFont( 'DejaVu Sans Mono', 60 )
        self.size = ( pygame.display.Info().current_w,
                      pygame.display.Info().current_h )
        self.screen = pygame.display.set_mode( self.size )
        self.screen.fill( ( 0, 0, 0 ) )
        pygame.display.flip()

        request = {}
        request['icon'] = 'wait.png'
        request['color'] = 'normal'
        request['title'] = u'Wait'
        request['message'] = u''
        self.change_screen( request )

    def change_screen( self, request ):
        """ change background image """

        if not os.path.isfile( request['icon'] ):
            path = 'wait.png'
        else:
            path = request['icon']

        if request['color'] == 'green':
            color = ( 0, 255, 0 )
        elif request['color'] == 'red':
            color = ( 255, 0, 0 )
        elif request['color'] == 'blue':
            color = ( 0, 0, 255 )
        else:
            color = ( 255, 255, 255 )

        img = pygame.image.load( path )
        img.fill( ( 0, 0, 0, 255 ), None, pygame.BLEND_RGBA_MULT )
        img.fill( color + (0, ), None, pygame.BLEND_RGBA_ADD )
        img_rect = img.get_rect()
        img_rect.center = (self.size[0] / 2, ( self.size[1] / 2 ) - 100 )

        title = self.tfont.render( request['title'], False, color )
        title_rect = title.get_rect()
        title_rect.center = ( ( self.size[0] / 2 ),
                              ( self.size[1] / 2 ) + 150 )

        message = self.mfont.render( request['message'], False, color )
        message_rect = title.get_rect()
        message_rect.center = ( ( self.size[0] / 2 ),
                                ( self.size[1] / 2 ) + 250 )

        self.screen.fill( ( 0, 0, 0 ) )
        self.screen.blit( img, img_rect )
        self.screen.blit( title, title_rect )
        self.screen.blit( message, message_rect )
        pygame.display.flip()

    def dispatch( self ):
        """ Dispatcher """
        conn, addr = self.sock.accept()
        print( "[.] {}, Host connected: address={}, port={}\n".format(
            time.strftime("%Y-%m-%d %H:%M:%S"), addr[0], str(addr[1]) ) )

        self.data = conn.recv( MAXBUF )

        if self.data:
            print( "<== {}, Receiving data, address={}, port={}:\n".format(
                time.strftime("%Y-%m-%d %H:%M:%S"),
                addr[0],
                str(addr[1]) ) )
            print( self.data )

            if self.change_screen( json.loads( self.data ) ):
                print( '[*] The screen has been changed' )
        conn.close()

    def main( self ):
        """ main """
        host = '127.0.0.1'
        port = 4000
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.sock.bind( ( host, port ) )
        self.sock.listen(1)

        while True:
            self.dispatch()

def main():
    """ main """
    lock = Lock()
    lock.main()

if __name__ == '__main__':
    main()
