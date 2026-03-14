# tibet-iot

IoT Transport Layer for TIBET — UDP transport, LAN discovery, and mesh relay over the tibet-ping protocol.

## What

**tibet-ping** is the proto layer: packets, trust, airlock.
**tibet-iot** is the transport layer: actually sending PingPackets over UDP, discovering devices on LAN via multicast, and mesh relay for multi-hop forwarding.

First async package in the TIBET ecosystem.

## Install

```bash
pip install tibet-iot
```

## Quick Start

```python
import asyncio
from tibet_iot import IoTNode

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
        print(response.decision)

    await node.stop()

asyncio.run(main())
```

## CLI

```bash
tibet-iot listen --did jis:home:hub
tibet-iot send jis:home:sensor 192.168.1.42:7150 temperature.read
tibet-iot discover
tibet-iot demo
```

## Architecture

```
IoTNode (async, tibet-iot)
  ├── PingNode (sync, tibet-ping) — proto layer
  ├── Transport — network I/O (UDP)
  ├── PeerTracker — connection tracking
  ├── NetworkDiscovery — LAN multicast beacon
  └── MeshRelay — multi-hop forwarding
```

## Wire Format

```
Offset  Size  Field
0       2     Magic: 0x54 0x50 ("TP")
2       1     Version: 0x01
3       1     Flags: bit 0 = is_response, bit 1 = msgpack
4       4     Payload length (uint32, big-endian)
8       N     Payload (JSON or msgpack)
```

## Network

- **Port 7150** — Main transport (UDP)
- **Port 7151** — Discovery multicast
- **Multicast group** — `224.0.71.50`

## License

MIT
