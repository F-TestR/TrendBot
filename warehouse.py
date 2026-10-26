"""
The bot's long-term database (SQLite, one file: state/trendbot.db).

  games       one row per game: studio, genre, creation date, mechanics
  daily       one row per game per day: peak/avg players, visits, favourites,
              likes, RoWatcher's breakout score, chart position, YouTube,
              Twitch and community numbers
  hourly      hourly peak players for young games (what the model learns from)
  alerts      every alert the bot sent, so it can check later whether it was right
  predictions every model prediction, for the same reason
  backfill    which games have had their past history downloaded
  meta        small key/value store (model weights, last backup...)

Between runs the file lives in GitHub's Actions cache. If the repo is private,
it is also backed up once a day to the repo's Releases page (see backup()).
"""
import gzip
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import config as C

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(HERE, "state", "trendbot.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
  uid TEXT PRIMARY KEY, name TEXT, place TEXT, creator_id TEXT, creator_type TEXT, creator_name TEXT,
  genre TEXT, subgenre TEXT, created TEXT, first_seen_rw TEXT, first_seen_bot TEXT, last_seen TEXT,
  mechanics TEXT, discovery TEXT);
CREATE TABLE IF NOT EXISTS daily (
  uid TEXT, day TEXT, peak INTEGER, low INTEGER, sum_ccu INTEGER DEFAULT 0, n INTEGER DEFAULT 0,
  visits INTEGER, favorites INTEGER, likes INTEGER, dislikes INTEGER, rw_score REAL, fav_conv REAL,
  algo_reach REAL, rev_usd REAL, chart_best INTEGER, yt_n INTEGER, yt_views INTEGER, yt_big INTEGER,
  tw_v INTEGER, grp INTEGER, dc INTEGER, updated TEXT, src TEXT,
  PRIMARY KEY (uid, day));
CREATE TABLE IF NOT EXISTS hourly (uid TEXT, hour TEXT, ccu INTEGER, visits INTEGER, PRIMARY KEY (uid, hour));
CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, day TEXT, uid TEXT,
  kind TEXT, players INTEGER, score REAL);
CREATE TABLE IF NOT EXISTS predictions (day TEXT, uid TEXT, prob REAL, players INTEGER, model TEXT,
  PRIMARY KEY (day, uid));
CREATE TABLE IF NOT EXISTS backfill (uid TEXT PRIMARY KEY, ts TEXT, points INTEGER, status TEXT);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
CREATE INDEX IF NOT EXISTS daily_day ON daily(day);
CREATE INDEX IF NOT EXISTS games_creator ON games(creator_id);
"""


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def meta_get(db, k, default=None):
    r = db.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
    return json.loads(r["v"]) if r else default


def meta_set(db, k, v):
    db.execute("INSERT INTO meta(k, v) VALUES(?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, json.dumps(v)))


def _int(v):
    try:
        return int(float(v)) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _float(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ writes ---

def record_snapshot(db, g, t, mechanics=""):
    """g: a raw game dict from RoWatcher's /games list (rich fields). One live reading."""
    uid = str(g.get("universeId") or g.get("_id") or g.get("id") or "")
    if not uid:
        return
    day, hour = t.strftime("%Y-%m-%d"), t.strftime("%Y-%m-%dT%H")
    playing = _int(g.get("playing")) or 0
    created = (g.get("robloxCreatedAt") or "")[:10] or None
    db.execute("""INSERT INTO games(uid, name, place, creator_id, creator_type, creator_name, genre, subgenre,
                    created, first_seen_rw, first_seen_bot, last_seen, mechanics, discovery)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                  ON CONFLICT(uid) DO UPDATE SET name=excluded.name, place=COALESCE(excluded.place, place),
                    creator_id=COALESCE(excluded.creator_id, creator_id), creator_type=COALESCE(excluded.creator_type, creator_type),
                    creator_name=COALESCE(excluded.creator_name, creator_name), genre=COALESCE(excluded.genre, genre),
                    subgenre=COALESCE(excluded.subgenre, subgenre), created=COALESCE(excluded.created, created),
                    first_seen_rw=COALESCE(first_seen_rw, excluded.first_seen_rw), last_seen=excluded.last_seen,
                    mechanics=excluded.mechanics, discovery=COALESCE(excluded.discovery, discovery)""",
               (uid, g.get("name"), str(g.get("rootPlaceId") or "") or None, str(g.get("creatorId") or "") or None,
                g.get("creatorType"), g.get("creatorName"), g.get("genre"), g.get("subgenre"), created,
                (g.get("firstSeen") or "")[:10] or None, day, day, mechanics, g.get("discoverySource")))
    rev = None
    re_ = g.get("revenueEstimate") or {}
    if isinstance(re_, dict):
        rev = _float(((re_.get("expected") or {}).get("dailyUsd")))
    db.execute("""INSERT INTO daily(uid, day, peak, low, sum_ccu, n, visits, favorites, likes, dislikes, rw_score,
                    fav_conv, algo_reach, rev_usd, src)
                  VALUES(?,?,?,?,?,1,?,?,?,?,?,?,?,?,'live')
                  ON CONFLICT(uid, day) DO UPDATE SET peak=MAX(COALESCE(peak,0), excluded.peak),
                    low=MIN(COALESCE(low, excluded.low), excluded.low), sum_ccu=sum_ccu+excluded.sum_ccu, n=n+1,
                    visits=COALESCE(excluded.visits, visits), favorites=COALESCE(excluded.favorites, favorites),
                    likes=COALESCE(excluded.likes, likes), dislikes=COALESCE(excluded.dislikes, dislikes),
                    rw_score=COALESCE(excluded.rw_score, rw_score), fav_conv=COALESCE(excluded.fav_conv, fav_conv),
                    algo_reach=COALESCE(excluded.algo_reach, algo_reach), rev_usd=COALESCE(excluded.rev_usd, rev_usd),
                    src='live'""",
               (uid, day, playing, playing, playing, _int(g.get("visits")), _int(g.get("favorites")),
                _int(g.get("likes")), _int(g.get("dislikes")), _float(g.get("breakoutScore")),
                _float(g.get("favConversion")), _float(g.get("algoReach")), rev))
    if playing >= 50 and created and \
            (t - datetime.strptime(created, "%Y-%m-%d").replace(tzinfo=timezone.utc)).days <= C.HOURLY_MAX_AGE_DAYS:
        db.execute("""INSERT INTO hourly(uid, hour, ccu, visits) VALUES(?,?,?,?)
                      ON CONFLICT(uid, hour) DO UPDATE SET ccu=MAX(ccu, excluded.ccu),
                        visits=COALESCE(excluded.visits, visits)""", (uid, hour, playing, _int(g.get("visits"))))


