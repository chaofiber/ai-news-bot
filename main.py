#!/usr/bin/env python3
"""
TechCrunch News Bot - Main Entry Point
A bot that fetches, summarizes, and filters TechCrunch articles based on your interests
"""

import argparse
import json
import os
import sys
from datetime import datetime

from src.scrapers import TechCrunchBot, TechCrunchScraper
from src.summarizers import GeminiSummarizer
from src.filters import InterestFilter

def fetch_posts(hours: int = 24, use_scraper: bool = True, max_pages: int = 5):
    """Fetch posts from TechCrunch"""
    print(f"📰 Fetching TechCrunch posts from the past {hours} hours...")
    
    if use_scraper:
        scraper = TechCrunchScraper()
        posts = scraper.fetch_recent_posts(hours=hours, max_pages=max_pages)
    else:
        bot = TechCrunchBot()
        posts = bot.fetch_recent_posts(hours=hours)
    
    print(f"✅ Fetched {len(posts)} posts")
    return posts

def summarize_posts(posts: list, output_file: str = 'data/summarized_posts.json'):
    """Summarize posts using Gemini AI"""
    print(f"\n🤖 Summarizing {len(posts)} posts with Gemini AI...")
    
    try:
        summarizer = GeminiSummarizer()
        summarized = []
        
        for i, post in enumerate(posts, 1):
            print(f"[{i}/{len(posts)}] {post['title'][:50]}...")
            summarized_post = summarizer.summarize_post(post)
            summarized.append(summarized_post)
        
        # Save results
        os.makedirs('data', exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(summarized, f, indent=2)
        
        print(f"✅ Saved summaries to {output_file}")
        return summarized
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please ensure your GEMINI_API_KEY is set in the .env file")
        return posts

def filter_posts(posts: list, config_file: str = 'config/interests_config.json'):
    """Filter posts based on interests"""
    print(f"\n🎯 Filtering posts based on your interests...")
    
    filter = InterestFilter(config_file)
    filtered = filter.filter_posts(posts)
    
    relevant = [p for p in filtered if p['is_relevant']]
    print(f"✅ Found {len(relevant)} relevant posts out of {len(posts)}")
    
    return filtered

def display_results(posts: list, show_all: bool = False):
    """Display filtered results"""
    relevant = [p for p in posts if p['is_relevant']] if not show_all else posts
    
    if not relevant:
        print("\n❌ No relevant posts found")
        return
    
    print("\n" + "="*80)
    print("📊 RELEVANT POSTS")
    print("="*80)
    
    for i, post in enumerate(relevant[:10], 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Score: {post.get('relevance_score', 0):.1f}")
        print(f"   Link: {post['link']}")
        
        if post.get('ai_summary'):
            summary = post['ai_summary'][:200] + "..." if len(post['ai_summary']) > 200 else post['ai_summary']
            print(f"   Summary: {summary}")

def main():
    parser = argparse.ArgumentParser(description='TechCrunch News Bot')
    parser.add_argument('--hours', type=int, default=24, 
                      help='Number of hours to look back (default: 24)')
    parser.add_argument('--scraper', action='store_true', 
                      help='Use web scraper instead of RSS feed')
    parser.add_argument('--summarize', action='store_true', 
                      help='Summarize posts using Gemini AI')
    parser.add_argument('--filter', action='store_true', 
                      help='Filter posts based on interests')
    parser.add_argument('--all', action='store_true', 
                      help='Show all posts, not just relevant ones')
    parser.add_argument('--save', type=str, 
                      help='Save results to file')
    
    args = parser.parse_args()
    
    print("🚀 TechCrunch News Bot")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Fetch posts
    posts = fetch_posts(hours=args.hours, use_scraper=args.scraper)
    
    # Summarize if requested
    if args.summarize:
        posts = summarize_posts(posts)
    
    # Filter if requested
    if args.filter:
        posts = filter_posts(posts)
        display_results(posts, show_all=args.all)
    else:
        # Display all posts
        print(f"\n📰 Found {len(posts)} posts:")
        for i, post in enumerate(posts[:20], 1):
            print(f"{i}. {post['title']}")
    
    # Save if requested
    if args.save:
        os.makedirs('data', exist_ok=True)
        output_file = f"data/{args.save}"
        with open(output_file, 'w') as f:
            json.dump(posts, f, indent=2)
        print(f"\n💾 Saved results to {output_file}")

if __name__ == '__main__':
    main()