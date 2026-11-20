#!/usr/bin/env python3
"""Housemate HP server for the Rogue Lineage Assist Tool.

A house has one Leader, any number of Officers and Members. Nobody joins with a shared password: an Officer or the Leader makes a
ONE-TIME invite code, the new player types it into their tool once, and it is used up. Members only get a private key of their own
(stored hashed here), so a removed member is locked out at once and nobody else is affected.

Run it anywhere that has Python 3.8+ (no packages):
    python3 housemate_server.py            # port 8080 (or $PORT); needs HTTPS in front of it when used over the internet
Settings (environment variables, all optional):
    PORT              the port (default 8080)
    DATA_FILE         where the houses are kept (default house_data.json next to this file)
    CREATE_KEY        if set, making a NEW house needs this key (so strangers can't make houses on your server)
    INVITE_HOURS      how long an invite code lives (default 24, at most 168)
    TRUST_PROXY       set to 1 when the server sits behind Render / Cloudflare / nginx (the real address comes from X-Forwarded-For)
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.environ.get("DATA_FILE") or os.path.join(HERE, "house_data.json")
CREATE_KEY = os.environ.get("CREATE_KEY") or ""
TRUST_PROXY = os.environ.get("TRUST_PROXY") == "1"      # behind Render / Cloudflare / nginx: the address comes from X-Forwarded-For
INVITE_HOURS = max(1, min(168, int(os.environ.get("INVITE_HOURS", "24") or 24)))

MEMBER_TTL = 6.0            # seconds without a message = offline
MAX_HOUSES = 300
MAX_MEMBERS = 40            # per house
MAX_INVITES = 20            # unused invites per house at once
MAX_BODY = 4096
RATE = 12.0                 # messages per second and address (each tool sends 2 / s)
SLOW_RATE = 10              # create / join / invite attempts per minute and address
BUFFS_MAX = 12
ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"          # no 0 O 1 I L: easy to read out loud / type
ROLES = ("leader", "officer", "member")

_lock = threading.RLock()
_houses = {}                # house id -> {"name", "created", "members": {mid: {...}}}
_invites = {}               # sha256(code) -> {"house", "by", "exp"}
_online = {}                # (house id, mid) -> {"hp", "buffs", "seen"}
_rate = {}
_slow = {}
HEX = re.compile(r"^[0-9a-f]{8,32}$")


# ---------------------------------------------------------------- storage
def load():
    global _houses, _invites
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        _houses = data.get("houses", {})
        _invites = data.get("invites", {})
    except FileNotFoundError:
        _houses, _invites = {}, {}
    except Exception:
        _houses, _invites = {}, {}


def save():
    """Writes everything (called after every change of a house; not for HP messages)."""
    with _lock:
        data = {"houses": _houses, "invites": _invites}
        try:
            d = os.path.dirname(DATA_FILE) or "."
            fd, tmp = tempfile.mkstemp(prefix=".house_", dir=d)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f)
            os.replace(tmp, DATA_FILE)
        except Exception:
            pass


# ---------------------------------------------------------------- helpers
def h(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def clean_name(v, default="Player"):
    s = "".join(ch for ch in str(v or "") if ch.isprintable())[:24].strip()
    return s or default


def clean_buffs(v):
    out = []
    if not isinstance(v, list):
        return out
    for b in v[:BUFFS_MAX]:
        try:
            k = str(b["k"])[:24]
            if not re.fullmatch(r"[a-z0-9_]+", k):
                continue
            left, tot = float(b["l"]), float(b["t"])
            if left != left or tot != tot:
                continue
            out.append({"k": k, "b": 1 if b.get("b") else 0, "l": round(max(-1.0, min(86400.0, left)), 1), "t": round(max(0.0, min(86400.0, tot)), 1)})
        except Exception:
            continue
    return out


def norm_code(code):
    return re.sub(r"[^A-Z0-9]", "", str(code or "").upper())


def new_code():
    raw = "".join(secrets.choice(ALPHABET) for _ in range(10))
    return raw[:5] + "-" + raw[5:]


class Err(Exception):
    def __init__(self, status, msg):
        super().__init__(msg)
        self.status, self.msg = status, msg


def auth(body):
    """(house, member id, member) of a valid request; Err otherwise."""
    hid, mid, sec = str(body.get("house", "")), str(body.get("id", "")), str(body.get("secret", ""))
    if not HEX.match(hid) or not HEX.match(mid) or not sec or len(sec) > 80:
        raise Err(400, "bad request")
    with _lock:
        house = _houses.get(hid)
        mem = house["members"].get(mid) if house else None
        ok = bool(mem) and hmac.compare_digest(mem["secret"], h(sec))
        if not ok:
            raise Err(403, "You are not in this house (any more).")
        return house, mid, mem


def purge_invites(now):
    for k in [k for k, v in _invites.items() if v["exp"] < now or v["house"] not in _houses]:
        _invites.pop(k, None)


def public_member(mid, m, online):
    return {"id": mid, "name": m["name"], "role": m["role"], "online": bool(online)}


# ---------------------------------------------------------------- actions
def do_create(body, now):
    if CREATE_KEY and not hmac.compare_digest(h(str(body.get("key", ""))), h(CREATE_KEY)):
        raise Err(403, "This server needs its house key to make a new house.")
    with _lock:
        if len(_houses) >= MAX_HOUSES:
            raise Err(503, "This server can't take more houses.")
        hid, mid, sec = secrets.token_hex(8), secrets.token_hex(6), secrets.token_urlsafe(24)
        _houses[hid] = {"name": clean_name(body.get("house_name"), "House"), "created": now,
                        "members": {mid: {"name": clean_name(body.get("name")), "role": "leader", "secret": h(sec), "joined": now}}}
        save()
    return {"house": hid, "id": mid, "secret": sec, "role": "leader", "house_name": _houses[hid]["name"]}


def do_invite(body, now):
    house, mid, mem = auth(body)
    if mem["role"] not in ("leader", "officer"):
        raise Err(403, "Only the Leader and Officers can make invite codes.")
    hours = INVITE_HOURS
    try:
        hours = max(1, min(INVITE_HOURS, int(body.get("hours", INVITE_HOURS))))
    except (TypeError, ValueError):
        pass
    with _lock:
        purge_invites(now)
        hid = str(body["house"])
        if sum(1 for v in _invites.values() if v["house"] == hid) >= MAX_INVITES:
            raise Err(429, "Too many unused invite codes. Wait for them to expire or be used.")
        if len(house["members"]) >= MAX_MEMBERS:
            raise Err(409, "The house is full.")
        code = new_code()
        _invites[h(norm_code(code))] = {"house": hid, "by": mid, "exp": now + hours * 3600.0, "code": code}
        save()
    return {"code": code, "hours": hours, "expires": now + hours * 3600.0}


def do_join(body, now):
    code = norm_code(body.get("code"))
    if len(code) != 10:
        raise Err(400, "That is not an invite code.")
    with _lock:
        purge_invites(now)
        inv = _invites.get(h(code))
        if not inv:
            raise Err(403, "That invite code is wrong, used up or expired. Ask an Officer for a new one.")
        house = _houses.get(inv["house"])
        if house is None or len(house["members"]) >= MAX_MEMBERS:
            raise Err(409, "The house is full.")
        _invites.pop(h(code), None)                                   # ONE use: gone before anything else happens
        mid, sec = secrets.token_hex(6), secrets.token_urlsafe(24)
        house["members"][mid] = {"name": clean_name(body.get("name")), "role": "member", "secret": h(sec), "joined": now}
        save()
        return {"house": inv["house"], "id": mid, "secret": sec, "role": "member", "house_name": house["name"]}


def do_roster(body, now):
    house, mid, mem = auth(body)
    with _lock:
        hid = str(body["house"])
        purge_invites(now)
        out = {"house_name": house["name"], "role": mem["role"],
               "members": [public_member(k, m, now - _online.get((hid, k), {}).get("seen", -1e9) <= MEMBER_TTL) for k, m in house["members"].items()]}
        order = {"leader": 0, "officer": 1, "member": 2}
        out["members"].sort(key=lambda m: (order[m["role"]], m["name"].lower()))
        if mem["role"] in ("leader", "officer"):
            out["invites"] = sorted([{"id": k[:16], "by": house["members"].get(v["by"], {}).get("name", "?"), "expires": v["exp"], "code": v.get("code", "")}
                                     for k, v in _invites.items() if v["house"] == hid and (mem["role"] == "leader" or v["by"] == mid)],
                                    key=lambda i: i["expires"])                     # (the Leader sees every code, an Officer only their own)
        return out


def do_invite_cancel(body, now):
    house, mid, mem = auth(body)
    if mem["role"] not in ("leader", "officer"):
        raise Err(403, "Only the Leader and Officers can cancel invite codes.")
    iid = str(body.get("invite") or "")
    with _lock:
        hid = str(body["house"])
        for k, v in list(_invites.items()):
            if v["house"] == hid and len(iid) >= 8 and k.startswith(iid) and (mem["role"] == "leader" or v["by"] == mid):
                _invites.pop(k, None)
                save()
                return {"ok": True}
    raise Err(404, "That invite code is gone already.")


def do_disband(body, now):
    house, mid, mem = auth(body)
    if mem["role"] != "leader":
        raise Err(403, "Only the Leader can disband the house.")
    with _lock:
        hid = str(body["house"])
        _houses.pop(hid, None)
        purge_invites(now)
        save()
    return {"ok": True}


def do_role(body, now):
    house, mid, mem = auth(body)
    if mem["role"] != "leader":
        raise Err(403, "Only the Leader can promote or demote.")
    target, role = str(body.get("target", "")), str(body.get("role", ""))
    with _lock:
        t = house["members"].get(target)
        if t is None or target == mid or role not in ("officer", "member"):
            raise Err(400, "That member can't be changed.")
        t["role"] = role
        save()
    return {"ok": True}


def do_kick(body, now):
    house, mid, mem = auth(body)
    target = str(body.get("target", ""))
    with _lock:
        t = house["members"].get(target)
        if t is None or target == mid:
            raise Err(400, "That member can't be removed.")
        if not (mem["role"] == "leader" or (mem["role"] == "officer" and t["role"] == "member")):
            raise Err(403, "You can't remove that member.")
        house["members"].pop(target, None)
        _online.pop((str(body["house"]), target), None)
        save()
    return {"ok": True}


def do_leave(body, now):
    house, mid, mem = auth(body)
    hid = str(body["house"])
    with _lock:
        if mem["role"] == "leader" and len(house["members"]) > 1:
            raise Err(409, "Hand the house to someone else first (Make Leader), then leave.")
        house["members"].pop(mid, None)
        _online.pop((hid, mid), None)
        if not house["members"]:
            _houses.pop(hid, None)                                    # the last one left: the house is gone
        save()
    return {"ok": True}


def do_transfer(body, now):
    house, mid, mem = auth(body)
    if mem["role"] != "leader":
        raise Err(403, "Only the Leader can hand the house over.")
    target = str(body.get("target", ""))
    with _lock:
        t = house["members"].get(target)
        if t is None or target == mid:
            raise Err(400, "Pick another member.")
        t["role"], mem["role"] = "leader", "officer"
        save()
    return {"ok": True}


def do_rename(body, now):
    house, mid, mem = auth(body)
    with _lock:
        mem["name"] = clean_name(body.get("name"), mem["name"])
        save()
    return {"ok": True}


def do_sync(body, now):
    house, mid, mem = auth(body)
    hid = str(body["house"])
    with _lock:
        for k in [k for k, v in _online.items() if now - v["seen"] > 30]:
            _online.pop(k, None)
        if body.get("share", True):
            hp = body.get("hp")
            try:
                hp = None if hp is None else max(0, min(100, int(round(float(hp)))))
            except (TypeError, ValueError):
                hp = None
            _online[(hid, mid)] = {"hp": hp, "buffs": clean_buffs(body.get("buffs")), "seen": now}
        else:
            _online.pop((hid, mid), None)
        others = []
        for k, m in house["members"].items():
            st = _online.get((hid, k))
            if k != mid and st and now - st["seen"] <= MEMBER_TTL:
                others.append({"id": k, "name": m["name"], "role": m["role"], "hp": st["hp"], "buffs": st["buffs"], "age": round(now - st["seen"], 2)})
        return {"members": others, "me": {"role": mem["role"], "name": mem["name"]}, "house_name": house["name"], "ttl": MEMBER_TTL}


ROUTES = {"/v1/create": (do_create, True), "/v1/join": (do_join, True), "/v1/invite": (do_invite, True), "/v1/invite_cancel": (do_invite_cancel, False), "/v1/disband": (do_disband, False), "/v1/roster": (do_roster, False),
          "/v1/role": (do_role, False), "/v1/kick": (do_kick, False), "/v1/leave": (do_leave, False), "/v1/transfer": (do_transfer, False),
          "/v1/rename": (do_rename, False), "/v1/sync": (do_sync, False)}
# (the second value: counted against the slow limit - the things that make or open something)


def too_fast(addr, now, slow):
    with _lock:
        t0, n = _rate.get(addr, (now, 0))
        if now - t0 >= 1.0:
            t0, n = now, 0
        n += 1
        _rate[addr] = (t0, n)
        bad = n > RATE
        if slow:
            s0, k = _slow.get(addr, (now, 0))
            if now - s0 >= 60.0:
                s0, k = now, 0
            k += 1
            _slow[addr] = (s0, k)
            bad = bad or k > SLOW_RATE
        if len(_rate) > 5000:
            for a in [a for a, (t, _n) in _rate.items() if now - t > 5]:
                _rate.pop(a, None)
            for a in [a for a, (t, _n) in _slow.items() if now - t > 70]:
                _slow.pop(a, None)
        return bad


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "rlat-house"

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        data = json.dumps(obj, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/health", "/v1/health"):
            self._send(200, {"ok": True, "service": "rlat-housemate", "version": 2, "needs_key": bool(CREATE_KEY)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        route = ROUTES.get(self.path)
        if route is None:
            self._send(404, {"error": "not found"})
            return
        fn, slow = route
        now = time.time()
        xff = self.headers.get("X-Forwarded-For") if TRUST_PROXY else None
        addr = xff.split(",")[-1].strip() if xff else self.client_address[0]          # (the last entry is the one OUR proxy added: can't be faked)
        if too_fast(addr, now, slow):
            self._send(429, {"error": "Too many tries. Wait a minute."})
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > MAX_BODY:
                self._send(413, {"error": "bad size"})
                return
            body = json.loads(self.rfile.read(n).decode("utf-8", "replace"))
            if not isinstance(body, dict):
                raise ValueError("not an object")
        except Exception:
            self._send(400, {"error": "bad request"})
            return
        try:
            self._send(200, fn(body, now))
        except Err as e:
            self._send(e.status, {"error": e.msg})
        except Exception:
            self._send(500, {"error": "server error"})


def make_server(host="0.0.0.0", port=8080):
    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    return srv


if __name__ == "__main__":
    load()
    port = int(os.environ.get("PORT", "8080"))
    print(f"Housemate server on port {port} ({len(_houses)} houses loaded, data file {DATA_FILE})", flush=True)
    make_server("0.0.0.0", port).serve_forever()
