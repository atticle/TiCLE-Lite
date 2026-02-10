import gc, sys, time, machine, json
import uasyncio as asyncio
from upaho.client import Client

LOGO = r"""
      ___  __          __
     / _ )/ /_ _____  / /__
    / _  / / // / _ \/  '_/
   /____/_/\_, /_//_/_/\_\
          /___/
"""

def _noop(*_): pass

def _patch_ssl_layer():
    try:
        import ssl
    except Exception:
        return

    if getattr(ssl, "_ticle_patched", False):
        return

    orig = getattr(ssl, "wrap_socket", None)

    def _need_wrap(s):
        return (not hasattr(s, "settimeout")) or (not hasattr(s, "ioctl"))

    class _Compat:
        __slots__ = ("_s", "_r")
        def __init__(self, sslsock, rawsock):
            self._s = sslsock
            self._r = rawsock

        def settimeout(self, t):
            r = self._r
            if r and hasattr(r, "settimeout"):
                try:
                    r.settimeout(t)
                except Exception:
                    pass
            return None

        def setblocking(self, flag):
            r = self._r
            if r and hasattr(r, "setblocking"):
                try:
                    r.setblocking(flag)
                except Exception:
                    pass
            return None

        def ioctl(self, req, arg):
            r = self._r
            if r and hasattr(r, "ioctl"):
                try:
                    return r.ioctl(req, arg)
                except Exception:
                    return 0
            try:
                return self._s.ioctl(req, arg)
            except Exception:
                return 0

        def fileno(self):
            try:
                return self._s.fileno()
            except Exception:
                try:
                    return self._r.fileno()
                except Exception:
                    return -1

        def close(self):
            try:
                self._s.close()
            except Exception:
                pass
            try:
                if self._r and self._r is not self._s:
                    self._r.close()
            except Exception:
                pass

        def __getattr__(self, name):
            return getattr(self._s, name)

    if orig:
        def wrap_socket(sock, *args, **kwargs):
            server_hostname = kwargs.get("server_hostname", None)
            try:
                ss = orig(sock, *args, **kwargs)
            except TypeError:
                try:
                    ss = orig(sock, server_hostname=server_hostname)
                except Exception:
                    ss = orig(sock)
            return _Compat(ss, sock) if _need_wrap(ss) else ss

        ssl.wrap_socket = wrap_socket

    if hasattr(ssl, "SSLContext"):
        try:
            _orig_ctx_wrap = ssl.SSLContext.wrap_socket

            def _ctx_wrap(self, sock, *args, **kwargs):
                server_hostname = kwargs.get("server_hostname", None)
                try:
                    ss = _orig_ctx_wrap(self, sock, *args, **kwargs)
                except TypeError:
                    try:
                        ss = _orig_ctx_wrap(self, sock, server_hostname=server_hostname)
                    except Exception:
                        ss = _orig_ctx_wrap(self, sock)
                return _Compat(ss, sock) if _need_wrap(ss) else ss

            ssl.SSLContext.wrap_socket = _ctx_wrap
        except Exception:
            pass

    ssl._ticle_patched = True


