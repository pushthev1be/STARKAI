"""
Intelligence Collector - Collects data from Reddit, Twitter, GitHub
Provides unified interface for external data ingestion and analysis
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False

try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

import requests

class IntelligenceCollector:
    """Collects and analyzes data from external sources"""
    
    def __init__(self):
        self.config = self._load_config()
        self.reddit_client = None
        self.twitter_client = None
        self.github_client = None
        self.data_cache = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from creds.json"""
        config_path = Path(__file__).parent.parent / "config" / "creds.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"reddit": {}, "twitter": {}, "github": {}}
    
    def initialize(self):
        """Initialize all API connections"""
        print("Initializing Intelligence Collector...")
        
        self._init_reddit()
        self._init_twitter()
        self._init_github()
        
        print("✓ Intelligence Collector initialized")
    
    def _init_reddit(self):
        """Initialize Reddit API connection"""
        if not REDDIT_AVAILABLE:
            print("⚠ Reddit (praw) library not available")
            return
            
        reddit_config = self.config.get("reddit", {})
        client_id = os.getenv('REDDIT_CLIENT_ID') or reddit_config.get('client_id')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET') or reddit_config.get('client_secret')
        user_agent = reddit_config.get('user_agent', 'STARKAI:1.0.0 (by /u/starkai)')
        
        if client_id and client_secret:
            try:
                self.reddit_client = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                print("✓ Reddit API connection established")
            except Exception as e:
                print(f"⚠ Reddit API error: {e}")
        else:
            print("⚠ Reddit API credentials not found")
    
    def _init_twitter(self):
        """Initialize Twitter API connection"""
        if not TWITTER_AVAILABLE:
            print("⚠ Twitter (tweepy) library not available")
            return
            
        twitter_config = self.config.get("twitter", {})
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN') or twitter_config.get('bearer_token')
        
        if bearer_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=bearer_token)
                print("✓ Twitter API connection established")
            except Exception as e:
                print(f"⚠ Twitter API error: {e}")
        else:
            print("⚠ Twitter API credentials not found")
    
    def _init_github(self):
        """Initialize GitHub API connection"""
        if not GITHUB_AVAILABLE:
            print("⚠ GitHub (PyGithub) library not available")
            return
            
        github_config = self.config.get("github", {})
        token = os.getenv('GITHUB_TOKEN') or github_config.get('token')
        
        if token:
            try:
                self.github_client = Github(token)
                print("✓ GitHub API connection established")
            except Exception as e:
                print(f"⚠ GitHub API error: {e}")
        else:
            print("⚠ GitHub API credentials not found")
    
    def collect_reddit_data(self, subreddit_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Collect data from Reddit subreddit"""
        if not self.reddit_client:
            return []
        
        try:
            subreddit = self.reddit_client.subreddit(subreddit_name)
            posts = []
            
            for submission in subreddit.hot(limit=limit):
                posts.append({
                    "id": submission.id,
                    "title": submission.title,
                    "author": str(submission.author),
                    "score": submission.score,
                    "url": submission.url,
                    "created_utc": submission.created_utc,
                    "num_comments": submission.num_comments,
                    "selftext": submission.selftext[:500] if submission.selftext else "",
                    "subreddit": subreddit_name
                })
            
            self.data_cache[f"reddit_{subreddit_name}"] = posts
            return posts
            
        except Exception as e:
            print(f"Reddit collection error: {e}")
            return []
    
    def collect_twitter_data(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Collect data from Twitter search"""
        if not self.twitter_client:
            return []
        
        try:
            tweets = self.twitter_client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations']
            )
            
            if not tweets.data:
                return []
            
            tweet_data = []
            for tweet in tweets.data:
                tweet_data.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": str(tweet.created_at),
                    "retweet_count": tweet.public_metrics.get('retweet_count', 0),
                    "like_count": tweet.public_metrics.get('like_count', 0),
                    "reply_count": tweet.public_metrics.get('reply_count', 0),
                    "quote_count": tweet.public_metrics.get('quote_count', 0)
                })
            
            self.data_cache[f"twitter_{query}"] = tweet_data
            return tweet_data
            
        except Exception as e:
            print(f"Twitter collection error: {e}")
            return []
    
    def collect_github_data(self, repo_name: str) -> Dict[str, Any]:
        """Collect data from GitHub repository"""
        if not self.github_client:
            return {}
        
        try:
            repo = self.github_client.get_repo(repo_name)
            
            commits = []
            for commit in repo.get_commits()[:10]:
                commits.append({
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": str(commit.commit.author.date)
                })
            
            issues = []
            for issue in repo.get_issues(state='open')[:10]:
                issues.append({
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": str(issue.created_at),
                    "user": issue.user.login
                })
            
            repo_data = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "created_at": str(repo.created_at),
                "updated_at": str(repo.updated_at),
                "commits": commits,
                "issues": issues
            }
            
            self.data_cache[f"github_{repo_name}"] = repo_data
            return repo_data
            
        except Exception as e:
            print(f"GitHub collection error: {e}")
            return {}
    
    def analyze_sentiment(self, text_data: List[str]) -> Dict[str, float]:
        """Simple sentiment analysis on collected text"""
        positive_words = ['good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'best', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'sucks', 'disappointing']
        
        total_texts = len(text_data)
        if total_texts == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        
        positive_count = 0
        negative_count = 0
        
        for text in text_data:
            text_lower = text.lower()
            if any(word in text_lower for word in positive_words):
                positive_count += 1
            elif any(word in text_lower for word in negative_words):
                negative_count += 1
        
        neutral_count = total_texts - positive_count - negative_count
        
        return {
            "positive": positive_count / total_texts,
            "negative": negative_count / total_texts,
            "neutral": neutral_count / total_texts
        }
    
    def get_trending_topics(self, source: str = "all") -> List[str]:
        """Get trending topics from various sources"""
        topics = []
        
        if source in ["all", "reddit"] and self.reddit_client:
            try:
                for submission in self.reddit_client.subreddit("all").hot(limit=5):
                    topics.append(f"Reddit: {submission.title}")
            except:
                pass
        
        if source in ["all", "github"] and self.github_client:
            try:
                trending_repos = self.github_client.search_repositories(
                    query="created:>2024-01-01", 
                    sort="stars", 
                    order="desc"
                )
                for repo in trending_repos[:3]:
                    topics.append(f"GitHub: {repo.name}")
            except:
                pass
        
        return topics
    
    def export_data(self, filename: str, data_type: str = "all"):
        """Export collected data to file"""
        export_data = {}
        
        if data_type == "all":
            export_data = self.data_cache
        else:
            export_data = {k: v for k, v in self.data_cache.items() if data_type in k}
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Export error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get collector status"""
        return {
            "reddit_connected": self.reddit_client is not None,
            "twitter_connected": self.twitter_client is not None,
            "github_connected": self.github_client is not None,
            "cached_datasets": len(self.data_cache),
            "available_sources": {
                "reddit": REDDIT_AVAILABLE,
                "twitter": TWITTER_AVAILABLE,
                "github": GITHUB_AVAILABLE
            }
        }
