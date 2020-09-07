from pathlib import Path

import pytest_twisted
from twisted.internet import reactor
from twisted.internet import endpoints
from twisted.internet import defer

from singtserver import SessionFiles as ServerSessionFiles
from singtserver import Database
from singtserver import Command
from singtserver import UDPServer
from singtserver import TCPServerFactory
from singtserver import WebServer
from singtclient import client

def create_server(context):
    # Server
    # ======

    # Add reactor to context
    context["reactor"] = reactor
    reactor_  = context["reactor"]

    # Create session files
    session_files = ServerSessionFiles(Path.cwd() / "test_tcp__test_announce_invite")
    context["session_files"] = session_files

    # Create a database
    database = Database(context)
    context["database"] = database

    # Define the UDPServer class
    context["udp_server"] = UDPServer
    
    # Create a Command
    command = Command(context)
    context["command"] = command
    
    # Create a web server
    web_server = WebServer(context)
    context["web_server"] = web_server
    
    # Create a TCP server factory
    tcp_server_factory = TCPServerFactory(context)
    context["tcp_server_factory"] = tcp_server_factory

    # Start TCP server listening
    endpoint = endpoints.serverFromString(reactor_, "tcp:1234")
    d_listening = endpoint.listen(tcp_server_factory)


def create_client(context):
    # Client
    # ======
    
    client.init_headless(context)


def test_announce():
    # Create server
    server_context = {}
    create_server(server_context)

    # Create client
    client_context = {}
    create_client(client_context)

    # Get client ID
    client_database = client_context["database"]
    client_id = client_database.get_client_id()

    # Connect client to server; client automatically announces itself
    client_command = client_context["command"]
    username = "test_client"
    address = "127.0.0.1"
    client_command.connect(username, address)
    tcp_client = client_context["tcp_client"]

    # Test that client has announced itself to the TCP server
    tcp_server_factory = server_context["tcp_server_factory"]
    tcp_server_factory._shared_context.participants
    
    # Test that client has announced itself to the UDP server
