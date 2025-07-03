import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class DataSource:
    name: str
    url: str
    headers: Dict[str, str]
    rate_limit: float


class EfficientIntelCollector:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, tuple] = {}
        self._rate_limiters: Dict[str, float] = {}
        
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    @lru_cache(maxsize=128)
    def _get_data_source_config(self, source: str) -> Optional[DataSource]:
        configs = {
            'reddit': DataSource(
                'reddit', 
                'https://api.reddit.com', 
                {'User-Agent': 'STARKAI/1.0'}, 
                1.0
            ),
            'twitter': DataSource(
                'twitter', 
                'https://api.twitter.com', 
                {'Authorization': 'Bearer TOKEN'}, 
                0.5
            ),
            'github': DataSource(
                'github', 
                'https://api.github.com', 
                {'Accept': 'application/vnd.github.v3+json'}, 
                0.1
            )
        }
        return configs.get(source)

    async def collect_data_batch(self, sources: List[str], queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        if not self._session:
            raise RuntimeError("Collector must be used as async context manager")
            
        tasks = []
        for source in sources:
            for query in queries:
                tasks.append(self._collect_single(source, query))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._organize_results(results, sources, queries)

    async def _collect_single(self, source: str, query: str) -> Dict[str, Any]:
        cache_key = f"{source}:{query}"
        
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < 300:
                return {'source': source, 'query': query, 'data': data, 'cached': True}

        await self._respect_rate_limit(source)
        
        config = self._get_data_source_config(source)
        if not config:
            return {'source': source, 'query': query, 'error': 'Unknown source', 'cached': False}
            
        try:
            params = {'q': query, 'limit': 25}
            if self._session:
                async with self._session.get(
                    f"{config.url}/search", 
                    headers=config.headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._cache[cache_key] = (data, time.time())
                        return {'source': source, 'query': query, 'data': data, 'cached': False}
                    else:
                        return {
                            'source': source, 
                            'query': query, 
                            'error': f'HTTP {response.status}', 
                            'cached': False
                        }
            else:
                return {'source': source, 'query': query, 'error': 'No session available', 'cached': False}
        except Exception as e:
            return {'source': source, 'query': query, 'error': str(e), 'cached': False}

    async def _respect_rate_limit(self, source: str):
        config = self._get_data_source_config(source)
        if not config:
            return
            
        last_request = self._rate_limiters.get(source, 0)
        time_since_last = time.time() - last_request
        
        if time_since_last < config.rate_limit:
            await asyncio.sleep(config.rate_limit - time_since_last)
        
        self._rate_limiters[source] = time.time()

    def _organize_results(self, results: List, sources: List[str], queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        organized = {source: [] for source in sources}
        
        for result in results:
            if isinstance(result, dict) and 'source' in result:
                source = result['source']
                if source in organized:
                    organized[source].append(result)
        
        return organized

    def clear_cache(self):
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        total_entries = len(self._cache)
        fresh_entries = sum(
            1 for _, timestamp in self._cache.values() 
            if time.time() - timestamp < 300
        )
        return {
            'total_entries': total_entries,
            'fresh_entries': fresh_entries,
            'stale_entries': total_entries - fresh_entries
        }


async def main():
    async with EfficientIntelCollector() as collector:
        results = await collector.collect_data_batch(
            sources=['reddit', 'twitter', 'github'],
            queries=['AI', 'machine learning', 'python']
        )
        
        for source, data_list in results.items():
            print(f"\n{source.upper()} Results:")
            for item in data_list:
                if 'error' in item:
                    print(f"  Error for '{item['query']}': {item['error']}")
                else:
                    cached_status = "cached" if item.get('cached') else "fresh"
                    print(f"  Query '{item['query']}': {len(item.get('data', {}))} results ({cached_status})")
        
        print(f"\nCache Stats: {collector.get_cache_stats()}")


if __name__ == "__main__":
    asyncio.run(main())
