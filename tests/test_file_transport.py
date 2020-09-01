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


def create_server(directory, audio_id):
    # Server
    # ======
    
    # Create server
    # Create empty context
    server_context = {}

    # Create a session_files instance
    session_files = ServerSessionFiles(Path.cwd() / directory)
    server_context["session_files"] = session_files
    
    # Start a file transport server factory
    file_transport_server_factory = FileTransportServerFactory(server_context)
    port = 2000
    endpoint = endpoints.serverFromString(reactor, f"tcp:{port}")
    d_listening = endpoint.listen(file_transport_server_factory)

    # Anticipate audio id
    d_anticipated_audio_id = file_transport_server_factory.anticipate_audio_id(audio_id)

    d_terminated = defer.gatherResults([d_listening, d_anticipated_audio_id])
    def on_success(results):
        listening_port, audio_id = results
        print(f"Received audio id {audio_id}")
        print("Shutting down server")
        return listening_port.stopListening()
    d_terminated.addCallback(on_success)
    
    return (d_anticipated_audio_id, d_terminated)


def create_client():
    # Client
    # ======
    host = "127.0.0.1"
    port = 2000
    point = TCP4ClientEndpoint(reactor, host, port)
    d_protocol = connectProtocol(point, FileTransportClient())

    return d_protocol
    
def test_send_file():
    audio_id = 101
    d_anticipated_audio_id, d_terminated = \
        create_server(
            "test_file_transport__test_send_file",
            audio_id
        )
    
    d_protocol = create_client()
    
    def gotProtocol(p):
        file_path = Path(
            "/Users/matthew/Desktop/VirtualChoir/Sounds/psallite.opus"
        )
        p.send_file(file_path, audio_id)
    d_protocol.addCallback(gotProtocol)

    return defer.gatherResults([
        d_protocol,
        d_anticipated_audio_id,
        d_terminated
    ])


def test_write():
    print("Starting test_write()")
    audio_id = 101
    d_anticipated_audio_id, d_terminated = \
        create_server(
            "test_file_transport__test_write",
            audio_id
        )
    
    d_protocol = create_client()
    
    def gotProtocol(p):
        print("in gotProtocol: p:", p)
        file_path = Path(
            "/Users/matthew/Desktop/VirtualChoir/Sounds/psallite.opus"
        )
        with open(file_path, "rb") as f:
            chunk_size = 1000
            p.open(audio_id)
            while True:
                data = f.read(chunk_size)
                if len(data) == 0:
                    # We've reached the end of the file
                    break
                p.write(data)
            p.close()
    d_protocol.addCallback(gotProtocol)

    return defer.gatherResults([
        d_protocol,
        d_anticipated_audio_id,
        d_terminated
    ])
