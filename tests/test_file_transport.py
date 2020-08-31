from pathlib import Path

import pytest_twisted

from twisted.internet import reactor
from twisted.internet import endpoints
from twisted.internet import defer
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol

from singtserver.server_file import FileTransportServerFactory
from singtserver.session_files import SessionFiles as ServerSessionFiles

from singtclient.client_file import FileTransportClient

def test_send_file():
    # Server
    # ======
    
    # Create server
    # Create empty context
    server_context = {}

    # Create a session_files instance
    session_files = ServerSessionFiles(Path.cwd() / "server_file_test")
    server_context["session_files"] = session_files
    
    # Start a file transport server factory
    file_transport_server_factory = FileTransportServerFactory(server_context)
    port = 2000
    endpoints.serverFromString(reactor, f"tcp:{port}").listen(file_transport_server_factory)

    # Anticipate audio id
    audio_id = 101
    d_anticipated_audio_id = file_transport_server_factory.anticipate_audio_id(audio_id)

    def on_success(audio_id):
        print(f"Received audio id {audio_id}")
    d_anticipated_audio_id.callCallback(on_success)
    
    # Client
    # ======

    file_path = Path("/Users/matthew/Desktop/VirtualChoir/Sounds/psallite.opus")

    port = 2000
    point = TCP4ClientEndpoint(reactor, "127.0.0.1", port)
    d_protocol = connectProtocol(point, FileTransportClient())
    
    def gotProtocol(p):
        p.send_file(file_path, audio_id)
    d_protocol.addCallback(gotProtocol)

    return defer.gatherResults([d_protocol, d_anticipated_audio_id])

