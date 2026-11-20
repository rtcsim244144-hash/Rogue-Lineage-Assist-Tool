#!/usr/bin/env python3
"""A pretend housemate for testing alone: joins your house with an invite code and sends a moving HP bar and two draining buffs.
    python housemate_fake_player.py https://your-server-address INVITE-CODE [Name]
Leave it running; press Ctrl+C to stop (the pretend player disappears from your screen a few seconds later)."""
import json, sys, time, math, urllib.request, urllib.error


def call(base, path, payload):
    req = urllib.request.Request(base.rstrip("/") + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    base, code = sys.argv[1], sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else "Fake Merp"
    st, me = call(base, "/v1/join", {"code": code, "name": name})
    if st != 200:
        print("Could not join:", me.get("error", st))
        return
    print(f"Joined '{me['house_name']}' as {name}. Sending HP + buffs... (Ctrl+C to stop)")
    t0 = time.time()
    while True:
        t = time.time() - t0
        hp = int(60 + 40 * math.sin(t / 6.0))
        fire_left = 60 - (t % 60)
        tempest_left = 20 - (t % 20)
        buffs = [{"k": "fire", "b": 0, "l": round(fire_left, 1), "t": 60.0}, {"k": "tempest", "b": 1, "l": round(tempest_left, 1), "t": 20.0}]
        st, r = call(base, "/v1/sync", {"house": me["house"], "id": me["id"], "secret": me["secret"], "hp": hp, "buffs": buffs, "share": True})
        if st != 200:
            print("Stopped:", r.get("error", st))
            return
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("bye")
