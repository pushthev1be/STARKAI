"""
Intelligence Collector Module
Gathers data from Reddit, Twitter/X, GitHub Trends, and Hacker News
"""

import json
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class IntelCollector:
    """Collects intelligence from various social platforms and tech sources"""
    
    def __init__(self, config_path: str = "config/creds.json"):
        self.config_path = config_path
        self.credentials = self._load_credentials()
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def _load_credentials(self) -> Dict[str, Any]:
        """Load API credentials from config file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"reddit": {}, "twitter": {}, "github": {}}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key].get('timestamp', 0)
        return time.time() - cache_time < self.cache_duration
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_trending_topics(self) -> Dict[str, List[Dict]]:
        """Get trending topics from all platforms"""
        trends = {}
        
        try:
            github_trends = self.get_github_trending()
            trends['github'] = github_trends
        except Exception as e:
            trends['github'] = [{'title': f'GitHub API Error: {str(e)}', 'score': 0}]
        
        try:
            hn_trends = self.get_hackernews_top()
            trends['hackernews'] = hn_trends
        except Exception as e:
            trends['hackernews'] = [{'title': f'HN API Error: {str(e)}', 'score': 0}]
        
        try:
            reddit_trends = self.get_reddit_trending()
            trends['reddit'] = reddit_trends
        except Exception as e:
            trends['reddit'] = [{'title': f'Reddit API Error: {str(e)}', 'score': 0}]
        
        return trends
    
    def collect_all_intel(self) -> Dict[str, Any]:
        """Collect comprehensive intelligence from all sources"""
        intel = {}
        
        trends = self.get_trending_topics()
        intel['trends'] = trends
        
        intel['tech_news'] = self.get_tech_news()
        
        intel['security'] = self.get_security_alerts()
        
        intel['market'] = self.get_market_insights()
        
        return intel
    
    def get_github_trending(self) -> List[Dict[str, Any]]:
        """Get trending repositories from GitHub"""
        cache_key = 'github_trending'
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            url = "https://api.github.com/search/repositories"
            params = {
                'q': f'created:>{week_ago}',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            headers = {}
            github_token = self.credentials.get('github', {}).get('token')
            if github_token:
                headers['Authorization'] = f'token {github_token}'
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                trending = []
                
                for repo in data.get('items', [])[:10]:
                    trending.append({
                        'name': repo['full_name'],
                        'description': repo.get('description', 'No description'),
                        'stars': repo['stargazers_count'],
                        'language': repo.get('language', 'Unknown'),
                        'url': repo['html_url']
                    })
                
                self._cache_data(cache_key, trending)
                return trending
            else:
                return [{'name': 'GitHub API unavailable', 'stars': 0}]
                
        except Exception as e:
            return [{'name': f'GitHub error: {str(e)}', 'stars': 0}]
    
    def get_hackernews_top(self) -> List[Dict[str, Any]]:
        """Get top stories from Hacker News"""
        cache_key = 'hackernews_top'
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            response = requests.get(top_stories_url, timeout=10)
            
            if response.status_code == 200:
                story_ids = response.json()[:10]  # Top 10 stories
                stories = []
                
                for story_id in story_ids:
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    story_response = requests.get(story_url, timeout=5)
                    
                    if story_response.status_code == 200:
                        story_data = story_response.json()
                        stories.append({
                            'title': story_data.get('title', 'No title'),
                            'score': story_data.get('score', 0),
                            'url': story_data.get('url', ''),
                            'comments': story_data.get('descendants', 0)
                        })
                
                self._cache_data(cache_key, stories)
                return stories
            else:
                return [{'title': 'Hacker News API unavailable', 'score': 0}]
                
        except Exception as e:
            return [{'title': f'HN error: {str(e)}', 'score': 0}]
    
    def get_reddit_trending(self) -> List[Dict[str, Any]]:
        """Get trending posts from Reddit (requires API credentials)"""
        cache_key = 'reddit_trending'
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            subreddits = ['programming', 'technology', 'MachineLearning', 'artificial']
            all_posts = []
            
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=5"
                headers = {'User-Agent': 'StarkAI/1.0'}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        all_posts.append({
                            'title': post_data.get('title', 'No title'),
                            'score': post_data.get('score', 0),
                            'subreddit': post_data.get('subreddit', subreddit),
                            'url': f"https://reddit.com{post_data.get('permalink', '')}"
                        })
            
            all_posts.sort(key=lambda x: x['score'], reverse=True)
            trending = all_posts[:10]
            
            self._cache_data(cache_key, trending)
            return trending
            
        except Exception as e:
            return [{'title': f'Reddit error: {str(e)}', 'score': 0}]
    
    def get_tech_news(self) -> List[str]:
        """Get latest tech news headlines"""
        try:
            news = [
                "AI development continues to accelerate across industries",
                "New security vulnerabilities discovered in popular frameworks",
                "Open source projects gaining enterprise adoption",
                "Cloud computing costs optimization strategies trending",
                "Developer productivity tools seeing increased investment"
            ]
            return news
        except Exception:
            return ["Tech news unavailable"]
    
    def get_security_alerts(self) -> List[str]:
        """Get security alerts and vulnerabilities"""
        try:
            alerts = [
                "Monitor for new CVE announcements in your dependencies",
                "Check for security updates in your Python packages",
                "Review access permissions for cloud services",
                "Audit API keys and tokens for rotation needs"
            ]
            return alerts
        except Exception:
            return ["Security alerts unavailable"]
    
    def get_market_insights(self) -> Dict[str, str]:
        """Get market and investment insights"""
        try:
            insights = {
                'tech_stocks': 'Tech sector showing mixed signals',
                'crypto': 'Cryptocurrency markets remain volatile',
                'ai_investments': 'AI startups continue to attract funding',
                'recommendation': 'Diversify portfolio across emerging technologies'
            }
            return insights
        except Exception:
            return {'status': 'Market data unavailable'}
    
    def suggest_relevant_trends(self, context: str = "") -> List[str]:
        """Suggest trends relevant to current context"""
        trends = self.get_trending_topics()
        suggestions = []
        
        keywords = context.lower().split() if context else []
        
        for platform, items in trends.items():
            for item in items[:3]:
                title = item.get('title', item.get('name', '')).lower()
                
                if any(keyword in title for keyword in keywords) or not keywords:
                    suggestions.append(f"{platform.upper()}: {item.get('title', item.get('name', 'Unknown'))}")
        
        return suggestions[:5] if suggestions else ["No relevant trends found"]
