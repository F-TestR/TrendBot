"""Settings for the Roblox trend bot. Change numbers here, not in bot.py."""

# ---- API budget (RoWatcher free tier = 1,000 requests/day) ----
DAILY_REQUEST_CAP = 950          # hard stop, leaves headroom under 1,000
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
YT_DAILY_UNIT_CAP = 9000         # of the free 10,000 (long videos + Shorts + trending + lookups)
YT_QUERIES = [                   # long videos: 3 searches x 12 runs/day x 100 units = 3,600 units/day
    "roblox",
    "new roblox game",
    "roblox simulator",
]
# YouTube Shorts (2 searches x 12 runs/day x 100 units = 2,400 units/day). TikTok and Instagram Reels
# have no free public API, so Shorts is the short-video signal.
YT_SHORTS_QUERIES = ["roblox"]
YT_SHORTS_ORDERS = ["viewCount", "date"]   # most-watched new Shorts, and the newest (catches things early)
YT_SHORT_MAX_SECONDS = 180       # videos this short count as Shorts
YT_SHORTS_INTL = [               # Shorts in other languages (every 4 hours: 3 x 6 x 100 = 1,800 units/day)
    ("roblox", "pt", "BR"),
    ("roblox", "es", "MX"),
    ("roblox", "id", "ID"),
]
YT_SHORTS_INTL_EVERY_MIN = 240
YT_SHORTS_SIGNAL_VPH = 20_000    # a game counts as "hot on Shorts" at 20K+ views/hour across its Shorts...
YT_SHORTS_SIGNAL_N = 3           # ...or 3+ Shorts about it in 48h
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
 crazy insane funny hours played playing best worst ever this that every
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
DEEP_LAST_PAGE = 20              # pages 4-20 in rotation (RoWatcher serves only the first 2,000 results since Oct 2026;
                                 # the bot also detects the cap by itself and re-checks daily)
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
LEARN_ENTRY_CCU = 600            # a game is "noticed" the first day it reaches this many players (inside the top 2,000)
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

# =====================================================================
# Engagement: session length, stickiness score, backtest, features, opportunity map
# =====================================================================
SESSION_MIN_MIN = 0.5            # estimated sessions outside this range (minutes) are treated as noise
SESSION_MAX_MIN = 240
ENGAGE_MIN_AVG_CCU = 300         # games averaging fewer players in a week aren't scored
BACKTEST_MIN_PAIRS = 40          # game-weeks needed before the survival backtest is reported
FEATURE_MIN_GAMES = 8            # a description feature needs this many games to be compared
MAP_GROWTH_PCT = 10              # "growing" on the opportunity map = players up 10%+ vs 3 weeks ago

# Features looked for in game descriptions (any of the phrases counts). Add your own.
DESCRIPTION_FEATURES = {
    "daily rewards / streaks": ["daily reward", "daily rewards", "daily login", "login reward", "login rewards", "streak", "streaks", "daily spin", "daily chest"],
    "weekly update schedule": ["every saturday", "every friday", "every week", "weekly update", "weekly updates", "updates every", "new update every"],
    "codes": ["code", "codes"],
    "group rewards": ["join the group", "join our group", "group rewards", "group reward", "group members"],
    "friend bonus": ["friend boost", "friends boost", "per friend", "for every friend", "invite friends", "play with friends"],
    "trading": ["trade", "trading", "trades"],
    "pets / collecting": ["pet", "pets", "collect", "collection", "index"],
    "rebirth / prestige": ["rebirth", "rebirths", "prestige"],
    "limited events": ["event", "events", "limited time", "limited-time", "admin abuse"],
    "quests / missions": ["quest", "quests", "mission", "missions", "challenges"],
    "leaderboards": ["leaderboard", "leaderboards", "global leaderboard"],
    "offline / idle earnings": ["offline", "idle", "afk"],
    "co-op / teams": ["co-op", "coop", "team up", "squad", "party"],
    "PvP": ["pvp", "1v1", "duel", "duels"],
    "base building / decorating": ["decorate", "build your", "customize your", "customise your", "base"],
    "roleplay": ["roleplay", "rp"],
}

# =====================================================================
# Forward calendar: things known to be coming
# =====================================================================
FUTURE_HORIZON_DAYS = 42         # look this far ahead (plus things released in the last 14 days)
FUTURE_DIGEST_ITEMS = 8          # how many upcoming things the daily digest lists
FUTURE_ALERT_NEW_GAMES = 2       # 🔮 alert when an upcoming thing appears in this many brand-new Roblox games
TMDB_REGION = "US"               # film release dates for this country (GB for the UK)
TMDB_MIN_POPULARITY = 40         # skip obscure upcoming films

