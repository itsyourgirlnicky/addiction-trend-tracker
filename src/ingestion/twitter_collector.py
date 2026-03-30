import tweepy
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

QUERY = """
(
  addiction OR addict OR addicted OR "in recovery" OR rehab OR
  "treatment center" OR "getting clean" OR "staying sober" OR
  "addiction crisis" OR "addiction epidemic" OR "addiction pandemic" OR

  "substance use" OR "substance abuse" OR "substance disorder" OR
  "drug epidemic" OR "drug crisis" OR "drug pandemic" OR
  "war on drugs" OR "drug policy" OR "drug prevention" OR
  opioid OR opiate OR heroin OR fentanyl OR cocaine OR meth OR
  methamphetamine OR crack OR "prescription drug abuse" OR
  "drug overdose" OR overdose OR withdrawal OR relapse OR
  "drug trafficking" OR "drug cartels" OR narcotics OR

  alcohol OR alcoholism OR "alcohol abuse" OR "alcohol crisis" OR
  "alcohol epidemic" OR "binge drinking" OR sobriety OR
  "alcohol use disorder" OR "drunk driving" OR

  gambling OR "problem gambling" OR "gambling addiction" OR
  "gambling epidemic" OR "gambling crisis" OR "sports betting" OR
  "online gambling" OR "betting addiction" OR "casino addiction" OR
  "gambling disorder" OR "gambling harm" OR "gambling helpline" OR
  "gambling recovery" OR "lost everything gambling"
)
lang:en
-is:retweet
-is:reply
"""


def collect_tweets(max_results=100):
    client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

    response = client.search_recent_tweets(
        query=QUERY,
        max_results=max_results,
        tweet_fields=["created_at", "text", "geo", "lang", "author_id", "public_metrics"],
        place_fields=["full_name", "country", "country_code", "place_type"],
        expansions=["geo.place_id", "author_id"],
        user_fields=["location"]
    )

    if not response.data:
        print("No tweets returned.")
        return []

    places = {p["id"]: p for p in (response.includes.get("places") or [])}
    users  = {u["id"]: u for u in (response.includes.get("users")  or [])}

    posts = []
    for tweet in response.data:
        place = places.get((tweet.geo or {}).get("place_id"))
        user  = users.get(tweet.author_id)

        posts.append({
            "id":              str(tweet.id),
            "text":            tweet.text,
            "created_at":      str(tweet.created_at),
            "lang":            tweet.lang,
            "place_name":      place["full_name"]    if place else None,
            "country":         place["country"]      if place else None,
            "country_code":    place["country_code"] if place else None,
            "place_type":      place["place_type"]   if place else None,
            "author_location": user.location         if user  else None,
            "metrics":         tweet.public_metrics
        })

    os.makedirs("data/raw", exist_ok=True)
    filename = f"data/raw/tweets_{datetime.now().strftime('%Y%m%d_%H%M')}.jsonl"
    with open(filename, "w") as f:
        for post in posts:
            f.write(json.dumps(post) + "\n")

    print(f"Saved {len(posts)} tweets to {filename}")
    return posts


if __name__ == "__main__":
    collect_tweets(max_results=100)