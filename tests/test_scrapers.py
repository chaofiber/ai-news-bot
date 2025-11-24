#!/usr/bin/env python3
"""
Tests for web and RSS scrapers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import datetime, timedelta
import pytz
from src.scrapers import TechCrunchBot, TechCrunchScraper

class TestRSSScraper(unittest.TestCase):
    """Test RSS feed scraper"""
    
    def setUp(self):
        self.bot = TechCrunchBot()
    
    def test_fetch_recent_posts(self):
        """Test fetching recent posts from RSS feed"""
        posts = self.bot.fetch_recent_posts(hours=48)
        
        # RSS feed should return posts
        self.assertIsInstance(posts, list)
        
        if posts:  # If there are posts
            # Check post structure
            post = posts[0]
            self.assertIn('title', post)
            self.assertIn('link', post)
            self.assertIn('published', post)
            self.assertIn('time_ago', post)
            
            # Check link format
            self.assertTrue(post['link'].startswith('https://techcrunch.com/'))
    
    def test_time_filtering(self):
        """Test that posts are filtered by time"""
        # Get posts from last 1 hour (should be very few or none)
        recent_posts = self.bot.fetch_recent_posts(hours=1)
        
        # Get posts from last week
        week_posts = self.bot.fetch_recent_posts(hours=168)
        
        # Week should have more posts than 1 hour
        self.assertGreaterEqual(len(week_posts), len(recent_posts))
    
    def test_clean_text(self):
        """Test HTML cleaning function"""
        html_text = "<p>Hello &amp; welcome to <b>TechCrunch</b></p>"
        cleaned = self.bot._clean_text(html_text)
        self.assertEqual(cleaned, "Hello & welcome to TechCrunch")

class TestWebScraper(unittest.TestCase):
    """Test web scraper"""
    
    def setUp(self):
        self.scraper = TechCrunchScraper()
    
    def test_fetch_posts_from_page(self):
        """Test fetching posts from a single page"""
        posts = self.scraper.fetch_posts_from_page(1)
        
        # Should return posts
        self.assertIsInstance(posts, list)
        
        if posts:
            # Check post structure
            post = posts[0]
            self.assertIn('title', post)
            self.assertIn('link', post)
            self.assertIn('published_datetime', post)
    
    def test_duplicate_removal(self):
        """Test that duplicates are removed"""
        posts = self.scraper.fetch_recent_posts(hours=24, max_pages=2)
        
        # Check for unique URLs
        urls = [p['link'] for p in posts]
        self.assertEqual(len(urls), len(set(urls)), "Duplicate URLs found")
    
    def test_time_ago_calculation(self):
        """Test time ago string generation"""
        now = datetime.now(pytz.UTC)
        
        # Test minutes
        minutes_ago = now - timedelta(minutes=30)
        result = self.scraper._get_time_ago(minutes_ago)
        self.assertIn("minutes ago", result)
        
        # Test hours
        hours_ago = now - timedelta(hours=5)
        result = self.scraper._get_time_ago(hours_ago)
        self.assertIn("hours ago", result)
        
        # Test days
        days_ago = now - timedelta(days=3)
        result = self.scraper._get_time_ago(days_ago)
        self.assertIn("days ago", result)

if __name__ == '__main__':
    unittest.main()