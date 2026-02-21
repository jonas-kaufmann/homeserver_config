import os

from fritzconnection import FritzConnection


def get_external_ip() -> str:
    fritz_ip = os.getenv("FRITZ_IP", None)
    fritz_user = os.getenv("FRITZ_USER", None)
    fritz_pw = os.getenv("FRITZ_PW", None)

    if fritz_ip is None:
        raise EnvironmentError("FRITZ_IP not set")
    if fritz_user is None:
        raise EnvironmentError("FRITZ_USER not set")
    if fritz_pw is None:
        raise EnvironmentError("FRITZ_PW not set")

    fc = FritzConnection(
        address=fritz_ip, user=fritz_user, password=fritz_pw, timeout=10
    )
    ip = fc.call_action("WANIPConn1", "GetExternalIPAddress")["NewExternalIPAddress"]

    return ip