# Dates you know about: (date, name, words to look for in Roblox titles).
# Add Roblox events, big game launches, film dates, school holidays - anything you hear about.
FUTURE_EVENTS = [
    ("2026-10-31", "Halloween", ["halloween", "spooky", "pumpkin", "ghost", "haunted"]),
    ("2026-11-26", "Thanksgiving (US)", ["thanksgiving", "turkey", "feast"]),
    ("2026-11-27", "Black Friday", ["black friday", "shopping", "sale"]),
    ("2026-12-25", "Christmas", ["christmas", "santa", "elf", "snow", "gift", "present", "sleigh"]),
    ("2026-12-31", "New Year's Eve", ["new year", "fireworks", "countdown"]),
    ("2027-02-14", "Valentine's Day", ["valentine", "valentines", "love", "heart"]),
    ("2027-03-28", "Easter", ["easter", "bunny", "egg hunt"]),
]

# =====================================================================
# Badges: players per day, playtime per player, returning share, funnels (free, no key)
# =====================================================================
BADGE_GAMES_PER_DAY = 400        # games whose badges are read each day (watchlist and young games first)
BADGE_GAMES_PER_RUN = 10         # per 20-minute run (72 runs a day)
BADGE_MIN_PLAYERS = 500          # only read badges for games with at least this many players
BADGE_MAX_PAGES = 3              # up to 300 badges per game
BADGE_PAUSE_SECONDS = 0.6        # pause between games, to be polite to Roblox
BADGE_MIN_WIN_RATE = 0.01        # badges earned by fewer than 1% of daily players are too imprecise for the player count
BADGE_KEEP_DAYS = 21             # raw badge stats kept this long
BADGE_PLAYTIME_REFERENCE = 25    # minutes/day used as "typical" until enough games are measured

# =====================================================================
# Algorithm mirror: learns what Roblox's recommendation algorithm rewards right now
# =====================================================================
PROMO_MIN_PLAYERS = 200          # game-days with fewer average players are ignored
PROMO_GROWTH_RATIO = 1.5         # "growth" outcome = next 7 days' average players >= 1.5x the last 7 days'
PROMO_HISTORY_WEEKS = 5          # train on the last 5 weeks (recent enough to notice algorithm changes)
PROMO_DAY_STEP = 1               # use every day
PROMO_GAMES_PER_DAY = 250        # sample this many games per training day
PROMO_MIN_EXAMPLES = 300
PROMO_MIN_POSITIVES = 25
PROMO_ITERS = 300
PROMO_L2 = 0.02
PROMO_KEEP_HISTORY = 60          # days of learned weights kept, for the change watch
PROMO_SHIFT_DAYS = 21            # compare this week's weights with ~3 weeks ago
PROMO_SHIFT_MIN = 0.25           # a weight moving this much (in standard steps) counts as a change

# =====================================================================
# Presentation (Discord cards)
# =====================================================================
DIGEST_STYLE = "cards"           # "cards" = short Discord cards (recommended) · "text" = the old long text digest
BOARD_ROWS = 8                   # games on the daily "Games to watch" card
BOARD_MIN_PLAYERS = 300          # young games below this are left off the board
BOARD_PLAYTIME_HEADLINE = 30     # minutes/player/day needed for the playtime headline

# A model's % is only shown (and only triggers alerts) once it scores at least this on data it never saw (0.5 = coin flip)
MODEL_TRUST_AUC = 0.6

# =====================================================================
# Roblox direct (free, no key): Roblox's own home-page sorts, Roblox search, and live numbers
# for games below RoWatcher's 2,000-game cap
# =====================================================================
RBX_SORTS_EVERY_MIN = 60         # read Roblox's home-page sorts this often
RBX_DEVICES = ["computer", "phone"]   # sorts differ a little by device
RBX_SKIP_SORTS = {"filters_v5", "top-paid-access", "music-top-100", "trending-music-experiences",
                  "more-when-you-subscribe", "learning-and-explore"}
RBX_CHART_SORTS = {"top-trending", "up-and-coming", "fun-with-friends", "top-revisited"}  # count as "Roblox is pushing it"
# Countries whose Top Trending / Up-and-Coming lists are read (phone, first page = 1 request each).
# Trends often start in Brazil, the Philippines, Indonesia or Mexico days before the US.
RBX_COUNTRIES = ["us", "br", "ph", "id", "mx", "gb", "de", "fr", "es", "th", "vn", "tr", "pl", "ca", "au"]
RBX_HOME_COUNTRIES = {"us", "gb", "ca", "au"}   # "abroad first" = charting outside these but not worldwide
RBX_COUNTRY_EVERY_MIN = 60
ABROAD_ALERT_COUNTRIES = 2       # 🌍 alert when a young game charts in 2+ countries but not worldwide
RBX_SEARCH_WORDS = ["simulator", "tycoon", "obby", "steal", "anomaly", "clean", "wash", "pirate", "disaster", "brainrot"]
RBX_SEARCH_WORDS_PER_RUN = 2     # words searched per run (each once a day) - finds tiny new copies
RBX_SEARCH_PAGES = 3             # result pages per word (~30-60 games)
RBX_MIN_PLAYERS = 20             # ignore discovered games smaller than this
RBX_TRACK_DAYS = 14              # keep following a discovered or young game this many days after last seen
RBX_TRACK_MAX = 1500             # most games tracked directly per run (50 per request)