def record_chart(db, games, t):
    day = t.strftime("%Y-%m-%d")
    for rank, g in enumerate(games, 1):
        uid = str(g.get("universeId") or "")
        if not uid:
            continue
        db.execute("""INSERT INTO daily(uid, day, chart_best, rw_score) VALUES(?,?,?,?)
                      ON CONFLICT(uid, day) DO UPDATE SET chart_best=MIN(COALESCE(chart_best, 9999), excluded.chart_best),
                        rw_score=COALESCE(excluded.rw_score, rw_score)""",
                   (uid, day, rank, _float(g.get("breakoutScore"))))


def record_history(db, uid, points, created=None):
    """Backfill: RoWatcher history points [{time, playing, visits}] -> hourly + daily rows."""
    hourly, daily = {}, {}
    for p in points:
        ts = (p.get("time") or "")
        if len(ts) < 13:
            continue
        playing = _int(p.get("playing")) or 0
        visits = _int(p.get("visits"))
        h, d = ts[:13], ts[:10]
        cur = hourly.get(h)
        hourly[h] = (max(cur[0], playing) if cur else playing, visits if visits is not None else (cur[1] if cur else None))
        dd = daily.setdefault(d, [0, None, 0, 0, None])
        dd[0] = max(dd[0], playing)
        dd[1] = playing if dd[1] is None else min(dd[1], playing)
        dd[2] += playing
        dd[3] += 1
        if visits is not None:
            dd[4] = visits
    young_until = None
    if created:
        young_until = (datetime.strptime(created, "%Y-%m-%d") + timedelta(days=C.HOURLY_MAX_AGE_DAYS)).strftime("%Y-%m-%dT%H")
    db.executemany("""INSERT INTO hourly(uid, hour, ccu, visits) VALUES(?,?,?,?)
                      ON CONFLICT(uid, hour) DO UPDATE SET ccu=MAX(ccu, excluded.ccu)""",
                   [(uid, h, v[0], v[1]) for h, v in hourly.items()
                    if v[0] >= 50 and (young_until is None or h <= young_until)])
    # never overwrite days the bot measured live
    db.executemany("""INSERT INTO daily(uid, day, peak, low, sum_ccu, n, visits, src) VALUES(?,?,?,?,?,?,?,'backfill')
                      ON CONFLICT(uid, day) DO UPDATE SET
                        peak=CASE WHEN src='live' THEN peak ELSE MAX(COALESCE(peak,0), excluded.peak) END,
                        low=CASE WHEN src='live' THEN low ELSE excluded.low END,
                        sum_ccu=CASE WHEN src='live' THEN sum_ccu ELSE excluded.sum_ccu END,
                        n=CASE WHEN src='live' THEN n ELSE excluded.n END,
                        visits=COALESCE(visits, excluded.visits),
                        src=CASE WHEN src='live' THEN 'live' ELSE 'backfill' END""",
                   [(uid, d, v[0], v[1], v[2], v[3], v[4]) for d, v in daily.items()])
    return len(points)


