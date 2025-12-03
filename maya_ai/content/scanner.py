# maya_ai/content/scanner.py

import praw
import os
import random

class ContentScanner:
    """
    Scans various online sources for interesting content for Maya to react to.
    """
    def __init__(self):
        # --- Reddit API Setup ---
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT"),
                check_for_async=False
            )
            print("Successfully connected to Reddit API.")
        except Exception as e:
            self.reddit = None
            print(f"Error connecting to Reddit API: {e}")
            print("Please ensure your .env file is set up correctly with Reddit credentials.")

    def get_reddit_memes(self, limit=5):
        """
        Fetches top hot posts from a list of meme-related subreddits.
        Filters for image posts and returns a list of dictionaries.
        """
        if not self.reddit:
            print("Cannot fetch from Reddit, API client not initialized.")
            return []

        subreddits = ["memes", "dankmemes", "IndianDankMemes"]
        subreddit_choice = random.choice(subreddits)
        print(f"Scanning r/{subreddit_choice} for hot memes...")

        hot_posts = []
        try:
            subreddit = self.reddit.subreddit(subreddit_choice)
            # Fetching more than needed because we filter out non-image posts
            for post in subreddit.hot(limit=limit * 2):
                # Check if the post is an image and not stickied
                if not post.stickied and post.url.endswith(('jpg', 'jpeg', 'png', 'gif')):
                    post_data = {
                        "source": "Reddit",
                        "subreddit": subreddit_choice,
                        "title": post.title,
                        "url": post.url,
                        "score": post.score,
                        "author": str(post.author)
                    }
                    hot_posts.append(post_data)

                if len(hot_posts) >= limit:
                    break

            print(f"Found {len(hot_posts)} image-based memes.")
            return hot_posts
        except Exception as e:
            print(f"An error occurred while fetching from r/{subreddit_choice}: {e}")
            return []

    def get_twitter_trends(self):
        """Placeholder for fetching trending topics from Twitter."""
        print("Twitter scanning is not yet implemented.")
        # TODO: Implement Tweepy logic here
        return []

    def get_tech_news(self):
        """Placeholder for fetching tech news."""
        print("News scanning is not yet implemented.")
        # TODO: Implement a news API or RSS feed reader here
        return []

    def check_creator_posts(self):
        """Placeholder for checking if the creator has posted anything new."""
        print("Creator post checking is not yet implemented.")
        # TODO: Implement logic to check a specific user's social media
        return []

# --- Example Usage ---
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print("--- Testing Content Scanner ---")
    scanner = ContentScanner()

    if scanner.reddit:
        print("\nFetching Reddit memes...")
        memes = scanner.get_reddit_memes(limit=3)
        if memes:
            for i, meme in enumerate(memes, 1):
                print(f"\n--- Meme #{i} ---")
                print(f"  Title: {meme['title']}")
                print(f"  URL: {meme['url']}")
                print(f"  Subreddit: r/{meme['subreddit']}")
                print(f"  Score: {meme['score']}")
        else:
            print("Could not retrieve any memes. Check your API credentials and network.")

    print("\n--- Content Scanner Test Complete ---")
