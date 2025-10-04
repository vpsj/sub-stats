#!/usr/bin/env python3
import os, json, time
from pathlib import Path

try:
    import praw
except Exception:
    raise SystemExit("praw not installed. The GitHub Action will install it.")

# Read credentials from env
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "SubStats/0.1 by u/rail_subscriber")

if not CLIENT_ID or not CLIENT_SECRET:
    raise SystemExit("Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET environment variable.")

# Create PRAW Reddit instance (read-only)
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

SUB = "indianrailways"
data_path = Path("data.json")

def write_data(count):
    now_ms = int(time.time() * 1000)
    if data_path.exists():
        data = json.loads(data_path.read_text())
    else:
        data = {"logs": []}

    # Append only if different from last logged count (avoids duplicates)
    last = data["logs"][-1]["count"] if data["logs"] else None
    if last is None or last != count:
        data["logs"].append({"time": now_ms, "count": int(count)})

    # Keep last 10000 entries
    data["logs"] = sorted(data["logs"], key=lambda x: x["time"])[-10000:]
    data_path.write_text(json.dumps(data, indent=2))
    print(f"Wrote data.json entry: time={now_ms}, count={count}")

def main():
    try:
        sub = reddit.subreddit(SUB)
        count = sub.subscribers
        if not isinstance(count, int) or count <= 0:
            raise ValueError(f"Invalid subscriber count: {count}")
        print(f"Fetched subscriber count: {count}")
        write_data(count)
    except Exception as e:
        print("Error fetching subscriber count:", e)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