def record_alert(db, t, uid, kind, players, score=None):
    db.execute("INSERT INTO alerts(ts, day, uid, kind, players, score) VALUES(?,?,?,?,?,?)",
               (t.isoformat(), t.strftime("%Y-%m-%d"), uid, kind, players, score))


def record_sources_day(db, day, rows):
    """rows: {uid: dict(yt_n, yt_views, yt_big, tw_v, grp, dc, updated)} for a finished day."""
    for uid, r in rows.items():
        db.execute("""INSERT INTO daily(uid, day, yt_n, yt_views, yt_big, tw_v, grp, dc, updated) VALUES(?,?,?,?,?,?,?,?,?)
                      ON CONFLICT(uid, day) DO UPDATE SET yt_n=excluded.yt_n, yt_views=excluded.yt_views,
                        yt_big=excluded.yt_big, tw_v=COALESCE(excluded.tw_v, tw_v), grp=COALESCE(excluded.grp, grp),
                        dc=COALESCE(excluded.dc, dc), updated=COALESCE(excluded.updated, updated)""",
                   (uid, day, r.get("yt_n"), r.get("yt_views"), r.get("yt_big"), r.get("tw_v"),
                    r.get("grp"), r.get("dc"), r.get("updated")))


def prune(db, today):
    cut_h = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=C.HOURLY_KEEP_DAYS)).strftime("%Y-%m-%dT00")
    db.execute("DELETE FROM hourly WHERE hour < ?", (cut_h,))
    cut_d = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=C.DAILY_KEEP_DAYS)).strftime("%Y-%m-%d")
    db.execute("DELETE FROM daily WHERE day < ?", (cut_d,))


# ------------------------------------------------------------------ reads ---

def series(db, uid, since=None):
    q = "SELECT day, peak FROM daily WHERE uid=? AND peak IS NOT NULL" + (" AND day>=?" if since else "") + " ORDER BY day"
    return {r["day"]: r["peak"] for r in db.execute(q, (uid, since) if since else (uid,))}


def creator_best(db, creator_id, exclude_uid=None, before=None):
    """Best daily peak any OTHER game by this studio reached (optionally before a date)."""
    if not creator_id:
        return 0
    q = """SELECT MAX(d.peak) AS m FROM daily d JOIN games g ON g.uid=d.uid
           WHERE g.creator_id=? AND d.uid!=?""" + (" AND d.day<?" if before else "")
    args = (creator_id, exclude_uid or "") + ((before,) if before else ())
    r = db.execute(q, args).fetchone()
    return r["m"] or 0


def stats(db):
    out = {}
    for t in ("games", "daily", "hourly", "alerts", "predictions", "backfill"):
        out[t] = db.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()["c"]
    out["mb"] = round(os.path.getsize(DB_PATH) / 1e6, 1) if os.path.exists(DB_PATH) else 0
    return out


# ------------------------------------------------------------------ backup ---

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def _gh(method, url, token, data=None, ctype="application/json", accept="application/vnd.github+json"):
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Accept": accept, "User-Agent": "roblox-trend-bot",
        "X-GitHub-Api-Version": "2022-11-28", **({"Content-Type": ctype} if data is not None else {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
        return json.loads(body) if body and accept.endswith("json") else body


def _release(repo, token, create=False):
    try:
        return _gh("GET", f"https://api.github.com/repos/{repo}/releases/tags/{C.BACKUP_TAG}", token)
    except urllib.error.HTTPError as e:
        if e.code != 404 or not create:
            raise
    return _gh("POST", f"https://api.github.com/repos/{repo}/releases", token, json.dumps({
        "tag_name": C.BACKUP_TAG, "name": "Trend bot database backup",
        "body": "Automatic daily backup of the trend bot's database. Don't delete — the bot restores from it.",
        "prerelease": True}).encode())


def repo_is_private(repo, token):
    try:
        return bool(_gh("GET", f"https://api.github.com/repos/{repo}", token).get("private"))
    except Exception as e:
        print(f"couldn't check repo visibility: {e}", file=sys.stderr)
        return None


ENC_ASSET = "trendbot-backup.tar.gz.enc"


def _openssl(args, data, password):
    import subprocess
    env = dict(os.environ, TB_PASS=password)
    r = subprocess.run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-md", "sha256",
                        "-pass", "env:TB_PASS"] + args, input=data, capture_output=True, env=env, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[:200])
    return r.stdout


def _bundle(db):
    """tar.gz of the database and state.json (the bot's whole memory)."""
    import io
    import tarfile
    db.commit()
    tmp = DB_PATH + ".bak"
    dst = sqlite3.connect(tmp)
    db.backup(dst)
    dst.close()
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(tmp, arcname="trendbot.db")
        sp = os.environ.get("STATE_PATH")
        if sp and os.path.exists(sp):
            tar.add(sp, arcname="state.json")
    os.remove(tmp)
    return buf.getvalue()


