#!/usr/bin/env python3
"""
Tests for interest filtering system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
from src.filters import InterestFilter

class TestInterestFilter(unittest.TestCase):
    """Test interest filtering functionality"""
    
    def setUp(self):
        self.filter = InterestFilter('config/interests_config.json')
        
        # Sample posts for testing
        self.sample_posts = [
            {
                'title': 'New humanoid robot from Boston Dynamics',
                'ai_summary': 'Boston Dynamics unveiled their latest bipedal robot',
                'key_points': ['Advanced robotics', 'Autonomous navigation'],
                'significance': 'Major advancement in robotics',
                'link': 'https://example.com/1'
            },
            {
                'title': 'Facebook announces new feature',
                'ai_summary': 'Social media platform adds new timeline feature',
                'key_points': ['Social media update', 'User interface'],
                'significance': 'Social platform evolution',
                'link': 'https://example.com/2'
            },
            {
                'title': 'Robotics startup raises $50M Series B',
                'ai_summary': 'Funding round led by venture capital firms',
                'key_points': ['Series B funding', 'Robotics investment'],
                'significance': 'Growing robotics market',
                'link': 'https://example.com/3'
            },
            {
                'title': 'Bitcoin reaches new high',
                'ai_summary': 'Cryptocurrency market sees major gains',
                'key_points': ['Blockchain technology', 'Crypto trading'],
                'significance': 'Financial market impact',
                'link': 'https://example.com/4'
            },
            {
                'title': 'Waymo expands robotaxi service',
                'ai_summary': 'Autonomous vehicle company enters new cities',
                'key_points': ['Self-driving cars', 'Urban mobility'],
                'significance': 'Transportation revolution',
                'link': 'https://example.com/5'
            }
        ]
    
    def test_score_calculation(self):
        """Test that scoring works correctly"""
        # Test robotics post (should score high)
        robot_post = self.sample_posts[0]
        score, matches = self.filter.score_post(robot_post)
        
        self.assertGreater(score, 10, "Robotics post should score high")
        self.assertIn('robotics', [m['topic'] for m in matches['matched_topics']])
        self.assertIn('humanoid_robots', [m['topic'] for m in matches['matched_topics']])
    
    def test_exclusion_penalty(self):
        """Test that excluded topics get penalized"""
        # Facebook post should be penalized
        fb_post = self.sample_posts[1]
        score, matches = self.filter.score_post(fb_post)
        self.assertLess(score, 0, "Facebook post should have negative score")
        
        # Bitcoin post should be penalized
        crypto_post = self.sample_posts[3]
        score, matches = self.filter.score_post(crypto_post)
        self.assertLess(score, 0, "Crypto post should have negative score")
    
    def test_relevance_filtering(self):
        """Test filtering relevant posts"""
        filtered = self.filter.get_relevant_posts(self.sample_posts)
        
        # Should include robotics posts
        titles = [p['title'] for p in filtered]
        self.assertIn('New humanoid robot from Boston Dynamics', titles)
        self.assertIn('Robotics startup raises $50M Series B', titles)
        self.assertIn('Waymo expands robotaxi service', titles)
        
        # Should exclude social media and crypto
        self.assertNotIn('Facebook announces new feature', titles)
        self.assertNotIn('Bitcoin reaches new high', titles)
    
    def test_priority_weights(self):
        """Test that priority affects scoring"""
        # Create a post that matches high priority topic
        high_priority_post = {
            'title': 'robot',
            'ai_summary': '',
            'key_points': [],
            'significance': '',
            'link': 'https://example.com/high'
        }
        
        # Create a post that matches medium priority topic
        medium_priority_post = {
            'title': 'waymo',
            'ai_summary': '',
            'key_points': [],
            'significance': '',
            'link': 'https://example.com/medium'
        }
        
        high_score, _ = self.filter.score_post(high_priority_post)
        medium_score, _ = self.filter.score_post(medium_priority_post)
        
        # High priority should score higher than medium
        self.assertGreater(high_score, medium_score)
    
    def test_title_multiplier(self):
        """Test that title matches score higher"""
        # Post with keyword in title
        title_post = {
            'title': 'New robot unveiled',
            'ai_summary': '',
            'key_points': [],
            'significance': '',
            'link': 'https://example.com/title'
        }
        
        # Post with keyword only in summary
        summary_post = {
            'title': 'Tech news',
            'ai_summary': 'New robot unveiled',
            'key_points': [],
            'significance': '',
            'link': 'https://example.com/summary'
        }
        
        title_score, _ = self.filter.score_post(title_post)
        summary_score, _ = self.filter.score_post(summary_post)
        
        # Title match should score higher
        self.assertGreater(title_score, summary_score)
    
    def test_sorting_by_relevance(self):
        """Test that posts are sorted by relevance score"""
        filtered = self.filter.filter_posts(self.sample_posts)
        
        # Check that scores are in descending order
        scores = [p['relevance_score'] for p in filtered]
        self.assertEqual(scores, sorted(scores, reverse=True))

if __name__ == '__main__':
    unittest.main()