# =====================================================================
# Forecasting: S-curve peak forecasts, breakout-start detection, lifespans
# =====================================================================
FC_HISTORY_DAYS = 90             # history used
FC_WINDOW_DAYS = 21              # a game's last 21 days are used for its curve
FC_MIN_DAYS = 4                  # a game needs this many days of data before its peak is forecast
FC_MIN_PLAYERS = 300             # ...and at least this many average players
FC_BACKTEST_DAYS = 5             # back-test: forecast made from the first 5 days of a rise
FC_BACKTEST_MIN = 10             # games needed before the back-test is reported
CP_WINDOW_DAYS = 30              # days of growth history the change-point detector looks at
CP_EXPECTED_RUN = 20             # prior: growth regimes last ~20 days on average
CP_RECENT = 3                    # "just started" = within the last 3 days
CP_MIN_PROB = 0.5                # fire when that is at least 50% likely...
CP_MIN_GROWTH = 0.12             # ...the new regime grows 12%+ a day...
CP_MIN_JUMP = 0.10               # ...and is 10+ points/day faster than before
CP_MIN_PLAYERS = 200             # ignore tiny games
CP_BACKTEST_GAMES = 400          # games sampled for the back-test
SURV_MIN_PEAK = 1000             # lifespans are measured for games that peaked above this
SURV_MIN_GROUP = 8               # groups smaller than this aren't reported

# =====================================================================
# Trend Score: one calibrated 0-100 score combining every early signal
# =====================================================================
TS_MIN_TARGET = 1000             # "took off" = average players at least double within 14 days AND reach this
TS_MIN_PLAYERS = 150             # young games below this aren't scored
TS_MIN_EXAMPLES = 400            # outcomes needed before the learned model replaces the starting formula...
TS_MIN_POSITIVES = 30            # ...including this many games that took off
TS_KEEP_DAYS = 90                # daily snapshots kept for learning
TS_ALERT = 60                    # 🚀 alert when a young game's Trend Score reaches this
TS_PING = 80                     # ...and ping you at this
MERGE_ALERTS = True              # several alerts about one game in the same run become one card

# =====================================================================
# Money (earnings by game, genre, mechanic, size) and published reports
# =====================================================================
MONEY_DAYS = 7                   # revenue averaged over the last 7 complete days
MONEY_MIN_DAYS = 3               # a game needs revenue readings on at least 3 of them
MONEY_MIN_CCU = 400              # only games averaging 400+ concurrent players
MONEY_MIN_GROUP = 6              # groups smaller than this aren't shown
PUBLISH_REPORTS = True           # write digest/weekly/money reports to the repo's "reports" branch
REPORTS_BRANCH = "reports"
HOUR_PROFILE_ALPHA = 0.1         # how fast the time-of-day profile adapts (daily averages are corrected by it)

# =====================================================================
# Roblox platform events, studios, game passes, icons, alert budget, live dashboard
# =====================================================================
RBX_EVENTS = ["the hollow", "the hunt", "the games", "the hatch", "the classic", "egg hunt"]  # known event names
EVENT_MIN_GAMES = 8              # a new title tag in this many games at once counts as an event
EVENT_NEW_DAYS = 10              # ...if it first appeared within this many days
STUDIO_ALERT_PEAK = 10000        # 🏆 alert when a studio whose other game peaked this high launches something new
STUDIO_ALERT_MIN_PLAYERS = 100   # ...and the new game already has this many players
PASSES_GAMES_PER_RUN = 8         # game-pass lists read per run (top earners first, each about once a week)
PASSES_REFRESH_DAYS = 7
ICON_TRACK_MAX = 300             # games whose icon is checked for changes each day (young + board + watchlist)
ICON_COPY_DISTANCE = 6           # icons this similar (perceptual hash bits) count as a copy
ALERT_DAILY_BUDGET = 12          # most alert cards per day (pings and watchlist always go through); the rest go in the digest
PAGES_DASHBOARD = True           # publish the dashboard as a live web page (GitHub Pages, from the reports branch)