def backup_encrypted(db, repo, token, password):
    data = _openssl(["-salt"], _bundle(db), password)
    rel = _release(repo, token, create=True)
    for a in rel.get("assets", []):
        if a["name"] == ENC_ASSET:
            _gh("DELETE", f"https://api.github.com/repos/{repo}/releases/assets/{a['id']}", token)
    _gh("POST", f"https://uploads.github.com/repos/{repo}/releases/{rel['id']}/assets?name={ENC_ASSET}",
        token, data, ctype="application/octet-stream")
    return f"encrypted backup saved ({len(data)/1e6:.1f} MB)"


def backup(db):
    """Daily backup to the repo's Releases page: plain (private repos) or encrypted with BACKUP_PASSWORD (any repo)."""
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not (repo and token and C.BACKUP_TO_RELEASES):
        return "skipped (not running on GitHub)"
    password = os.environ.get("BACKUP_PASSWORD")
    if password:
        return backup_encrypted(db, repo, token, password)
    private = repo_is_private(repo, token)
    if not private:
        return "skipped — repo is public; add a BACKUP_PASSWORD secret for encrypted backups (see SETUP.md)"
    db.commit()
    tmp = DB_PATH + ".bak"
    src = sqlite3.connect(tmp)
    db.backup(src)
    src.close()
    with open(tmp, "rb") as f:
        data = gzip.compress(f.read(), 6)
    os.remove(tmp)
    rel = _release(repo, token, create=True)
    for a in rel.get("assets", []):
        if a["name"] == "trendbot.db.gz":
            _gh("DELETE", f"https://api.github.com/repos/{repo}/releases/assets/{a['id']}", token)
    _gh("POST", f"https://uploads.github.com/repos/{repo}/releases/{rel['id']}/assets?name=trendbot.db.gz",
        token, data, ctype="application/gzip")
    return f"backed up ({len(data)/1e6:.1f} MB)"


def _download(repo, token, asset):
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/assets/{asset['id']}", headers={
        "Authorization": f"Bearer {token}", "Accept": "application/octet-stream", "User-Agent": "roblox-trend-bot"})
    try:
        return opener.open(req, timeout=120).read()
    except urllib.error.HTTPError as e:
        if e.code not in (301, 302, 307):
            raise
        return urllib.request.urlopen(urllib.request.Request(
            e.headers["Location"], headers={"User-Agent": "roblox-trend-bot"}), timeout=120).read()


def _restore_encrypted(repo, token, asset, password):
    import io
    import tarfile
    data = _openssl(["-d"], _download(repo, token, asset), password)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    restored = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            if m.name == "trendbot.db" and not os.path.exists(DB_PATH):
                with open(DB_PATH, "wb") as f:
                    f.write(tar.extractfile(m).read())
                restored.append("database")
            sp = os.environ.get("STATE_PATH")
            if m.name == "state.json" and sp and not os.path.exists(sp):
                os.makedirs(os.path.dirname(sp), exist_ok=True)
                with open(sp, "wb") as f:
                    f.write(tar.extractfile(m).read())
                restored.append("state")
    return f"restored {' + '.join(restored) or 'nothing'} from the encrypted backup ({len(data)/1e6:.1f} MB)"


def restore_if_missing():
    """If the cache lost the database, pull the last backup from Releases."""
    if os.path.exists(DB_PATH):
        return None
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not (repo and token):
        return None
    try:
        rel = _release(repo, token)
        password = os.environ.get("BACKUP_PASSWORD")
        enc = next((a for a in rel.get("assets", []) if a["name"] == ENC_ASSET), None)
        if password and enc:
            return _restore_encrypted(repo, token, enc, password)
        asset = next((a for a in rel.get("assets", []) if a["name"] == "trendbot.db.gz"), None)
        if not asset:
            return None
        opener = urllib.request.build_opener(_NoRedirect)
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/assets/{asset['id']}", headers={
            "Authorization": f"Bearer {token}", "Accept": "application/octet-stream", "User-Agent": "roblox-trend-bot"})
        try:
            data = opener.open(req, timeout=120).read()
        except urllib.error.HTTPError as e:
            if e.code not in (301, 302, 307):
                raise
            data = urllib.request.urlopen(urllib.request.Request(
                e.headers["Location"], headers={"User-Agent": "roblox-trend-bot"}), timeout=120).read()
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, "wb") as f:
            f.write(gzip.decompress(data))
        return f"restored database from backup ({len(data)/1e6:.1f} MB)"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        print(f"restore failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"restore failed: {e}", file=sys.stderr)
    return None
