from pathlib import Path

import pytest_twisted
from twisted.internet import reactor
from twisted.internet import defer

from singtserver import SessionFiles
from singtserver import Database
from singtserver import Participants
from singtserver import UDPServer
from singtserver.server import start_logging
from singtclient.client_udp import UDPClientBase


def start_udp_server(context, port=2001):
    udp_server = UDPServer(context)
    listening = reactor.listenUDP(port, udp_server)
    return udp_server, listening

# def test_create_udp_server():
#     context = {}

#     udp_server, listening = start_udp_server(context)
    
#     d = listening.stopListening()
#     return d

def create_listener():
    class Listener:
        def __init__(self):
            self.d_joined = defer.Deferred()
            self.d_left = defer.Deferred()
            
        def participant_joined(self, client_id, name):
            print(f"Participant joined with client_id {client_id} "+
                  f"and name '{name}'")
            self.d_joined.callback((client_id, name))

        def participant_left(self, client_id, name):
            print(f"Participant left with client_id {client_id} "+
                  f"and name '{name}'")
            self.d_left.callback((client_id, name))
            
    listener = Listener()
    return listener



def test_create_udp_client():
    # Create server's context
    server_context = {}

    # Create session files
    session_files = SessionFiles(Path.cwd() / ("test_udp__test_create_udp_client"))
    server_context["session_files"] = session_files

    # Enable logging
    start_logging(session_files)
    
    # Create Database
    database = Database(server_context)
    server_context["database"] = database

    # Create Participants
    participants = Participants(server_context)
    server_context["participants"] = participants

    # Create UDP Server
    print("Starting UDP server")
    host = "127.0.0.1"
    port = 2001
    udp_server, listening = start_udp_server(server_context, port)
    
    # Create UDP Client (well, the base at least)
    udp_client_base = UDPClientBase(host, port)

    # Connect the client to the server
    print("Connecting UDP client")
    reactor.listenUDP(0, udp_client_base)
    
    # Fake the TCP announce
    client_id = 1
    client_name = "test"
    participants.join_tcp(client_id, client_name)
    
    # Announce via UDP
    udp_client_base.announce(client_id)
    #participants.join_udp(client_id)

    # Add a participants listener
    listener = create_listener()
    participants.add_listener(listener)

    # Test that the participants include the client
    def check(details):
        joined_client_id, joined_client_name = details
        assert joined_client_id == client_id
        assert joined_client_name == client_name
    listener.d_joined.addCallback(check)
    
    # # Stop the server
    # d = listening.stopListening()
    # return d

    return listener.d_joined
