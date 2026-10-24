"""Settings for the Roblox trend bot. Change numbers here, not in bot.py."""

# ---- API budget (RoWatcher free tier = 1,000 requests/day) ----
DAILY_REQUEST_CAP = 950          # hard stop, leaves headroom under 1,000
TOP_PAGES = 10                   # (legacy) see CORE_PAGES / DEEP_LAST_PAGE further down
PAGE_SIZE = 100
MAX_DETAIL_LOOKUPS_PER_RUN = 5   # extra calls for new candidates (created date etc.)

# ---- What counts as interesting ----
MIN_PLAYERS_NEW_ENTRY = 2000     # alert when a young game first crosses this many players
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

# =====================================================================
# Extra sources (stage 1): YouTube, Roblox public data, Discord servers
# =====================================================================

# ---- How often each source is checked (minutes) ----
YT_EVERY_MIN = 120               # YouTube: every 2 hours (keeps well inside the free quota)
ROBLOX_EVERY_MIN = 60            # Roblox likes/favourites/updates: hourly

# ---- YouTube (free quota = 10,000 units/day; a search costs 100) ----
YT_DAILY_UNIT_CAP = 8000
YT_QUERIES = [                   # 4 searches x 12 runs/day x 100 units = 4,800 units/day
    "roblox",
    "new roblox game",
    "roblox tycoon",
    "roblox simulator",
]
YT_MAX_PLACE_LOOKUPS_PER_RUN = 25   # game links in video descriptions -> which game
YT_MIN_NAME_CHARS = 8            # game names shorter than this aren't matched in titles (too generic)
YT_SIGNAL_MIN_VIDEOS = 2         # a game counts as "hot on YouTube" with 2+ videos in 48h...
YT_SIGNAL_MIN_VIEWS = 100_000    # ...or 100K+ views in 48h
YT_RISING_MIN_VIDEOS = 4         # a title word needs 4+ videos in 48h to count as rising
YT_GENERIC_NAMES = set("""
roblox|the game|obby game|tycoon game|simulator|hide and seek|tower defense|the floor is lava|
murder mystery|untitled game|escape the|natural disasters|survive the|find the
""".replace("\n", "").split("|"))
YT_TITLE_STOPWORDS = set("""
the and for you your this that with from but not are was were have has had got get gets getting
how why what when who which into out over all every any one two three new best most more very
just can cant dont did does its it's i'm me my our we they them his her their roblox robloxs
video videos game games play played playing playthrough gameplay part funny insane secret
became become becoming made make making tried trying try first last ever day days hour hours
vs win won lose lost each only never again here there then than like even still really
shorts short youtube viral trending update new free gets got
""".split())
NAME_EDGE_WORDS = set("new upd update updated event beta alpha release x2 x5 x10 2x 5x 10x".split())

# ---- Roblox public data ----
ROBLOX_MAX_GAMES = 300           # watchlist + young games + YouTube-linked games
ENRICH_MIN_PLAYERS = 1000        # only enrich young games with at least this many players

# ---- Community (Roblox groups automatic, Discord optional) ----
COMMUNITY_EVERY_MIN = 360        # every 6 hours
COMMUNITY_MAX_GAMES = 120        # games whose group members are tracked
GROUP_LOOKUPS_PER_RUN = 80
COMMUNITY_SIGNAL_PCT = 3         # +3% members in ~2 days counts as growing

# Roblox hides games' Discord links from bots, so list the servers you want tracked:
#   "universe id": "invite code or full discord.gg link"
# Find a game's invite on its Roblox page (Social links) or in its YouTube descriptions.
DISCORD_INVITES = {
    # "10767380385": "https://discord.gg/example",
}
DISCORD_MAX_GAMES = 40

# ---- Heat score alerts ----
HEAT_ALERT_SCORE = 55            # 🔥 alert when heat >= this AND 2+ sources agree
EARLY_WARNING_VIDEOS = 3         # 👀 alert: 3+ YouTube videos in 48h...
EARLY_WARNING_VIEWS = 300_000    # ...or 300K+ views, while the game is still small
EARLY_WARNING_MAX_PLAYERS = 5000

# =====================================================================
# Twitch (optional, free): which Roblox games streamers are playing
# =====================================================================
TWITCH_EVERY_MIN = 60
TWITCH_PAGES = 5                 # 5 x 100 = top 500 live Roblox streams per check
TWITCH_SIGNAL_VIEWERS = 300      # a game counts as "rising on Twitch" with 300+ viewers...
TWITCH_SIGNAL_GROWTH = 1.5       # ...and 1.5x its viewers from ~2 days before

# =====================================================================
# Insights: mechanics, updates, lifecycle, weekly report
# =====================================================================
WEEKLY_REPORT_WEEKDAY = 6        # 0 = Monday ... 6 = Sunday (posted with that morning's digest)
HIT_PLAYERS = 5000               # a new game "hits" if it reaches this many players
GAP_MAX_NEW_GAMES = 2            # "open gap" = demand up 10%+ with at most this many new games that week
BREAKOUT_PLAYERS = 10000         # a young game crossing this is logged as a breakout
UPDATE_MIN_PLAYERS = 2000        # only measure updates on games with at least this many players
INSIGHT_KEEP_DAYS = 180          # breakouts and update results are kept this long
MAX_UPDATE_EVENTS = 400

