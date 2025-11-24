#!/usr/bin/env python3
"""
Test Email Digest Locally
Run this to test the email functionality without GitHub Actions
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from src.email_sender import EmailSender

def test_with_sample_data():
    """Test with sample data (no API calls needed)"""
    
    # Sample data mimicking filtered posts
    sample_posts = [
        {
            'title': 'Boston Dynamics unveils new Atlas humanoid robot',
            'link': 'https://techcrunch.com/2024/example/atlas-robot',
            'published': '2024-11-24 10:00 UTC',
            'author': 'TechCrunch',
            'ai_summary': 'Boston Dynamics revealed its latest Atlas humanoid robot featuring advanced bipedal locomotion and AI-powered perception systems. The robot demonstrates unprecedented agility and can perform complex tasks in industrial environments.',
            'key_points': [
                'New hydraulic actuators provide 50% more power',
                'AI vision system can identify and manipulate objects',
                'Battery life extended to 4 hours of continuous operation'
            ],
            'significance': 'Major advancement in humanoid robotics for industrial applications',
            'relevance_score': 28.5,
            'is_relevant': True,
            'relevance_matches': {
                'matched_topics': [
                    {'topic': 'robotics', 'priority': 'high', 'score': 15},
                    {'topic': 'humanoid_robots', 'priority': 'high', 'score': 13.5}
                ],
                'matched_keywords': ['robot', 'humanoid', 'atlas', 'bipedal', 'robotics']
            }
        },
        {
            'title': 'Waymo expands robotaxi service to 10 new cities',
            'link': 'https://techcrunch.com/2024/example/waymo-expansion',
            'published': '2024-11-24 08:30 UTC',
            'author': 'TechCrunch Staff',
            'ai_summary': 'Waymo announced a major expansion of its autonomous vehicle service, bringing robotaxis to 10 new US cities. The expansion represents the largest rollout of autonomous vehicles to date.',
            'key_points': [
                'Service will launch in Seattle, Boston, and Chicago first',
                'Fleet size increasing to 10,000 vehicles',
                'Partnership with Uber for seamless integration'
            ],
            'significance': 'Marks a turning point in autonomous vehicle adoption',
            'relevance_score': 22.0,
            'is_relevant': True,
            'relevance_matches': {
                'matched_topics': [
                    {'topic': 'autonomous_vehicles', 'priority': 'medium', 'score': 12},
                    {'topic': 'robotics', 'priority': 'high', 'score': 10}
                ],
                'matched_keywords': ['waymo', 'robotaxi', 'autonomous', 'self-driving']
            }
        },
        {
            'title': 'Robotics startup Figure raises $500M at $5B valuation',
            'link': 'https://techcrunch.com/2024/example/figure-funding',
            'published': '2024-11-24 06:00 UTC',
            'author': 'Mary Ann Azevedo',
            'ai_summary': 'Figure, a humanoid robotics startup, closed a massive $500M Series C round led by Microsoft and OpenAI. The company plans to accelerate development of its general-purpose humanoid robots.',
            'key_points': [
                'Funding led by Microsoft, OpenAI, and Jeff Bezos',
                'Valuation jumped from $1B to $5B in one year',
                'Plans to deploy 1,000 robots by end of 2025'
            ],
            'significance': 'Signals massive investor confidence in humanoid robotics',
            'relevance_score': 31.0,
            'is_relevant': True,
            'relevance_matches': {
                'matched_topics': [
                    {'topic': 'robotics_startups', 'priority': 'high', 'score': 18},
                    {'topic': 'humanoid_robots', 'priority': 'high', 'score': 13}
                ],
                'matched_keywords': ['robotics', 'startup', 'Figure', 'humanoid', 'funding', 'Series']
            }
        },
        {
            'title': 'Meta launches new VR headset for consumers',
            'link': 'https://techcrunch.com/2024/example/meta-vr',
            'published': '2024-11-24 05:00 UTC',
            'author': 'TechCrunch',
            'ai_summary': 'Meta unveiled its latest Quest VR headset with improved display and processing power, targeting mainstream consumers.',
            'key_points': ['Better display', 'Lower price point', 'New content partnerships'],
            'relevance_score': 0,
            'is_relevant': False,
            'relevance_matches': {
                'matched_topics': [],
                'matched_keywords': []
            }
        },
        {
            'title': 'Tesla Optimus robot demonstrates new capabilities',
            'link': 'https://techcrunch.com/2024/example/tesla-optimus',
            'published': '2024-11-23 22:00 UTC',
            'author': 'TechCrunch',
            'ai_summary': 'Tesla showcased new capabilities of its Optimus humanoid robot, including ability to sort objects autonomously and navigate complex environments using neural networks.',
            'key_points': [
                'Demonstrated autonomous object sorting',
                'Uses same FSD neural network as Tesla cars',
                'Production timeline moved to 2025'
            ],
            'significance': 'Shows Tesla\'s progress in transferring autonomous vehicle tech to robotics',
            'relevance_score': 8.5,
            'is_relevant': True,
            'relevance_matches': {
                'matched_topics': [
                    {'topic': 'humanoid_robots', 'priority': 'high', 'score': 5},
                    {'topic': 'autonomous_vehicles', 'priority': 'medium', 'score': 3.5}
                ],
                'matched_keywords': ['Tesla', 'Optimus', 'robot', 'humanoid', 'autonomous']
            }
        }
    ]
    
    return sample_posts

def test_email_preview():
    """Generate email preview without sending"""
    
    print("📧 Testing Email Digest Locally")
    print("="*60)
    
    # Get sample data
    posts = test_with_sample_data()
    print(f"✅ Loaded {len(posts)} sample posts")
    
    # Create email sender
    sender = EmailSender()
    
    # Generate HTML
    html_content = sender.create_html_email(posts)
    
    # Save HTML to file for preview
    preview_file = 'email_preview.html'
    with open(preview_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ HTML email saved to: {preview_file}")
    print("   Open this file in your browser to preview the email")
    
    # Show email configuration
    print("\n📮 Email Configuration:")
    print(f"   From: {sender.sender}")
    print(f"   To: {sender.recipient}")
    print(f"   SMTP: {sender.smtp_server}:{sender.smtp_port}")
    
    # Ask if user wants to send test email
    print("\n" + "="*60)
    response = input("Would you like to send a test email? (y/n): ").lower()
    
    if response == 'y':
        if not sender.password:
            print("❌ EMAIL_PASSWORD not set in .env file")
            print("   Add your email app password to .env:")
            print("   EMAIL_PASSWORD=your-app-password")
            return
        
        print("\n📤 Sending test email...")
        success = sender.send_email(posts)
        if success:
            print(f"✅ Test email sent to {sender.recipient}")
        else:
            print("❌ Failed to send email. Check your credentials.")
    else:
        print("ℹ️  Email not sent. You can preview it in email_preview.html")

def test_with_real_data():
    """Test with real data (requires API key)"""
    
    print("📊 Testing with Real Data")
    print("="*60)
    
    try:
        # Check if we have recent data
        data_files = [f for f in os.listdir('data') if f.endswith('.json')]
        if data_files:
            latest = sorted(data_files)[-1]
            print(f"Found existing data: {latest}")
            use_existing = input("Use existing data? (y/n): ").lower()
            
            if use_existing == 'y':
                with open(f'data/{latest}', 'r') as f:
                    posts = json.load(f)
                print(f"✅ Loaded {len(posts)} posts from {latest}")
                
                # Send email
                sender = EmailSender()
                html_content = sender.create_html_email(posts)
                
                with open('email_preview.html', 'w') as f:
                    f.write(html_content)
                print("✅ Preview saved to email_preview.html")
                
                return
        
        # Run full pipeline
        print("\nRunning full pipeline (this will use API calls)...")
        from daily_digest import run_daily_digest
        run_daily_digest()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nFalling back to sample data...")
        test_email_preview()

def main():
    print("\n🧪 TechCrunch Email Digest - Local Test")
    print("="*60)
    print("\nOptions:")
    print("1. Test with sample data (no API needed)")
    print("2. Test with real data (requires Gemini API)")
    print("3. Use existing data file")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '1':
        test_email_preview()
    elif choice == '2':
        test_with_real_data()
    elif choice == '3':
        # List data files
        data_files = [f for f in os.listdir('data') if f.endswith('.json')]
        if data_files:
            print("\nAvailable data files:")
            for i, f in enumerate(data_files, 1):
                print(f"{i}. {f}")
            
            file_choice = input("Select file number: ").strip()
            try:
                file_idx = int(file_choice) - 1
                with open(f'data/{data_files[file_idx]}', 'r') as f:
                    posts = json.load(f)
                
                sender = EmailSender()
                html_content = sender.create_html_email(posts)
                
                with open('email_preview.html', 'w') as f:
                    f.write(html_content)
                print(f"✅ Preview saved to email_preview.html")
                
                send = input("Send test email? (y/n): ").lower()
                if send == 'y':
                    sender.send_email(posts)
            except:
                print("❌ Invalid selection")
        else:
            print("No data files found")
    else:
        print("Invalid option. Using sample data...")
        test_email_preview()

if __name__ == '__main__':
    main()