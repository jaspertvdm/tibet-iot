"""Start a hub node that trusts laptop and listens on port 7150."""
import asyncio
import logging
from tibet_iot import IoTNode, TransportConfig

logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

async def main():
    config = TransportConfig(bind_port=7150)
    node = IoTNode("jis:dl360:hub", config=config)

    # Trust de laptop
    node.set_trust("jis:laptop:jasper", 0.95)

    await node.start()
    print(f"\nHub listening on 0.0.0.0:7150 as jis:dl360:hub")
    print(f"Trusting: jis:laptop:jasper (0.95)")
    print(f"DL360 IP: 192.168.4.76")
    print(f"\nVanaf laptop:")
    print(f"  pip install tibet-iot")
    print(f"  tibet-iot send jis:dl360:hub 192.168.4.76:7150 hello.world --my-did jis:laptop:jasper")
    print(f"\nWachten op pings... (Ctrl+C om te stoppen)")

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await node.stop()

asyncio.run(main())
