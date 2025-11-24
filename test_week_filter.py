#!/usr/bin/env python3
"""
Test script to analyze one week of posts with interest filtering
(Using a subset to avoid excessive API calls)
"""

import json
import time
from gemini_summarizer import GeminiSummarizer
from interest_filter import InterestFilter

def main():
    # Load all posts
    with open('techcrunch_posts.json', 'r') as f:
        all_posts = json.load(f)
    
    print(f"📊 Loaded {len(all_posts)} posts from the past week")
    
    # Sample 20 posts for summarization (to save API calls)
    # Select posts that might match our interests based on titles
    robot_keywords = ['robot', 'autonomous', 'waymo', 'zoox', 'tesla', 'monarch', 'tractor', 'starship', 'drone']
    
    potentially_relevant = []
    other_posts = []
    
    for post in all_posts:
        title_lower = post['title'].lower()
        if any(keyword in title_lower for keyword in robot_keywords):
            potentially_relevant.append(post)
        else:
            other_posts.append(post)
    
    # Take up to 15 potentially relevant posts and 5 random others
    sample_posts = potentially_relevant[:15] + other_posts[:5]
    
    print(f"🎯 Selected {len(sample_posts)} posts for analysis")
    print(f"   - {len(potentially_relevant[:15])} potentially relevant")
    print(f"   - {len(other_posts[:5])} other posts")
    
    # Summarize the sample
    print("\n📝 Summarizing posts with Gemini...")
    summarizer = GeminiSummarizer()
    
    summarized_posts = []
    for i, post in enumerate(sample_posts, 1):
        print(f"[{i}/{len(sample_posts)}] {post['title'][:50]}...")
        summarized = summarizer.summarize_post(post)
        summarized_posts.append(summarized)
        
        # Be polite to API
        if i < len(sample_posts):
            time.sleep(2)
    
    # Save summarized sample
    with open('week_sample_summarized.json', 'w') as f:
        json.dump(summarized_posts, f, indent=2)
    
    # Apply interest filter
    print("\n🔍 Applying interest filter...")
    filter = InterestFilter('interests_config.json')
    
    # Analyze all posts
    filtered_posts = filter.filter_posts(summarized_posts)
    
    # Get statistics
    relevant_posts = [p for p in filtered_posts if p['is_relevant']]
    high_score = [p for p in filtered_posts if p['relevance_score'] >= 10]
    medium_score = [p for p in filtered_posts if 5 <= p['relevance_score'] < 10]
    
    print("\n" + "="*80)
    print("📊 INTEREST FILTERING RESULTS - ONE WEEK ANALYSIS")
    print("="*80)
    
    print(f"\n📈 Statistics:")
    print(f"   Total posts analyzed: {len(sample_posts)}")
    print(f"   Relevant posts (score ≥ 3): {len(relevant_posts)}")
    print(f"   High relevance (score ≥ 10): {len(high_score)}")
    print(f"   Medium relevance (5-9): {len(medium_score)}")
    
    print(f"\n🔥 TOP RELEVANT POSTS:")
    for i, post in enumerate(high_score[:10], 1):
        print(f"\n{i}. {post['title']}")
        print(f"   Score: {post['relevance_score']:.1f}")
        print(f"   Topics: {', '.join([m['topic'] for m in post['relevance_matches']['matched_topics']])}")
        print(f"   Keywords: {', '.join(post['relevance_matches']['matched_keywords'][:5])}")
    
    # Topic distribution
    print(f"\n📊 TOPIC DISTRIBUTION:")
    topic_counts = {}
    for post in relevant_posts:
        for match in post['relevance_matches']['matched_topics']:
            topic = match['topic']
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count} posts")
    
    # Save results
    with open('week_filtered_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_analyzed': len(sample_posts),
                'relevant_posts': len(relevant_posts),
                'high_relevance': len(high_score),
                'medium_relevance': len(medium_score),
                'topic_distribution': topic_counts
            },
            'relevant_posts': relevant_posts
        }, f, indent=2)
    
    print(f"\n✅ Results saved to week_filtered_results.json")

if __name__ == "__main__":
    main()