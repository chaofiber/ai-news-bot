#!/usr/bin/env python3
"""
Gemini-powered summarizer for TechCrunch posts
"""

import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

class GeminiSummarizer:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError("Please set your GEMINI_API_KEY in the .env file")
        
        genai.configure(api_key=api_key)
        
        # Initialize the model (using Gemini 2.0 Flash for efficiency)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def fetch_article_content(self, url: str) -> str:
        """
        Fetch the full article content from a URL
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Try to find the article content
            article_content = ""
            
            # Common article content selectors for TechCrunch
            content_selectors = [
                'div.article-content',
                'div.post-content',
                'article',
                'main',
                'div[class*="content"]'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Extract text from paragraphs
                    paragraphs = content_elem.find_all('p')
                    article_content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if article_content:
                        break
            
            # Fallback: get all paragraphs if no specific content area found
            if not article_content:
                all_paragraphs = soup.find_all('p')
                article_content = ' '.join([p.get_text(strip=True) for p in all_paragraphs[:20]])  # Limit to first 20 paragraphs
            
            return article_content[:5000]  # Limit to 5000 characters to avoid token limits
            
        except Exception as e:
            print(f"Error fetching article from {url}: {e}")
            return ""
    
    def summarize_post(self, post: Dict) -> Dict:
        """
        Summarize a single post using Gemini
        """
        try:
            # Fetch the full article content
            full_content = self.fetch_article_content(post['link'])
            
            if not full_content:
                print(f"Could not fetch content for: {post['title']}")
                return {**post, 'ai_summary': 'Content not available', 'key_points': []}
            
            # Create a prompt for Gemini
            prompt = f"""
            Please provide a comprehensive summary of the following tech news article.
            
            Title: {post['title']}
            Published: {post['published']}
            
            Article content:
            {full_content}
            
            Please provide:
            1. A 2-3 sentence executive summary
            2. 3-5 key bullet points
            3. Why this matters to the tech industry (1 sentence)
            
            Format your response as JSON with the following structure:
            {{
                "summary": "Executive summary here",
                "key_points": ["point 1", "point 2", "point 3"],
                "significance": "Why this matters"
            }}
            """
            
            # Generate summary using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                # Clean the response text to extract JSON
                response_text = response.text
                # Find JSON content between curly braces
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end != 0:
                    json_text = response_text[start:end]
                    summary_data = json.loads(json_text)
                else:
                    # Fallback if JSON parsing fails
                    summary_data = {
                        "summary": response.text[:300],
                        "key_points": [],
                        "significance": ""
                    }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                summary_data = {
                    "summary": response.text[:300],
                    "key_points": [],
                    "significance": ""
                }
            
            # Add the summary to the post
            enhanced_post = {
                **post,
                'ai_summary': summary_data.get('summary', ''),
                'key_points': summary_data.get('key_points', []),
                'significance': summary_data.get('significance', ''),
                'content_length': len(full_content)
            }
            
            return enhanced_post
            
        except Exception as e:
            print(f"Error summarizing post '{post['title']}': {e}")
            return {
                **post,
                'ai_summary': f'Error generating summary: {str(e)}',
                'key_points': [],
                'significance': ''
            }
    
    def summarize_posts(self, posts_file: str = 'techcrunch_posts.json') -> List[Dict]:
        """
        Summarize all posts from a JSON file
        """
        # Load posts
        with open(posts_file, 'r') as f:
            posts = json.load(f)
        
        print(f"📚 Summarizing {len(posts)} posts using Gemini...")
        
        summarized_posts = []
        for i, post in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}] Summarizing: {post['title'][:60]}...")
            
            summarized_post = self.summarize_post(post)
            summarized_posts.append(summarized_post)
            
            # Display the summary
            print(f"✅ Summary: {summarized_post['ai_summary'][:200]}...")
            if summarized_post['key_points']:
                print("📍 Key Points:")
                for point in summarized_post['key_points'][:3]:
                    print(f"   • {point}")
            
            # Be polite to the API (avoid rate limiting)
            if i < len(posts):
                time.sleep(2)
        
        return summarized_posts
    
    def save_summaries(self, summarized_posts: List[Dict], filename: str = 'summarized_posts.json'):
        """
        Save summarized posts to a JSON file
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summarized_posts, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(summarized_posts)} summarized posts to {filename}")
    
    def display_summaries(self, summarized_posts: List[Dict]):
        """
        Display summaries in a readable format
        """
        print("\n" + "="*80)
        print("📰 TECHCRUNCH DAILY DIGEST - AI SUMMARIES")
        print("="*80)
        
        for i, post in enumerate(summarized_posts, 1):
            print(f"\n{i}. {post['title']}")
            print(f"   📅 {post['published']} ({post.get('time_ago', 'N/A')})")
            print(f"   🔗 {post['link']}")
            print(f"\n   📝 Summary: {post.get('ai_summary', 'No summary available')}")
            
            if post.get('key_points'):
                print("\n   🎯 Key Points:")
                for point in post['key_points']:
                    print(f"      • {point}")
            
            if post.get('significance'):
                print(f"\n   💡 Why it matters: {post['significance']}")
            
            print("\n" + "-"*60)

def main():
    """Main function to run the summarizer"""
    print("🤖 Gemini Summarizer Starting...")
    print("First, please make sure you've added your Gemini API key to the .env file\n")
    
    try:
        summarizer = GeminiSummarizer()
        
        # Summarize the posts
        summarized_posts = summarizer.summarize_posts('techcrunch_posts.json')
        
        # Save the summaries
        summarizer.save_summaries(summarized_posts)
        
        # Display the summaries
        summarizer.display_summaries(summarized_posts)
        
        print("\n✅ Summarization complete!")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please edit the .env file and add your Gemini API key:")
        print("GEMINI_API_KEY=your_actual_api_key_here")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()