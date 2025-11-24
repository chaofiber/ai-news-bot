#!/usr/bin/env python3
"""
Enhanced TechCrunch News Bot with Web Scraping
Fetches more TechCrunch posts by scraping the website directly
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from typing import List, Dict
import time
import json

class TechCrunchScraper:
    def __init__(self):
        self.base_url = "https://techcrunch.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_posts_from_page(self, page_num: int = 1) -> List[Dict]:
        """
        Fetch posts from a specific page of TechCrunch
        """
        try:
            # TechCrunch uses pagination with /page/2/, /page/3/, etc.
            if page_num == 1:
                url = self.base_url
            else:
                url = f"{self.base_url}/page/{page_num}/"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            posts = []
            
            # Try multiple possible selectors
            articles = []
            
            # Modern TechCrunch structure - look for links with specific patterns
            # Find all h2 or h3 tags that might contain article titles
            for heading in soup.find_all(['h2', 'h3']):
                link = heading.find('a')
                if link and link.get('href', '').startswith('https://techcrunch.com/20'):
                    articles.append(heading.parent)
            
            # If no articles found with that method, try finding all article links
            if not articles:
                all_links = soup.find_all('a', href=True)
                article_links = {}
                for link in all_links:
                    href = link.get('href', '')
                    # TechCrunch article URLs follow pattern: /YYYY/MM/DD/slug/
                    if 'techcrunch.com/20' in href and '/page/' not in href and href not in article_links:
                        # Get the parent container that likely has the full article info
                        parent = link.parent
                        while parent and parent.name not in ['div', 'article', 'li']:
                            parent = parent.parent
                        if parent and link.get_text(strip=True):
                            article_links[href] = (link, parent)
                
                articles = [item[1] for item in article_links.values()]
            
            seen_urls = set()
            for article in articles:
                try:
                    # Extract link and title
                    link_elem = article.find('a', href=lambda x: x and 'techcrunch.com/20' in x)
                    if not link_elem:
                        continue
                    
                    link = link_elem.get('href')
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)
                    
                    title = link_elem.get_text(strip=True)
                    if not title or len(title) < 10:
                        # Try to find a better title
                        heading = article.find(['h2', 'h3'])
                        if heading:
                            title = heading.get_text(strip=True)
                    
                    if not title:
                        continue
                    
                    # Extract date - try multiple methods
                    pub_date = None
                    
                    # Method 1: Look for time element
                    time_elem = article.find('time')
                    if time_elem and time_elem.get('datetime'):
                        try:
                            pub_date = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                        except:
                            pass
                    
                    # Method 2: Parse from URL
                    if not pub_date and '/20' in link:
                        try:
                            import re
                            date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
                            if date_match:
                                year, month, day = date_match.groups()
                                pub_date = datetime(int(year), int(month), int(day), tzinfo=pytz.UTC)
                        except:
                            pass
                    
                    if not pub_date:
                        continue
                    
                    # Extract summary - look for any text that might be a description
                    summary = ""
                    for elem in article.find_all(['p', 'div']):
                        text = elem.get_text(strip=True)
                        if len(text) > 50 and title not in text:
                            summary = text
                            break
                    
                    if len(summary) > 300:
                        summary = summary[:297] + "..."
                    
                    # Extract author
                    author = "TechCrunch"
                    author_elem = article.find(['span', 'div'], string=lambda t: t and 'by' in t.lower())
                    if author_elem:
                        author = author_elem.get_text(strip=True).replace('by', '').strip()
                    
                    post = {
                        'title': title,
                        'link': link,
                        'published': pub_date.strftime('%Y-%m-%d %H:%M UTC'),
                        'published_datetime': pub_date,
                        'summary': summary,
                        'author': author,
                        'time_ago': self._get_time_ago(pub_date)
                    }
                    posts.append(post)
                    
                except Exception as e:
                    continue
            
            return posts
            
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            return []
    
    def fetch_recent_posts(self, hours: int = 24, max_pages: int = 10) -> List[Dict]:
        """
        Fetch TechCrunch posts from the past specified hours
        
        Args:
            hours: Number of hours to look back
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of post dictionaries
        """
        all_posts = []
        seen_urls = set()  # Track URLs to avoid duplicates
        cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=hours)
        
        print(f"Fetching posts from the past {hours} hours...")
        print(f"Cutoff time: {cutoff_time.strftime('%Y-%m-%d %H:%M UTC')}")
        
        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}...")
            posts = self.fetch_posts_from_page(page)
            
            if not posts:
                print(f"No posts found on page {page}, stopping...")
                break
            
            # Filter posts by time and add to collection (avoiding duplicates)
            page_has_old_posts = False
            new_posts_on_page = 0
            
            for post in posts:
                # Skip duplicates based on URL
                if post['link'] in seen_urls:
                    continue
                    
                if post['published_datetime'] >= cutoff_time:
                    all_posts.append(post)
                    seen_urls.add(post['link'])
                    new_posts_on_page += 1
                else:
                    page_has_old_posts = True
            
            print(f"  Found {new_posts_on_page} new unique posts on this page")
            
            # If all posts on this page are older than cutoff, stop
            if page_has_old_posts and all(p['published_datetime'] < cutoff_time for p in posts):
                print(f"All posts on page {page} are older than cutoff, stopping...")
                break
            
            # Be polite to the server
            time.sleep(1)
        
        # Sort by date (newest first)
        all_posts.sort(key=lambda x: x['published_datetime'], reverse=True)
        
        print(f"\nTotal unique posts found: {len(all_posts)}")
        
        # Remove the datetime object before returning
        for post in all_posts:
            del post['published_datetime']
        
        return all_posts
    
    def _get_time_ago(self, post_time: datetime) -> str:
        """Get human-readable time difference"""
        now = datetime.now(pytz.UTC)
        diff = now - post_time
        total_hours = diff.total_seconds() / 3600
        
        if total_hours < 1:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minutes ago"
        elif total_hours < 24:
            return f"{int(total_hours)} hours ago"
        else:
            days = int(total_hours / 24)
            if days == 1:
                return "1 day ago"
            return f"{days} days ago"
    
    def display_posts(self, posts: List[Dict]):
        """Display posts in a readable format"""
        if not posts:
            print("No posts found in the specified time range.")
            return
        
        print(f"\n{'='*80}")
        print(f"TechCrunch Posts - Found {len(posts)} posts")
        print(f"{'='*80}\n")
        
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title']}")
            print(f"   📅 {post['published']} ({post['time_ago']})")
            print(f"   ✍️  {post['author']}")
            print(f"   🔗 {post['link']}")
            if post['summary']:
                print(f"   📝 {post['summary']}")
            print()
    
    def save_to_json(self, posts: List[Dict], filename: str = "techcrunch_posts.json"):
        """Save posts to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(posts)} posts to {filename}")

def main():
    """Main function to run the enhanced bot"""
    print("🤖 Enhanced TechCrunch Scraper Starting...")
    
    scraper = TechCrunchScraper()
    
    # Fetch posts from the past 168 hours (7 days)
    posts = scraper.fetch_recent_posts(hours=168, max_pages=10)
    
    # Display the posts
    scraper.display_posts(posts)
    
    # Optionally save to JSON
    if posts:
        scraper.save_to_json(posts)
    
    return posts

if __name__ == "__main__":
    posts = main()
    print(f"\n🤖 Scraper finished. Retrieved {len(posts)} posts total.")