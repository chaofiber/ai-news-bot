#!/usr/bin/env python3
"""
Email sender module for daily digest
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict

class EmailSender:
    def __init__(self):
        self.sender = os.getenv('EMAIL_SENDER', 'your_email@gmail.com')
        self.password = os.getenv('EMAIL_PASSWORD', '')
        self.recipient = os.getenv('EMAIL_RECIPIENT', 'recipient@example.com')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
    
    def create_html_email(self, posts: List[Dict]) -> str:
        """Create beautiful HTML email content"""
        
        # Filter for relevant posts only
        relevant_posts = [p for p in posts if p.get('is_relevant', True)]
        high_relevance = [p for p in relevant_posts if p.get('relevance_score', 0) >= 10]
        medium_relevance = [p for p in relevant_posts if 5 <= p.get('relevance_score', 0) < 10]
        
        # Count by topic
        topic_counts = {}
        for post in relevant_posts:
            if 'relevance_matches' in post:
                for match in post['relevance_matches'].get('matched_topics', []):
                    topic = match['topic']
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    margin: -30px -30px 30px -30px;
                    text-align: center;
                }
                h1 {
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }
                .date {
                    font-size: 14px;
                    opacity: 0.9;
                    margin-top: 5px;
                }
                .stats {
                    display: flex;
                    justify-content: space-around;
                    margin: 30px 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                }
                .stat {
                    text-align: center;
                }
                .stat-number {
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                }
                .stat-label {
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .section {
                    margin: 30px 0;
                }
                .section-title {
                    font-size: 20px;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #667eea;
                }
                .post {
                    margin: 20px 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }
                .post-high {
                    border-left-color: #28a745;
                    background-color: #f0fdf4;
                }
                .post-medium {
                    border-left-color: #ffc107;
                    background-color: #fffef0;
                }
                .post-title {
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 10px;
                    color: #2c3e50;
                }
                .post-meta {
                    font-size: 12px;
                    color: #666;
                    margin-bottom: 10px;
                }
                .post-summary {
                    font-size: 14px;
                    color: #555;
                    margin: 10px 0;
                    line-height: 1.5;
                }
                .post-link {
                    display: inline-block;
                    margin-top: 10px;
                    padding: 8px 16px;
                    background-color: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 14px;
                    transition: background-color 0.3s;
                }
                .post-link:hover {
                    background-color: #5a67d8;
                }
                .topics {
                    margin-top: 8px;
                }
                .topic-badge {
                    display: inline-block;
                    padding: 4px 8px;
                    margin: 2px;
                    background-color: #e9ecef;
                    color: #495057;
                    border-radius: 4px;
                    font-size: 12px;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }
                .no-posts {
                    text-align: center;
                    padding: 40px;
                    color: #666;
                    font-style: italic;
                }
                .score {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: bold;
                    margin-left: 10px;
                }
                .score-high {
                    background-color: #28a745;
                    color: white;
                }
                .score-medium {
                    background-color: #ffc107;
                    color: #333;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 TechCrunch Daily Digest</h1>
                    <div class="date">""" + datetime.now().strftime('%B %d, %Y') + """</div>
                </div>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">""" + str(len(relevant_posts)) + """</div>
                        <div class="stat-label">Relevant Posts</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">""" + str(len(high_relevance)) + """</div>
                        <div class="stat-label">High Priority</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">""" + str(len(topic_counts)) + """</div>
                        <div class="stat-label">Topics Covered</div>
                    </div>
                </div>
        """
        
        if high_relevance:
            html += """
                <div class="section">
                    <h2 class="section-title">🔥 High Priority Articles</h2>
            """
            for post in high_relevance[:10]:  # Show up to 10 high priority posts
                html += self._create_post_html(post, 'high')
            html += "</div>"
        
        if medium_relevance:
            html += """
                <div class="section">
                    <h2 class="section-title">📊 Worth Reading</h2>
            """
            for post in medium_relevance[:10]:  # Show up to 10 medium priority posts  
                html += self._create_post_html(post, 'medium')
            html += "</div>"
        
        # Show remaining posts if any
        low_relevance = [p for p in relevant_posts if p.get('relevance_score', 0) < 5]
        if low_relevance:
            html += """
                <div class="section">
                    <h2 class="section-title">📌 Other Articles</h2>
            """
            for post in low_relevance[:10]:  # Show up to 10 more posts
                html += self._create_post_html(post, 'normal')
            html += "</div>"
        
        if not relevant_posts:
            html += """
                <div class="no-posts">
                    <p>No relevant articles found in today's TechCrunch feed.</p>
                    <p>Your interests: robotics, humanoid robots, autonomous vehicles</p>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p>Generated by TechCrunch AI News Bot</p>
                    <p>Personalized for: Robotics, Humanoid Robots, Autonomous Vehicles</p>
                    <p><a href="https://github.com/chaofiber/ai-news-bot" style="color: #667eea;">View on GitHub</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_post_html(self, post: Dict, priority: str = 'normal') -> str:
        """Create HTML for a single post"""
        score = post.get('relevance_score', 0)
        score_class = 'score-high' if score >= 10 else 'score-medium'
        
        topics = []
        if 'relevance_matches' in post:
            topics = [m['topic'].replace('_', ' ').title() 
                     for m in post['relevance_matches'].get('matched_topics', [])]
        
        html = f"""
            <div class="post post-{priority}">
                <div class="post-title">
                    {post['title']}
                    <span class="score {score_class}">Score: {score:.1f}</span>
                </div>
                <div class="post-meta">
                    📅 {post.get('published', 'Unknown date')} | 
                    ✍️ {post.get('author', 'TechCrunch')}
                </div>
        """
        
        if topics:
            html += '<div class="topics">'
            for topic in topics:
                html += f'<span class="topic-badge">{topic}</span>'
            html += '</div>'
        
        if post.get('ai_summary'):
            summary = post['ai_summary']
            if len(summary) > 300:
                summary = summary[:297] + '...'
            html += f'<div class="post-summary">{summary}</div>'
        
        if post.get('key_points'):
            html += '<div class="post-summary"><strong>Key Points:</strong><ul style="margin: 5px 0; padding-left: 20px;">'
            for point in post['key_points'][:3]:
                html += f'<li style="font-size: 13px; margin: 3px 0;">{point}</li>'
            html += '</ul></div>'
        
        html += f"""
                <a href="{post['link']}" class="post-link" target="_blank">Read Full Article →</a>
            </div>
        """
        
        return html
    
    def send_email(self, posts: List[Dict]) -> bool:
        """Send email with the digest"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🤖 TechCrunch Daily Digest - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = self.sender
            msg['To'] = self.recipient
            
            # Create plain text version
            text = self._create_plain_text(posts)
            
            # Create HTML version
            html = self.create_html_email(posts)
            
            # Attach parts
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {self.recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def _create_plain_text(self, posts: List[Dict]) -> str:
        """Create plain text version of email"""
        relevant_posts = [p for p in posts if p.get('is_relevant', True)]
        
        text = f"""
TechCrunch Daily Digest
{datetime.now().strftime('%B %d, %Y')}
{'='*50}

Found {len(relevant_posts)} relevant articles for you today.

"""
        
        for i, post in enumerate(relevant_posts[:10], 1):
            text += f"""
{i}. {post['title']}
   Score: {post.get('relevance_score', 0):.1f}
   Published: {post.get('published', 'Unknown')}
   Link: {post['link']}
   
   {post.get('ai_summary', 'No summary available')[:200]}...
   
{'─'*40}
"""
        
        text += """

Generated by TechCrunch AI News Bot
https://github.com/chaofiber/ai-news-bot
"""
        
        return text