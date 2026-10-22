"""Settings for the Roblox trend bot. Change numbers here, not in bot.py."""

# ---- API budget (RoWatcher free tier = 1,000 requests/day) ----
DAILY_REQUEST_CAP = 950          # hard stop, leaves headroom under 1,000
TOP_PAGES = 10                   # 10 pages x 100 = top 1,000 games by live players
PAGE_SIZE = 100
MAX_DETAIL_LOOKUPS_PER_RUN = 5   # extra calls for new candidates (created date etc.)

# ---- What counts as interesting ----
MIN_PLAYERS_NEW_ENTRY = 2000     # a brand-new game entering the top 1,000 with at least this many players
YOUNG_GAME_DAYS = 60             # only alert on games created within this many days (when known)
SURGE_MULTIPLIER = 3.0           # weekday high >= 3x last week's weekday highs
SURGE_MIN_PLAYERS = 3000         # ...and at least this many players
WATCH_DROP_PCT = 25              # watchlist game's weekday high down >= 25% vs a week ago
COPY_WAVE_MIN_GAMES = 3          # 3+ new games sharing a title keyword within 7 days
ALERT_COOLDOWN_DAYS = 3          # don't repeat the same alert for a game within this many days

# ---- Daily digest ----
DIGEST_HOUR_UTC = 7              # 07:00 UTC = 08:00 UK summer time / 07:00 UK winter time

# ---- Games you're watching (universe IDs) ----
WATCHLIST = {
    "10767380385": "Sell Fries! [Anomaly]",
    "10769543567": "Cat Battles",
    "10769188452": "Eat Everything In A Grocery Store",
    "10770018231": "Clone Baby Care (Anomaly)",
    "10769484703": "What If Disasters",
    "10769516701": "Facecard: Makeup Showdown",
    "10767138232": "Kukirin Life",
    "10155360168": "Illegal Soccer",
}

# Words ignored when spotting copy waves in titles
STOPWORDS = set("""
a an the and or for to of in on at with your you my is it be by from vs
new upd update updated beta alpha testing release event free x2 x5 x10 2x 5x 10x
w1 w2 w3 w4 world worlds part chapter ch season halloween hlwn spooky
game games simulator sim tycoon roblox obby
""".split())

KEEP_DAYS = 21                   # how many days of daily highs to keep per game
API_BASE = "https://rowatcher.com/api/v1"
