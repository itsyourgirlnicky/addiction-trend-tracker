import praw
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

SUBREDDITS = [
    "addiction", "alcoholism", "gambling", "problemgambling",
    "opiates", "recoveryoptions", "stopdrinking", "drugs",
    "leaves", "quittingkratom", "antidrug", "SoberLife",
    "Fentanyl", "heroin", "cocaine", "meth"
]

KEYWORDS = [
    "addiction", "addict", "recovery", "rehab", "overdose",
    "withdrawal", "relapse", "sober", "clean", "substance",
    "gambling", "betting", "casino", "alcohol", "drug epidemic",
    "opioid", "fentanyl", "cocaine", "meth", "heroin",
    "drug crisis", "addiction pandemic", "problem gambling"
]


def collect_posts(limit=100):
    posts = []

    for subreddit_name in SUBREDDITS:
        print(f"Collecting from r/{subreddit_name}...")
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for post in subreddit.hot(limit=limit):
                text = f"{post.title} {post.selftext}".lower()
                matched_keywords = [kw for kw in KEYWORDS if kw in text]
                if not matched_keywords:
                    continue

                posts.append({
                    "id":               post.id,
                    "source":           "reddit",
                    "subreddit":        subreddit_name,
                    "title":            post.title,
                    "text":             post.selftext,
                    "created_at":       datetime.utcfromtimestamp(
                                            post.created_utc
                                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    "score":            post.score,
                    "num_comments":     post.num_comments,
                    "author":           str(post.author),
                    "url":              post.url,
                    "matched_keywords": matched_keywords,
                    "author_location":  None
                })

        except Exception as e:
            print(f"Error on r/{subreddit_name}: {e}")
            continue

    os.makedirs("data/raw", exist_ok=True)
    filename = f"data/raw/reddit_{datetime.now().strftime('%Y%m%d_%H%M')}.jsonl"
    with open(filename, "w") as f:
        for post in posts:
            f.write(json.dumps(post) + "\n")

    print(f"\nDone — saved {len(posts)} posts to {filename}")
    return posts


if __name__ == "__main__":
    collect_posts(limit=100)