# Mechanic groups: a game belongs to a group if its title contains one of the words
# (plurals count too). Add your own groups or words freely.
MECHANICS = {
    "Tycoon / sell stuff": ["tycoon", "sell", "shop", "factory", "store", "restaurant", "bakery", "cafe"],
    "Anomaly / night shift": ["anomaly", "anomalies", "night shift", "nights", "inspect", "inspection"],
    "Horror": ["horror", "scary", "backrooms", "monster", "nightmare"],
    "Find / search": ["find", "search", "needle", "hidden", "hunt"],
    "Eat / grow big": ["eat", "eating", "grow", "fat", "bigger", "giant"],
    "Battles / army": ["battle", "battles", "army", "war", "fight", "fighting", "arena"],
    "Care / baby / pets": ["baby", "babies", "care", "daycare", "pet", "pets", "adopt"],
    "Disasters / survival": ["disaster", "disasters", "survive", "survival", "tsunami", "flood"],
    "Obby / parkour": ["obby", "parkour", "climb", "jump"],
    "Steal / brainrot": ["brainrot", "steal", "stealing"],
    "Sports": ["soccer", "football", "basketball", "volleyball", "tennis", "golf", "hockey", "baseball"],
    "Fashion / makeup": ["makeup", "dress", "fashion", "facecard", "beauty", "salon"],
    "Vehicles / riding": ["car", "cars", "scooter", "bike", "drive", "driving", "race", "racing", "ride", "truck"],
    "Fishing / farming": ["fish", "fishing", "farm", "farming", "garden", "plant", "harvest"],
    "RNG / gacha / luck": ["rng", "roll", "gacha", "luck", "lucky", "spin", "crate", "egg", "hatch"],
    "Tower defense": ["defense", "defence"],
    "Jobs / work sim": ["job", "work", "worker", "delivery", "clean", "cleaning", "cashier", "paramedic", "firefighter", "police"],
    "Roleplay / life": ["rp", "roleplay", "life", "town", "city", "school", "house"],
    "Anime / fighting style": ["anime", "slayer", "piece", "hero", "jujutsu", "blox"],
    "Merge / clicker": ["merge", "clicker", "click", "tap", "idle", "incremental"],
}

# =====================================================================
# Discord look and pings
# =====================================================================
RICH_CARDS = True                # alerts as cards with the game's icon (False = plain text)
PING_USER_ID = ""                # your Discord user ID to get @mentioned on big signals (see SETUP.md)
PING_HEAT_SCORE = 80             # ping when heat >= this on 3+ platforms...
PING_SURGE_MULTIPLIER = 5.0      # ...or a 5x+ surge
PING_EARLY_VIEWS = 1_000_000     # ...or 1M+ YouTube views on a small game
PING_COPY_WAVE_GAMES = 5         # ...or a copy wave of 5+ games
DIGEST_CHARTS = True             # attach player-curve charts to the digest
DASHBOARD = True                 # attach a dashboard.html file to the daily digest

# =====================================================================
# Deeper scanning + database + learning
# =====================================================================
# RoWatcher budget is paced across the day (DAILY_REQUEST_CAP above). Roughly per day:
#   core pages 216 · deep rotation 360 · charts 24 · discovery 30 · backfill ~140  =  ~770
CORE_PAGES = 3                   # pages 1-3 (top 300) every run
DEEP_LAST_PAGE = 30              # pages 4-30 (down to ~350 players) in rotation...
DEEP_PAGES_PER_RUN = 5           # ...5 per run, so each is refreshed about every 1.8 hours
DISCOVERY_FIRST_PAGE = 31        # once a day, pages 31-60 (~350 down to ~150 players)
DISCOVERY_LAST_PAGE = 60         # to find tiny young games for the model
CHARTS_EVERY_MIN = 60            # Roblox's algorithm charts (via RoWatcher)
BACKFILL_PER_RUN = 2             # past-history downloads per run (for the model)
BACKFILL_MAX_AGE_DAYS = 75       # only backfill games created within this many days
COPY_WAVE_MIN_PLAYERS = 500      # copies smaller than this don't count towards a copy wave

# ---- Database ----
HOURLY_MAX_AGE_DAYS = 62         # hourly player curves kept for games younger than this (the model needs ~60)
HOURLY_KEEP_DAYS = 120
DAILY_KEEP_DAYS = 400
BACKUP_TO_RELEASES = True        # daily backup to the repo's Releases page (private repos only)
BACKUP_TAG = "trendbot-db"

