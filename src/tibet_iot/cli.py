"""CLI for tibet-iot: listen, send, discover, demo.

Usage:
    tibet-iot listen [--port PORT] [--did DID]
    tibet-iot send <did> <host:port> <intent> [--purpose PURPOSE]
    tibet-iot discover [--port PORT] [--did DID]
    tibet-iot demo
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from tibet_ping import PingDecision

from .node import IoTNode
from .transport import TransportConfig, UDPTransport, DEFAULT_PORT

logger = logging.getLogger("tibet_iot")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="tibet-iot",
        description="TIBET IoT Transport Layer — UDP transport, discovery, mesh relay",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    sub = parser.add_subparsers(dest="command", help="Command")

    # listen
    p_listen = sub.add_parser("listen", help="Start node, listen for pings")
    p_listen.add_argument("--port", type=int, default=DEFAULT_PORT, help="UDP port")
    p_listen.add_argument("--did", default="jis:iot:node", help="Device DID")

    # send
    p_send = sub.add_parser("send", help="Send a ping to a target")
    p_send.add_argument("did", help="Target device DID")
    p_send.add_argument("addr", help="Target address (host:port)")
    p_send.add_argument("intent", help="Ping intent")
    p_send.add_argument("--purpose", default="CLI ping", help="Purpose description")
    p_send.add_argument("--port", type=int, default=0, help="Local bind port (0=random)")
    p_send.add_argument("--my-did", default="jis:iot:cli", help="Our device DID")

    # discover
    p_disc = sub.add_parser("discover", help="Broadcast discovery")
    p_disc.add_argument("--port", type=int, default=DEFAULT_PORT, help="UDP port")
    p_disc.add_argument("--did", default="jis:iot:node", help="Device DID")
    p_disc.add_argument(
        "--timeout", type=float, default=5.0, help="Listen timeout (seconds)"
    )

    # demo
    sub.add_parser("demo", help="Run two local nodes, ping back and forth")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    if args.command == "listen":
        asyncio.run(_cmd_listen(args))
    elif args.command == "send":
        asyncio.run(_cmd_send(args))
    elif args.command == "discover":
        asyncio.run(_cmd_discover(args))
    elif args.command == "demo":
        asyncio.run(_cmd_demo())
    else:
        parser.print_help()
        sys.exit(1)


async def _cmd_listen(args: argparse.Namespace) -> None:
    config = TransportConfig(bind_port=args.port)
    node = IoTNode(args.did, config=config)
    await node.start()
    print(f"Listening on :{args.port} as {args.did}")
    print("Press Ctrl+C to stop")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await node.stop()


async def _cmd_send(args: argparse.Namespace) -> None:
    host, port_str = args.addr.rsplit(":", 1)
    target_addr = (host, int(port_str))

    config = TransportConfig(bind_port=args.port)
    node = IoTNode(args.my_did, config=config)
    await node.start()

    print(f"Sending ping to {args.did} at {args.addr}")
    print(f"  intent: {args.intent}")
    print(f"  purpose: {args.purpose}")

    try:
        response = await node.send_ping(
            target=args.did,
            addr=target_addr,
            intent=args.intent,
            purpose=args.purpose,
        )
        if response:
            print(f"\nResponse: {response.decision.value}")
            print(f"  zone: {response.airlock_zone}")
            print(f"  trust: {response.trust_score}")
            if response.payload:
                print(f"  payload: {response.payload}")
        else:
            print("\nNo response (timeout)")
    finally:
        await node.stop()


async def _cmd_discover(args: argparse.Namespace) -> None:
    config = TransportConfig(bind_port=args.port)
    node = IoTNode(args.did, config=config)

    discovered: list[str] = []

    async def on_found(did: str, addr: tuple, resp: object) -> None:
        discovered.append(f"{did} at {addr[0]}:{addr[1]}")
        print(f"  Found: {did} at {addr[0]}:{addr[1]}")

    node.discovery.on_discovered(on_found)
    await node.start()

    print(f"Broadcasting discovery as {args.did}...")
    await node.discovery.broadcast_discover()

    print(f"Listening for {args.timeout}s...")
    await asyncio.sleep(args.timeout)

    await node.stop()
    print(f"\nDiscovered {len(discovered)} peer(s)")


async def _cmd_demo() -> None:
    """Demo: two nodes on localhost, ping back and forth."""
    print("=== TIBET IoT Demo ===\n")

    # Import MockTransport for in-process demo
    from .transport import Transport

    # Use real UDP on two different ports
    config_a = TransportConfig(bind_port=17150)
    config_b = TransportConfig(bind_port=17151)

    node_a = IoTNode("jis:demo:hub", config=config_a, heartbeat_interval=300, discovery_interval=300)
    node_b = IoTNode("jis:demo:sensor", config=config_b, heartbeat_interval=300, discovery_interval=300)

    # Hub trusts sensor
    node_a.set_trust("jis:demo:sensor", 0.9)

    await node_a.start()
    await node_b.start()

    print(f"Node A (hub):    {node_a.device_did} on :17150")
    print(f"Node B (sensor): {node_b.device_did} on :17151")
    print()

    # Sensor pings hub
    print("1. Sensor -> Hub: temperature.report")
    response = await node_b.send_ping(
        target="jis:demo:hub",
        addr=("127.0.0.1", 17150),
        intent="temperature.report",
        purpose="Demo temperature reading",
        payload={"celsius": 21.5},
    )

    if response:
        print(f"   Response: {response.decision.value} (zone: {response.airlock_zone})")
        print(f"   Trust: {response.trust_score}")
    else:
        print("   No response (timeout)")

    print()

    # Unknown node pings hub
    config_c = TransportConfig(bind_port=17152)
    node_c = IoTNode("jis:demo:unknown", config=config_c, heartbeat_interval=300, discovery_interval=300)
    await node_c.start()

    print("2. Unknown -> Hub: door.unlock (should be ROOD)")
    response = await node_c.send_ping(
        target="jis:demo:hub",
        addr=("127.0.0.1", 17150),
        intent="door.unlock",
        purpose="Unauthorized access attempt",
        timeout=3.0,
    )

    if response:
        print(f"   Response: {response.decision.value}")
    else:
        print("   No response (silent drop — ROOD)")

    print()
    print("Hub stats:", node_a.stats()["peers"])

    await node_a.stop()
    await node_b.stop()
    await node_c.stop()
    print("\n=== Demo complete ===")