class BlynkDevice:
    def __init__(
        self,
        template_id: str,
        auth_token: str,
        broker: str | None = None,
        firmware_version: str = "0.0.1",
        cafile: str = "ISRG_Root_X1.der",
        on_connected=_noop,
        on_disconnected=_noop,
        on_message=_noop,
        keepalive: int = 45,
        tls: bool = True,
        port: int | None = None,
    ):
        print(LOGO)

        self.template_id = template_id
        self.auth_token = auth_token
        self.broker = broker or "blynk.cloud"
        self.firmware_version = firmware_version
        self.cafile = cafile

        self.on_connected = on_connected
        self.on_disconnected = on_disconnected
        self.user_on_message = on_message

        self.keepalive = keepalive
        self._tls = tls
        self._port = port if port is not None else (8883 if tls else 1883)

        self._pending_subs = []
        self._pending_pubs = []

        _patch_ssl_layer()

        self._mqtt = Client(client_id="")
        self._mqtt.username_pw_set("device", self.auth_token)
        self._mqtt.on_message = self._on_message

        if self._tls:
            try:
                self._mqtt.tls_set(self.cafile)
            except Exception as e:
                print("[MQTT ERROR] tls_set failed:", e)

    async def run(self):
        while True:
            await asyncio.sleep_ms(10)

            if not self._mqtt.is_connected():
                if self._tls:
                    while not self._update_ntp_time():
                        await asyncio.sleep(1)

                try:
                    self._mqtt.disconnect()
                except Exception:
                    pass

                gc.collect()

                try:
                    rc = self._mqtt.connect(self.broker, self._port, self.keepalive)
                    if rc != 0 or (not self._mqtt.is_connected()):
                        raise OSError(rc if rc else 130)
                    self._after_connect()
                except Exception as e:
                    print("[MQTT ERROR] connect failed:", e)
                    await asyncio.sleep(5)
                    continue

            try:
                rc = self._mqtt.loop(0.2, 10)
                if rc != 0:
                    raise OSError(rc)
            except Exception as e:
                print("[MQTT ERROR] loop failed:", e)
                try:
                    self.on_disconnected()
                except Exception:
                    pass
                await asyncio.sleep(1)

    def publish(self, topic: str | bytes, payload: str | bytes, retain: bool = False, qos: int = 0):
        t = topic.decode() if isinstance(topic, (bytes, bytearray)) else str(topic)
        p = payload if isinstance(payload, (bytes, bytearray)) else str(payload)

        if self._mqtt.is_connected():
            try:
                self._mqtt.publish(t, p, qos, retain)
                return
            except Exception:
                pass

        self._pending_pubs.append((t, p, retain, qos))
        if len(self._pending_pubs) > 30:
            self._pending_pubs.pop(0)

    def subscribe(self, topic: str | bytes, qos: int = 0):
        t = topic.decode() if isinstance(topic, (bytes, bytearray)) else str(topic)

        if self._mqtt.is_connected():
            try:
                self._mqtt.subscribe(t, qos)
                return
            except Exception:
                pass

        self._pending_subs.append((t, qos))
        if len(self._pending_subs) > 30:
            self._pending_subs.pop(0)

    def _after_connect(self):
        try:
            self._mqtt.subscribe("downlink/#", 0)
        except Exception:
            pass

        info = {
            "type": self.template_id,
            "tmpl": self.template_id,
            "ver": self.firmware_version,
            "rxbuff": 1024,
        }
        try:
            self._mqtt.publish("info/mcu", json.dumps(info), 0, False)
        except Exception:
            pass

        for t, q in self._pending_subs:
            try:
                self._mqtt.subscribe(t, q)
            except Exception:
                pass
        self._pending_subs.clear()

        for t, p, r, q in self._pending_pubs:
            try:
                self._mqtt.publish(t, p, q, r)
            except Exception:
                pass
        self._pending_pubs.clear()

        try:
            self.on_connected()
        except Exception:
            pass

    def _on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload
        except Exception:
            return

        tb = topic if isinstance(topic, (bytes, bytearray)) else str(topic).encode()
        pb = payload if isinstance(payload, (bytes, bytearray)) else str(payload).encode()
        retained = bool(getattr(msg, "retain", False))
        dup = bool(getattr(msg, "dup", False))

        try:
            ts = tb.decode()
        except Exception:
            ts = ""

        if ts == "downlink/reboot":
            machine.reset()
            return
        if ts == "downlink/ping":
            return

        try:
            self.user_on_message(tb, pb, retained, dup)
        except Exception:
            pass

    @staticmethod
    def _time2str(t):
        y, m, d, H, M, S, w, _ = t
        a = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[w]
        return f"{a} {y}-{m:02d}-{d:02d} {H:02d}:{M:02d}:{S:02d}"

    @classmethod
    def _update_ntp_time(cls) -> bool:
        Jan24 = 756_864_000 if (time.gmtime(0)[0] == 2000) else 1_704_067_200
        if time.time() > Jan24:
            return True
        try:
            import ntptime
            ntptime.timeout = 5
            ntptime.settime()
            if time.time() > Jan24:
                print("UTC Time:", cls._time2str(time.gmtime()))
                return True
        except Exception:
            pass
        return False
