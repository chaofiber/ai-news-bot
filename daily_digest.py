#!/usr/bin/env python3
"""
Daily Digest Script for GitHub Actions
Fetches, summarizes, filters, and emails TechCrunch articles
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.scrapers import TechCrunchScraper
from src.summarizers import GeminiSummarizer  
from src.filters import InterestFilter
from src.email_sender import EmailSender

def run_daily_digest():
    """Main function for daily digest"""
    
    print("="*60)
    print(f"🤖 TechCrunch Daily Digest - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        # Step 1: Fetch posts from last 24 hours using scraper
        print("\n📰 Step 1: Fetching posts from last 24 hours...")
        scraper = TechCrunchScraper()
        posts = scraper.fetch_recent_posts(hours=24, max_pages=5)
        print(f"✅ Fetched {len(posts)} posts")
        
        if not posts:
            print("❌ No posts found. Exiting.")
            return
        
        # Step 2: Summarize posts with Gemini
        print("\n🤖 Step 2: Summarizing posts with AI...")
        try:
            summarizer = GeminiSummarizer()
            summarized_posts = []
            
            for i, post in enumerate(posts, 1):
                if i % 10 == 0:
                    print(f"  Progress: {i}/{len(posts)}")
                summarized_post = summarizer.summarize_post(post)
                summarized_posts.append(summarized_post)
            
            print(f"✅ Summarized {len(summarized_posts)} posts")
        except Exception as e:
            print(f"⚠️  Warning: Summarization failed ({e}), continuing with original posts")
            summarized_posts = posts
        
        # Step 3: Filter posts based on interests
        print("\n🎯 Step 3: Filtering posts based on interests...")
        filter = InterestFilter('config/interests_config.json')
        filtered_posts = filter.filter_posts(summarized_posts)
        relevant_posts = [p for p in filtered_posts if p['is_relevant']]
        print(f"✅ Found {len(relevant_posts)} relevant posts")
        
        # Step 4: Save results
        print("\n💾 Step 4: Saving results...")
        os.makedirs('data', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Save all filtered posts
        output_file = f'data/daily_digest_{timestamp}.json'
        with open(output_file, 'w') as f:
            json.dump(filtered_posts, f, indent=2)
        print(f"✅ Saved to {output_file}")
        
        # Step 5: Send email if configured
        email_recipient = os.getenv('EMAIL_RECIPIENT')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if email_recipient and email_password:
            print("\n📧 Step 5: Sending email digest...")
            sender = EmailSender()
            success = sender.send_email(filtered_posts)
            if success:
                print("✅ Email sent successfully")
            else:
                print("❌ Failed to send email")
        else:
            print("\n📧 Step 5: Email not configured, skipping...")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 DIGEST SUMMARY")
        print("="*60)
        print(f"Total posts fetched: {len(posts)}")
        print(f"Relevant posts found: {len(relevant_posts)}")
        
        if relevant_posts:
            print("\n🔥 Top relevant posts:")
            for i, post in enumerate(relevant_posts[:5], 1):
                score = post.get('relevance_score', 0)
                print(f"{i}. [{score:.1f}] {post['title'][:60]}...")
        
        print("\n✅ Daily digest completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running digest: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_daily_digest()