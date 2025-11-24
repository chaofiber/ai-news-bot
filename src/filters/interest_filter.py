#!/usr/bin/env python3
"""
Interest-based filtering system for TechCrunch posts
Filters and scores posts based on user-defined interests
"""

import json
import re
from typing import List, Dict, Tuple
from datetime import datetime

class InterestFilter:
    def __init__(self, config_file: str = 'config/interests_config.json'):
        """Initialize the interest filter with configuration"""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.interests = self.config['interests']
        self.exclude_topics = self.config.get('exclude_topics', [])
        self.scoring = self.config['scoring']
        
        # Compile regex patterns for efficient matching
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for all keywords"""
        for interest in self.interests:
            # Create case-insensitive pattern for each keyword
            pattern = '|'.join([r'\b' + re.escape(kw) + r'\b' 
                               for kw in interest['keywords']])
            interest['pattern'] = re.compile(pattern, re.IGNORECASE)
        
        for exclude in self.exclude_topics:
            pattern = '|'.join([r'\b' + re.escape(kw) + r'\b' 
                               for kw in exclude['keywords']])
            exclude['pattern'] = re.compile(pattern, re.IGNORECASE)
    
    def score_post(self, post: Dict) -> Tuple[float, Dict]:
        """
        Score a post based on interest configuration
        
        Returns:
            Tuple of (score, match_details)
        """
        score = 0
        matches = {
            'matched_topics': [],
            'matched_keywords': [],
            'exclude_matches': [],
            'score_breakdown': {}
        }
        
        # Combine all text fields for searching
        title = post.get('title', '')
        summary = post.get('ai_summary', '')
        key_points = ' '.join(post.get('key_points', []))
        significance = post.get('significance', '')
        
        # Check for exclusions first
        for exclude in self.exclude_topics:
            if exclude['pattern'].search(title + ' ' + summary):
                matches['exclude_matches'].append(exclude['topic'])
                score += self.scoring['exclude_penalty']
        
        # If heavily excluded, return early
        if score <= self.scoring['exclude_penalty']:
            matches['score_breakdown']['exclusion_penalty'] = score
            return score, matches
        
        # Score based on interests
        for interest in self.interests:
            topic_score = 0
            topic_matches = []
            
            # Check title (higher weight)
            title_matches = interest['pattern'].findall(title)
            if title_matches:
                weight = self._get_priority_weight(interest['priority'])
                title_score = len(set(title_matches)) * weight * self.scoring['title_match_multiplier']
                topic_score += title_score
                topic_matches.extend(title_matches)
            
            # Check summary
            summary_matches = interest['pattern'].findall(summary)
            if summary_matches:
                weight = self._get_priority_weight(interest['priority'])
                summary_score = len(set(summary_matches)) * weight * self.scoring['summary_match_multiplier']
                topic_score += summary_score
                topic_matches.extend(summary_matches)
            
            # Check key points and significance
            other_text = key_points + ' ' + significance
            other_matches = interest['pattern'].findall(other_text)
            if other_matches:
                weight = self._get_priority_weight(interest['priority'])
                other_score = len(set(other_matches)) * weight
                topic_score += other_score
                topic_matches.extend(other_matches)
            
            if topic_matches:
                matches['matched_topics'].append({
                    'topic': interest['topic'],
                    'priority': interest['priority'],
                    'score': topic_score
                })
                matches['matched_keywords'].extend(list(set(topic_matches)))
                matches['score_breakdown'][interest['topic']] = topic_score
                score += topic_score
        
        return score, matches
    
    def _get_priority_weight(self, priority: str) -> float:
        """Get the weight for a priority level"""
        mapping = {
            'high': self.scoring['high_priority_weight'],
            'medium': self.scoring['medium_priority_weight'],
            'low': self.scoring['low_priority_weight']
        }
        return mapping.get(priority, 1)
    
    def filter_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        Filter and rank posts based on interests
        
        Returns:
            List of posts with relevance scores, sorted by score
        """
        filtered_posts = []
        
        for post in posts:
            score, matches = self.score_post(post)
            
            # Add scoring information to the post
            enhanced_post = {
                **post,
                'relevance_score': score,
                'relevance_matches': matches,
                'is_relevant': score >= self.scoring['minimum_score_threshold']
            }
            
            filtered_posts.append(enhanced_post)
        
        # Sort by relevance score (highest first)
        filtered_posts.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return filtered_posts
    
    def get_relevant_posts(self, posts: List[Dict]) -> List[Dict]:
        """Get only posts that meet the minimum threshold"""
        filtered = self.filter_posts(posts)
        return [p for p in filtered if p['is_relevant']]
    
    def display_filtered_results(self, posts: List[Dict], show_all: bool = False):
        """Display filtered results with relevance information"""
        filtered_posts = self.filter_posts(posts)
        
        if not show_all:
            relevant_posts = [p for p in filtered_posts if p['is_relevant']]
        else:
            relevant_posts = filtered_posts
        
        print("\n" + "="*80)
        print("🎯 INTEREST-FILTERED TECHCRUNCH POSTS")
        print("="*80)
        
        if not relevant_posts:
            print("\n❌ No posts matched your interests today.")
            print(f"   Minimum score threshold: {self.scoring['minimum_score_threshold']}")
            return
        
        # Group by relevance level
        high_relevance = [p for p in relevant_posts if p['relevance_score'] >= 10]
        medium_relevance = [p for p in relevant_posts if 5 <= p['relevance_score'] < 10]
        low_relevance = [p for p in relevant_posts if p['relevance_score'] < 5]
        
        if high_relevance:
            print("\n🔥 HIGHLY RELEVANT:")
            self._display_post_group(high_relevance)
        
        if medium_relevance:
            print("\n📊 MODERATELY RELEVANT:")
            self._display_post_group(medium_relevance)
        
        if low_relevance and show_all:
            print("\n📌 POTENTIALLY RELEVANT:")
            self._display_post_group(low_relevance)
        
        # Summary statistics
        print("\n" + "-"*60)
        print(f"📈 SUMMARY:")
        print(f"   Total posts analyzed: {len(posts)}")
        print(f"   Relevant posts: {len([p for p in relevant_posts if p['is_relevant']])}")
        if high_relevance:
            print(f"   High relevance: {len(high_relevance)}")
        if medium_relevance:
            print(f"   Medium relevance: {len(medium_relevance)}")
    
    def _display_post_group(self, posts: List[Dict]):
        """Display a group of posts"""
        for i, post in enumerate(posts, 1):
            print(f"\n{i}. {post['title']}")
            print(f"   Score: {post['relevance_score']:.1f}")
            print(f"   Link: {post['link']}")
            
            if post['relevance_matches']['matched_topics']:
                topics = [t['topic'] for t in post['relevance_matches']['matched_topics']]
                print(f"   Matched Topics: {', '.join(topics)}")
            
            if post['relevance_matches']['matched_keywords']:
                keywords = list(set(post['relevance_matches']['matched_keywords']))[:5]
                print(f"   Keywords Found: {', '.join(keywords)}")
            
            if post.get('ai_summary'):
                summary = post['ai_summary'][:200] + "..." if len(post['ai_summary']) > 200 else post['ai_summary']
                print(f"   Summary: {summary}")
    
    def save_filtered_posts(self, posts: List[Dict], filename: str = 'filtered_posts.json'):
        """Save filtered posts to a JSON file"""
        filtered_posts = self.get_relevant_posts(posts)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(filtered_posts, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(filtered_posts)} relevant posts to {filename}")

def main():
    """Main function to test the interest filter"""
    print("🎯 Interest Filter Starting...")
    
    # Load summarized posts
    with open('summarized_posts.json', 'r') as f:
        posts = json.load(f)
    
    # Initialize filter
    filter = InterestFilter('interests_config.json')
    
    # Display filtered results
    filter.display_filtered_results(posts, show_all=True)
    
    # Save relevant posts
    filter.save_filtered_posts(posts)
    
    # Show configuration
    print("\n📋 Your Current Interest Configuration:")
    for interest in filter.interests:
        print(f"   - {interest['topic']} ({interest['priority']} priority)")

if __name__ == "__main__":
    main()