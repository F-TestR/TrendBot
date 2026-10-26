"""Posting to Discord webhooks: plain text, rich alert cards, and file attachments."""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

import config as C

UA = "roblox-trend-bot/1.2"

COLORS = {"new": 0x3BA55D, "surge": 0xFAA61A, "copy": 0x9B59B6, "heat": 0xED4245,
          "early": 0x5865F2, "update": 0x95A5A6, "breakout": 0xE67E22,
          "chart": 0x1ABC9C, "predict": 0xF1C40F, "theme": 0x2ECC71, "bridge": 0x00B0F4,
          "longterm": 0x8E7CC3, "future": 0xE91E63, "cp": 0x00B894, "trend": 0xFF4757, "abroad": 0x00CEC9, "studio": 0xF9CA24}


def _multipart(payload, files):
    boundary = uuid.uuid4().hex
    parts = []
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\n"
                 f"Content-Type: application/json\r\n\r\n".encode() + json.dumps(payload).encode() + b"\r\n")
    for i, (name, data, ctype) in enumerate(files):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"files[{i}]\"; filename=\"{name}\"\r\n"
                     f"Content-Type: {ctype}\r\n\r\n".encode() + data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def send(url, payload, files=None):
    """POST one message. Retries on rate limits; never raises."""
    if files:
        body, ctype = _multipart(payload, files)
    else:
        body, ctype = json.dumps(payload).encode(), "application/json"
    for attempt in range(3):
        req = urllib.request.Request(url, data=body, headers={"Content-Type": ctype, "User-Agent": UA})
        try:
            urllib.request.urlopen(req, timeout=30).read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 2.0
                try:
                    wait = float(json.loads(e.read().decode()).get("retry_after", 2))
                except Exception:
                    pass
                time.sleep(min(wait, 10))
                continue
            print(f"Discord error {e.code}: {e.read()[:300]}", file=sys.stderr)
            break
        except (urllib.error.URLError, OSError) as e:
            print(f"Couldn't reach Discord ({e}); will try again next run.", file=sys.stderr)
            if attempt == 2:
                break
            time.sleep(2)
    time.sleep(0.5)


def edit_interaction(app_id, token, payload):
    """Replace a slash command's "thinking…" message with the answer. Returns True on success."""
    url = f"https://discord.com/api/v10/webhooks/{app_id}/{token}/messages/@original"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="PATCH",
                                 headers={"Content-Type": "application/json", "User-Agent": UA})
    try:
        urllib.request.urlopen(req, timeout=30).read()
        return True
    except urllib.error.HTTPError as e:
        print(f"Discord reply failed {e.code}: {e.read()[:300]}", file=sys.stderr)
    except (urllib.error.URLError, OSError) as e:
        print(f"Couldn't reach Discord for the reply: {e}", file=sys.stderr)
    return False


def post_text(url, text, dry_run=False, label="", files=None):
    """Long text split into ~1,900-char messages; files go with the last one."""
    chunks, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > 1900:
            chunks.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        chunks.append(cur)
    for i, chunk in enumerate(chunks):
        last = i == len(chunks) - 1
        if dry_run or not url:
            print(f"----- [{label or 'discord'}] -----\n{chunk}")
            if last and files:
                print(f"(+ attached: {', '.join(f[0] for f in files)})")
            continue
        send(url, {"content": chunk, "allowed_mentions": {"parse": []}}, files if last else None)


def _ping_payload():
    uid = str(C.PING_USER_ID or "").strip()
    if not uid.isdigit():
        return {}
    return {"content": f"<@{uid}> big signal ⬇️", "allowed_mentions": {"users": [uid]}}


def post_alerts(url, alerts, header, icons, dry_run=False):
    """alerts: list of dicts {kind, title, desc, url, fields:[(name, value)], gid, ping, text}"""
    if not alerts:
        return
    if not C.RICH_CARDS or dry_run or not url:
        text = header + "\n" + "\n".join(a["text"] for a in alerts)
        if any(a.get("ping") for a in alerts) and _ping_payload():
            text = _ping_payload()["content"] + "\n" + text
        post_text(url, text, dry_run, "alerts")
        return
    embeds = []
    for a in alerts:
        e = {"title": a["title"][:256], "description": a.get("desc", "")[:4000],
             "color": COLORS.get(a["kind"], 0x5865F2)}
        if a.get("url"):
            e["url"] = a["url"]
        if a.get("fields"):
            e["fields"] = [{"name": n[:256], "value": str(v)[:1024], "inline": True} for n, v in a["fields"][:24]]
        if a.get("gid") and icons.get(a["gid"]):
            e["thumbnail"] = {"url": icons[a["gid"]]}
        if a.get("image"):
            e["image"] = {"url": a["image"]}
        embeds.append((a, e))
    # Discord: max 10 embeds and ~6,000 characters per message
    batch, size, first = [], 0, True
    def flush():
        nonlocal batch, size, first
        if not batch:
            return
        payload = {"content": header if first else "", "embeds": [e for _, e in batch],
                   "allowed_mentions": {"parse": []}}
        if any(a.get("ping") for a, _ in batch):
            p = _ping_payload()
            if p:
                payload["content"] = (p["content"] + "\n" + payload["content"]).strip()
                payload["allowed_mentions"] = p["allowed_mentions"]
        send(url, payload)
        batch, size, first = [], 0, False
    for a, e in embeds:
        n = len(json.dumps(e))
        if len(batch) >= 10 or size + n > 5500:
            flush()
        batch.append((a, e))
        size += n
    flush()
