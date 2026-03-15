"""tibet-iot CLI: DEPRECATED — use tibet-ping instead.

All commands are now available via tibet-ping:
    tibet-ping listen    (was: tibet-iot listen)
    tibet-ping send      (was: tibet-iot send)
    tibet-ping discover  (was: tibet-iot discover)
    tibet-ping net-demo  (was: tibet-iot demo)
"""

import warnings


def main() -> None:
    warnings.warn(
        "tibet-iot CLI is deprecated. Use 'tibet-ping' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from tibet_ping.cli import main as ping_main
    ping_main()