# ---- Learning ----
EXPLODE_CCU = 25000              # "exploded" = reached this many players...
LABEL_DAYS = 21                  # ...within this many days of first being noticed
LEARN_ENTRY_CCU = 300            # a game is "noticed" the first day it reaches this many players
LEARN_MAX_AGE_DAYS = 60          # only learn from games noticed within 60 days of creation
LEARN_MIN_EXAMPLES = 60          # don't train until there are this many finished examples...
LEARN_MIN_POSITIVES = 8          # ...including this many explosions
LEARN_L2 = 0.01
PREDICT_ALERT_PROB = 0.5         # 🎯 alert when the model gives a game 50%+...
PREDICT_ALERT_MAX_PLAYERS = 8000 # ...while it still has fewer than this many players
PREDICT_MAX_DAYS_AFTER = 5       # only predict for games noticed in the last few days

# ---- YouTube channel size ----
YT_BIG_CHANNEL_SUBS = 1_000_000  # a video from a channel this big counts as a "big creator" video

# =====================================================================
# Themes (trend prediction) + outside-Roblox signals
# =====================================================================
THEME_MIN_GAME_CCU = 100         # games below this never count towards a theme
THEME_MIN_CCU = 300              # themes smaller than this (with no new games) are ignored
THEME_HIT_CCU = 2000             # a theme's game "hits" at this many players...
THEME_BREAKOUT_GAMES = 3         # ...and a theme "breaks out" when it goes from <=1 hit to this many
THEME_HISTORY_DAYS = 60          # how far back to rebuild theme history the first time
THEME_KEEP_DAYS = 150
THEME_MIN_EXAMPLES = 200         # theme-days needed before the theme model trains...
THEME_MIN_POSITIVES = 8          # ...including this many breakouts
THEME_ALERT_PROB = 0.4           # 🌱 alert when a small theme scores this or more
THEME_ALERT_MAX_HITS = 1         # ...and still has at most this many 2K+ games
RW_TRENDS_EVERY_DAYS = 7         # refresh RoWatcher's curated trend list weekly (1 request)

# Outside Roblox
STEAM_RANK_CLIMB = 10            # a Steam game counts as rising if it climbed this many places in a week (or is new to the top 100)
YT_TRENDING_REGIONS = ["US", "GB"]
UPSTREAM_KEEP_DAYS = 150
SEASONS = {                      # month -> words that tend to trend then (next month's are included early)
    1: ["winter", "snow", "new year"],
    2: ["valentine", "valentines", "love"],
    3: ["spring", "easter", "egg"],
    4: ["easter", "egg", "spring"],
    6: ["summer", "beach", "pool", "water"],
    7: ["summer", "beach", "pool", "water"],
    8: ["summer", "school", "back to school"],
    9: ["school", "autumn", "fall"],
    10: ["halloween", "spooky", "ghost", "zombie", "pumpkin", "haunted"],
    11: ["thanksgiving", "turkey", "winter", "christmas"],
    12: ["christmas", "santa", "elf", "snow", "winter", "gift"],
}

# Words that are never themes on their own
THEME_STOPWORDS = set("""
the and for you your with from new upd update updated event beta alpha testing release free
game games play roblox obby simulator sim tycoon x2 x5 x10 2x 5x 10x part chapter season
but not are was have has can get got all any one two three more most very just how why what
when who out over into off our its his her they them this that there then than like
official full edition version remastered remake ultimate deluxe online world worlds
""".split())
THEME_GENERIC = set("""
game games world life city time super best mega ultra simulator tycoon roblox legends legend
battle battles war wars fight hero heroes story adventure online season update official
""".split())

# =====================================================================
# Weekday hold (Tue-Wed players vs the weekend before, relative to Roblox overall)
# =====================================================================
HOLD_MIN_PLAYERS = 1000          # only judge games with at least this many weekend players
HOLD_SPIKE_RATIO = 1.8           # Saturday > 1.8x Sunday = an event spike: use Sunday as the weekend
HOLD_GROWING_RATIO = 1.5         # weekdays 1.5x+ last week's = still growing: not judged
HOLD_MIN_BENCHMARK_GAMES = 30    # need this many rated games in a week to set the "typical" hold
HOLD_HISTORY_WEEKS = 8           # weeks rebuilt from the database (history downloads go back ~8 weeks)

# ---- Long-term games ----
LONGTERM_REL = 1.0               # long-term = holds at least as well as the typical game...
LONGTERM_SHARE = 0.75            # ...in at least 75% of its rated weeks...
LONGTERM_MIN_WEEKS = 2           # ...with at least this many weeks rated...
LONGTERM_WINDOW_WEEKS = 6        # ...looking back this many weeks
LONGTERM_PROMISING_REL = 1.15    # one strong week at this level = "promising"
GENRE_MIN_GAMES = 5              # genres with fewer rated games are left out of the genre table
BACKFILL_ESTABLISHED_PER_RUN = 1 # past-history downloads per run for older games (for long-term ratings)
BACKFILL_ESTABLISHED_MIN_PLAYERS = 1500
PLATFORM_EVERY_HOURS = 6         # Roblox-wide player counts (RoWatcher, 1 request each)
