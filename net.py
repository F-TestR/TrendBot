"""
A shared stopwatch and circuit breaker for the optional data sources.

The job is killed after 15 minutes, and a killed run posts nothing and saves nothing. Each run makes a few hundred
calls to Roblox, YouTube and others; if one of those services is slow, every call can wait out its full timeout and
the minutes add up. Two guards stop that:

  - a host that fails or times out BREAKER_FAILS times in a row is left alone for the rest of the run
  - once the run has used RUN_SOFT_LIMIT_SEC, optional calls are skipped so the digest still goes out

Skipped calls raise Skipped, which every caller already treats like any other failed fetch.
"""
import time
import urllib.error
import urllib.parse
from contextlib import contextmanager

import config as C

_t0 = time.monotonic()
_fails = {}
_told = set()
_scale = 1.0


class Skipped(Exception):
    pass


def begin(scale=1.0):
    """Start the stopwatch (called once at the start of a run). `scale` is how many planned 20-minute runs this
    one stands in for (see quota)."""
    global _t0, _scale
    _t0 = time.monotonic()
    _scale = max(1.0, min(float(scale), C.RUN_SCALE_MAX))
    _fails.clear()
    _told.clear()


def quota(per_run):
    """A per-run allowance, scaled to how long it has been since the last run.

    The allowances in config.py ("10 games per run") were sized for a run every 20 minutes, 72 a day. GitHub's
    free scheduler actually delivers one every 40-70 minutes, about 30 a day, so every rotating job was getting
    well under half its planned daily coverage. A run that follows a 60-minute gap now does three runs' worth."""
    return max(1, int(round(per_run * _scale)))


def used():
    return time.monotonic() - _t0


def out_of_time():
    return used() > C.RUN_SOFT_LIMIT_SEC


def _host(url):
    return urllib.parse.urlsplit(url).netloc or url[:40]


def tripped():
    """Hosts skipped in this run, for the run's summary line."""
    return sorted(h for h, n in _fails.items() if n >= C.BREAKER_FAILS)


def guard(url):
    if out_of_time():
        if "time" not in _told:
            _told.add("time")
            print(f"run has used {used():.0f}s: skipping the remaining optional lookups so the digest still goes out")
        raise Skipped("run is out of time")
    h = _host(url)
    if _fails.get(h, 0) >= C.BREAKER_FAILS:
        if h not in _told:
            _told.add(h)
            print(f"{h} failed {C.BREAKER_FAILS} times in a row: skipping it for the rest of this run")
        raise Skipped(f"{h} is not answering")


@contextmanager
def call(url):
    """Wrap one network call: `with NET.call(url): data = urlopen(...)`."""
    guard(url)
    h = _host(url)
    try:
        yield
    except urllib.error.HTTPError as e:
        # an answer of "no" (404, 403, 400) means the host is fine; overload answers count as failures
        _fails[h] = _fails.get(h, 0) + 1 if (e.code >= 500 or e.code == 429) else 0
        raise
    except Exception:
        _fails[h] = _fails.get(h, 0) + 1      # timeouts, dropped connections, bad JSON
        raise
    else:
        _fails[h] = 0


# ---- retry bookkeeping for once-a-day jobs --------------------------------------------------------------------
# A daily job that fails used to be marked done for the day, so one bad moment lost the whole day. Instead each
# failure is remembered as {name: [time, failures today]} and the job is tried again RETRY_MIN later, up to MAX_RETRIES.

def may_try(fails, name, t):
    f = fails.get(name)
    if not f or f[0][:10] != t.strftime("%Y-%m-%d"):
        return True
    from datetime import datetime, timedelta
    return f[1] < C.DAILY_JOB_MAX_RETRIES and (t - datetime.fromisoformat(f[0])) >= timedelta(minutes=C.DAILY_JOB_RETRY_MIN)


def failed(fails, name, t):
    f = fails.get(name)
    n = f[1] if f and f[0][:10] == t.strftime("%Y-%m-%d") else 0
    fails[name] = [t.isoformat(), n + 1]


def worked(fails, name):
    fails.pop(name, None)
