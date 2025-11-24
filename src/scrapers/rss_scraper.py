#!/usr/bin/env python3
"""
TechCrunch News Bot
Fetches all TechCrunch posts from the past 24 hours
"""

import feedparser
from datetime import datetime, timedelta
import pytz
from typing import List, Dict
import requests
from html import unescape
import re

class TechCrunchBot:
    def __init__(self):
        self.feed_url = "https://techcrunch.com/feed/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_recent_posts(self, hours: int = 240) -> List[Dict]:
        """
        Fetch TechCrunch posts from the past specified hours
        
        Args:
            hours: Number of hours to look back (default: 24)
            
        Returns:
            List of post dictionaries with title, link, date, and summary
        """
        try:
            # Parse the RSS feed
            feed = feedparser.parse(self.feed_url)
            
            # Get current time and cutoff time
            now = datetime.now(pytz.UTC)
            cutoff_time = now - timedelta(hours=hours)
            
            recent_posts = []
            
            for entry in feed.entries:
                # Parse the publication date
                pub_date = datetime(*entry.published_parsed[:6])
                pub_date = pytz.UTC.localize(pub_date)
                
                # Check if post is within the time window
                if pub_date >= cutoff_time:
                    # Clean up the summary
                    summary = self._clean_text(entry.get('summary', ''))
                    if len(summary) > 300:
                        summary = summary[:297] + "..."
                    
                    post = {
                        'title': self._clean_text(entry.title),
                        'link': entry.link,
                        'published': pub_date.strftime('%Y-%m-%d %H:%M UTC'),
                        'summary': summary,
                        'time_ago': self._get_time_ago(pub_date, now)
                    }
                    recent_posts.append(post)
            
            # Sort by publication date (newest first)
            recent_posts.sort(key=lambda x: x['published'], reverse=True)
            
            return recent_posts
            
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML and extra whitespace from text"""
        # Remove HTML tags
        text = re.sub('<.*?>', '', text)
        # Unescape HTML entities
        text = unescape(text)
        # Clean up whitespace
        text = ' '.join(text.split())
        return text
    
    def _get_time_ago(self, post_time: datetime, current_time: datetime) -> str:
        """Get human-readable time difference"""
        diff = current_time - post_time
        hours = diff.total_seconds() / 3600
        
        if hours < 1:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minutes ago"
        elif hours < 24:
            return f"{int(hours)} hours ago"
        else:
            days = int(hours / 24)
            return f"{days} days ago"
    
    def display_posts(self, posts: List[Dict]):
        """Display posts in a readable format"""
        if not posts:
            print("No posts found in the past 24 hours.")
            return
        
        print(f"\n{'='*80}")
        print(f"TechCrunch Posts - Past 24 Hours")
        print(f"Found {len(posts)} posts")
        print(f"{'='*80}\n")
        
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title']}")
            print(f"   📅 {post['published']} ({post['time_ago']})")
            print(f"   🔗 {post['link']}")
            if post['summary']:
                print(f"   📝 {post['summary']}")
            print()

def main():
    """Main function to run the bot"""
    print("🤖 TechCrunch News Bot Starting...")
    print("Fetching posts from the past 24 hours...\n")
    
    bot = TechCrunchBot()
    posts = bot.fetch_recent_posts(hours=240)
    bot.display_posts(posts)
    
    # Also return the posts for potential further processing
    return posts

if __name__ == "__main__":
    posts = main()
    print(f"🤖 TechCrunch News Bot Finished. Retrieved {len(posts)} posts.")