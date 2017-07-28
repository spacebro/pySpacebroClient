#!/usr/bin/env python
import unittest
import sys, os
from os import path
from mock import patch
from pySpacebroClient import SpacebroClient
from dotmap import DotMap

timeout=1
verbose=True

class TestSpacebroClient(unittest.TestCase):

    def on_newClient(self, args):
        #print(args)
        #print('on_newClient', args)
        #print('type', type (args))
        #print('name', args['name'])
        self.client = DotMap(args)

    def on_connections(self, args):
        self.connections = args

    def on_inMedia(self, args):
        self.inMediaValue = args

    def test_connect(self):
        settings = DotMap({
            'host': 'localhost',
            'port': 36000,
            'client': {
                'name': 'python-bro'
            },
            'channelName': 'media-stream',
            'verbose': verbose,
            'connection': [ 'python-bro/outMedia => etna/inMedia',
                            'python-bro/outMedia => etna/inMedia'
                          ]
            })
        spacebroClient = SpacebroClient(settings.toDict())

        # Listen
        spacebroClient.on('newClient', self.on_newClient)
        spacebroClient.wait(seconds=timeout)

        self.assertEqual(self.client.name, settings.client.name)
        spacebroClient.disconnect()

    def test_connections_sent_and_received(self):
        settings = DotMap({
            'host': 'localhost',
            'port': 36000,
            'client': {
                'name': 'python-bro'
            },
            'channelName': 'media-stream2',
            'verbose': verbose,
            'connection': [ 'python-bro/outMedia => etna/inMedia',
                            'python-bro/outMedia => etna/inMedia'
                          ]
            })
        spacebroClient = SpacebroClient(settings.toDict())

        # Listen
        spacebroClient.on('connections', self.on_connections)
        spacebroClient.wait(seconds=timeout)

        self.assertEqual(DotMap(self.connections[-1]).src.clientName, settings.connection[-1].split('/')[0])
        spacebroClient.disconnect()

    def test_connect_output_to_input(self):
        settings = DotMap({
            'host': 'localhost',
            'port': 36000,
            'client': {
                'name': 'python-bro',
                'in': {
                    'inMedia': {
                        'eventName': 'inMedia',
                        'description': 'Input media',
                        'type': 'all'
                    }
                },
                'out': {
                    'outMedia': {
                        'eventName': 'outMedia',
                        'description': 'Output media',
                        'type': 'all'
                    }
                }
            },
            'channelName': 'media-stream3',
            'verbose': verbose,
            'connection': [ 'python-bro/outMedia => python-bro/inMedia',
                            'python-bro/outMedia => etna/inMedia'
                          ]
        })
        spacebroClient = SpacebroClient(settings.toDict())

        # Listen
        spacebroClient.on(settings.client['in'].inMedia.eventName, self.on_inMedia)
        spacebroClient.wait(seconds=timeout)
        spacebroClient.emit(settings.client.out.outMedia.eventName, {'value': 5})
        spacebroClient.wait(seconds=timeout)

        self.assertEqual(DotMap(self.inMediaValue).value, 5)
        spacebroClient.disconnect()



if __name__ == '__main__':
    unittest.main()
