"""
Publish readable reports to the repo's `reports` branch (main stays clean).

Each daily digest writes:  reports/digest.md · reports/board.csv · reports/money.md · reports/money.csv
Each weekly report writes: reports/weekly.md
Open them on GitHub (switch the branch picker to "reports"), download the CSVs into a spreadsheet,
or hand them to Claude to answer questions from the bot's data.

Uses the workflow's built-in GITHUB_TOKEN (the workflow already has "contents: write").
"""
import base64
import json
import os
import re
import urllib.error
import urllib.request

import config as C

API = "https://api.github.com/repos/"


def _req(method, url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "roblox-trend-bot", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        txt = r.read().decode()
        return json.loads(txt) if txt else {}


def _ensure_branch(repo, token, branch):
    try:
        _req("GET", f"{API}{repo}/git/ref/heads/{branch}", token)
        return
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    info = _req("GET", f"{API}{repo}", token)
    base = _req("GET", f"{API}{repo}/git/ref/heads/{info['default_branch']}", token)
    _req("POST", f"{API}{repo}/git/refs", token, {"ref": f"refs/heads/{branch}", "sha": base["object"]["sha"]})


def publish(files, message):
    """files: {path: text}. Returns a short status string; never raises."""
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not (repo and token and C.PUBLISH_REPORTS):
        return "skipped (not on GitHub)"
    branch = C.REPORTS_BRANCH
    try:
        _ensure_branch(repo, token, branch)
        done = 0
        for path, text in files.items():
            url = f"{API}{repo}/contents/{path}"
            sha = None
            try:
                sha = _req("GET", f"{url}?ref={branch}", token).get("sha")
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
            body = {"message": message, "branch": branch,
                    "content": base64.b64encode(text.encode("utf-8")).decode()}
            if sha:
                body["sha"] = sha
            _req("PUT", url, token, body)
            done += 1
        return f"published {done} report file(s) to the '{branch}' branch"
    except Exception as e:
        return f"report publish failed: {e}"


def cards_md(title, cards, content=""):
    """Discord cards -> Markdown page."""
    out = [f"# {title}", ""]
    if content:
        out += [content, ""]
    for c in cards:
        if not c:
            continue
        out.append(f"## {c['title']}")
        out.append("")
        desc = c.get("description", "")
        desc = re.sub(r"^• ", "- ", desc, flags=re.M)
        out.append(desc)
        if c.get("footer"):
            out += ["", f"_{c['footer']['text']}_"]
        out.append("")
    return "\n".join(out)
