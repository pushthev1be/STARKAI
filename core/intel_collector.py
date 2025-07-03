import praw
import asyncio
from github import Github
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os

class IntelCollector:
    def __init__(self):
        self.reddit = self._setup_reddit()
        self.github = self._setup_github()
        self.intel_cache = {}
        
    def _setup_reddit(self) -> Optional[praw.Reddit]:
        """Initialize Reddit API client"""
        try:
            return praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent='STARKAI/1.0'
            )
        except Exception as e:
            print(f"Reddit setup failed: {e}")
            return None
            
    def _setup_github(self) -> Optional[Github]:
        """Initialize GitHub API client"""
        try:
            return Github(os.getenv('GITHUB_TOKEN'))
        except Exception as e:
            print(f"GitHub setup failed: {e}")
            return None
            
    async def gather_tech_intelligence(self, topics: List[str]) -> Dict[str, Any]:
        """Gather intelligence from multiple sources"""
        intel = {
            "timestamp": datetime.now().isoformat(),
            "topics": topics,
            "reddit_trends": [],
            "github_trends": [],
            "tech_news": []
        }
        
        if self.reddit is not None:
            intel["reddit_trends"] = await self._get_reddit_trends(topics)
            
        if self.github is not None:
            intel["github_trends"] = await self._get_github_trends(topics)
            
        self.intel_cache[datetime.now().isoformat()] = intel
        return intel
        
    async def _get_reddit_trends(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Get trending topics from Reddit"""
        trends = []
        try:
            if self.reddit is not None:
                for topic in topics:
                    subreddit = self.reddit.subreddit(topic)
                    for post in subreddit.hot(limit=5):
                        trends.append({
                            "title": post.title,
                            "score": post.score,
                            "url": post.url,
                            "subreddit": topic,
                            "created": datetime.fromtimestamp(post.created_utc).isoformat()
                        })
        except Exception as e:
            print(f"Reddit trends error: {e}")
        return trends
        
    async def _get_github_trends(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Get trending repositories from GitHub"""
        trends = []
        try:
            if self.github is not None:
                for topic in topics:
                    repos = self.github.search_repositories(
                        query=f"{topic} language:python",
                        sort="stars",
                        order="desc"
                    )
                    for repo in repos[:5]:
                        trends.append({
                            "name": repo.full_name,
                            "description": repo.description,
                            "stars": repo.stargazers_count,
                            "language": repo.language,
                            "url": repo.html_url,
                            "updated": repo.updated_at.isoformat()
                        })
        except Exception as e:
            print(f"GitHub trends error: {e}")
        return trends
