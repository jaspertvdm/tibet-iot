"""tibet-iot: IoT Transport Layer for TIBET.

tibet-ping is the proto layer (packets, trust, airlock).
tibet-iot is the transport layer: UDP transport, LAN discovery, mesh relay.

First async package in the TIBET ecosystem.

Usage::

    import asyncio
    from tibet_iot import IoTNode, TransportConfig

    async def main():
        node = IoTNode("jis:home:hub")
        node.set_trust("jis:home:sensor", 0.9)
        await node.start()

        response = await node.send_ping(
            target="jis:home:sensor",
            addr=("192.168.1.42", 7150),
            intent="temperature.read",
            purpose="Check room temperature",
        )

        if response:
            print(response.decision)  # PingDecision.ACCEPT

        await node.stop()

    asyncio.run(main())
"""

from .codec import PacketCodec, FrameFlags, MAGIC, VERSION, HEADER_SIZE
from .peers import PeerTracker, PeerRecord
from .relay import MeshRelay
from .transport import (
    Transport,
    UDPTransport,
    TransportConfig,
    DEFAULT_PORT,
    DISCOVERY_PORT,
)
from .discovery import NetworkDiscovery, MULTICAST_GROUP, MULTICAST_TTL
from .node import IoTNode

__version__ = "0.1.0"

__all__ = [
    # Node (main entry point)
    "IoTNode",
    # Transport
    "Transport",
    "UDPTransport",
    "TransportConfig",
    "DEFAULT_PORT",
    "DISCOVERY_PORT",
    # Codec
    "PacketCodec",
    "FrameFlags",
    "MAGIC",
    "VERSION",
    "HEADER_SIZE",
    # Peers
    "PeerTracker",
    "PeerRecord",
    # Relay
    "MeshRelay",
    # Discovery
    "NetworkDiscovery",
    "MULTICAST_GROUP",
    "MULTICAST_TTL",
]
