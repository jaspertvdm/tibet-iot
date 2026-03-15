"""tibet-iot: DEPRECATED — merged into tibet-ping v0.2.0.

All transport functionality is now part of tibet-ping:

    # Old (tibet-iot)
    from tibet_iot import IoTNode, TransportConfig

    # New (tibet-ping >= 0.2.0)
    from tibet_ping.transport import IoTNode, TransportConfig

This package re-exports everything from tibet_ping.transport for
backward compatibility. Switch to tibet-ping and remove tibet-iot
from your dependencies.
"""

import warnings

warnings.warn(
    "tibet-iot is deprecated. Use 'from tibet_ping.transport import ...' instead. "
    "See: https://pypi.org/project/tibet-ping/",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from tibet-ping's transport subpackage
from tibet_ping.transport import (
    IoTNode,
    Transport,
    UDPTransport,
    TransportConfig,
    DEFAULT_PORT,
    DISCOVERY_PORT,
    PacketCodec,
    FrameFlags,
    MAGIC,
    VERSION,
    HEADER_SIZE,
    PeerTracker,
    PeerRecord,
    MeshRelay,
    NetworkDiscovery,
    MULTICAST_GROUP,
    MULTICAST_TTL,
)

__version__ = "0.1.1"

__all__ = [
    "IoTNode",
    "Transport",
    "UDPTransport",
    "TransportConfig",
    "DEFAULT_PORT",
    "DISCOVERY_PORT",
    "PacketCodec",
    "FrameFlags",
    "MAGIC",
    "VERSION",
    "HEADER_SIZE",
    "PeerTracker",
    "PeerRecord",
    "MeshRelay",
    "NetworkDiscovery",
    "MULTICAST_GROUP",
    "MULTICAST_TTL",
]
