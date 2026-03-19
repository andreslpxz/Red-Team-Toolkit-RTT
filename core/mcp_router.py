import aiohttp
import asyncio
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from utils.logger import Logger
from utils.config import config
import datetime

class MCPRouter:
    """
    Custom Context Protocol Router.
    Connects to various data sources (APIs, Databases, Filesystem)
    to provide context for the security agent.
    """
    def __init__(self):
        self.shodan_key = os.getenv("SHODAN_API_KEY")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.db_path = config.db_path
        self.cache = {}
        self.rate_limits = {
            "nvd": {"last_call": 0, "interval": 6},  # NVD: 5 calls/30s = 6s interval
            "github": {"last_call": 0, "interval": 2},
        }

    async def _wait_for_rate_limit(self, source: str):
        """
        Enforces rate limits for external APIs.
        """
        if source in self.rate_limits:
            now = datetime.datetime.now().timestamp()
            elapsed = now - self.rate_limits[source]["last_call"]
            wait_time = self.rate_limits[source]["interval"] - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.rate_limits[source]["last_call"] = datetime.datetime.now().timestamp()

    async def fetch_from_api(self, source: str, query: str) -> List[Dict[str, Any]]:
        """
        Routes queries to appropriate external APIs with fallback logic.
        """
        source = source.lower()
        try:
            if source == "nvd":
                return await self._query_nvd(query)
            elif source == "github":
                return await self._query_github(query)
            elif source == "shodan":
                if self.shodan_key:
                    return await self._query_shodan(query)
                else:
                    Logger.warning("Shodan API key not found. Falling back to NVD.")
                    return await self._query_nvd(query)
            elif source == "mitre":
                return await self._scrape_mitre(query)
            else:
                return [{"error": f"API source '{source}' not recognized."}]
        except Exception as e:
            Logger.error(f"Error fetching from API {source}: {e}")
            return [{"error": str(e)}]

    async def _query_nvd(self, query: str) -> List[Dict[str, Any]]:
        """
        Queries the NVD CVE API.
        """
        await self._wait_for_rate_limit("nvd")
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    for vuln in data.get("vulnerabilities", []):
                        cve = vuln.get("cve", {})
                        results.append({
                            "id": cve.get("id"),
                            "description": cve.get("descriptions", [{}])[0].get("value"),
                            "severity": cve.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseSeverity"),
                            "source": "nvd"
                        })
                    return results
                else:
                    Logger.error(f"NVD API returned status {resp.status}")
                    return []

    async def _query_github(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches GitHub for POCs.
        """
        await self._wait_for_rate_limit("github")
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        url = f"https://api.github.com/search/repositories?q={query}+exploit+POC"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    for repo in data.get("items", [])[:5]: # Limit to top 5
                        results.append({
                            "name": repo.get("full_name"),
                            "url": repo.get("html_url"),
                            "description": repo.get("description"),
                            "source": "github_poc"
                        })
                    return results
                else:
                    return []

    async def _query_shodan(self, query: str) -> List[Dict[str, Any]]:
        """
        Queries Shodan (simplified).
        """
        url = f"https://api.shodan.io/shodan/host/search?key={self.shodan_key}&query={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = []
                    for host in data.get("matches", [])[:5]:
                        results.append({
                            "ip": host.get("ip_str"),
                            "ports": host.get("ports"),
                            "org": host.get("org"),
                            "source": "shodan"
                        })
                    return results
                else:
                    return []

    async def _scrape_mitre(self, query: str) -> List[Dict[str, Any]]:
        """
        Scrapes MITRE CVE page for info.
        """
        url = f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    soup = BeautifulSoup(await resp.text(), 'html.parser')
                    table = soup.find('div', {'id': 'GeneratedTable'})
                    if table:
                        description = table.find_all('td')[2].get_text(strip=True)
                        return [{"id": query, "description": description, "source": "mitre"}]
        return []

    def fetch_from_db(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetches findings from the local SQLite database.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT target, type, data, timestamp FROM findings WHERE data LIKE ? OR target LIKE ?", (f"%{query}%", f"%{query}%"))
            rows = cursor.fetchall()
            conn.close()
            return [{"target": r[0], "type": r[1], "data": r[2], "timestamp": r[3], "source": "local_db"} for r in rows]
        except Exception as e:
            Logger.error(f"Local DB query error: {e}")
            return []

    def fetch_filesystem(self, path: str) -> List[str]:
        """
        Lists files in /space for contextual awareness.
        """
        try:
            full_path = os.path.join("space", path)
            if os.path.exists(full_path):
                return os.listdir(full_path)
            return []
        except Exception as e:
            Logger.error(f"Filesystem fetch error: {e}")
            return []

    async def query(self, query: str, source: str = "all") -> Dict[str, Any]:
        """
        Universal query method that aggregates multiple sources.
        """
        results = {}
        if source == "all" or source == "nvd":
            results["nvd"] = await self.fetch_from_api("nvd", query)
        if source == "all" or source == "github":
            results["github"] = await self.fetch_from_api("github", query)
        if source == "all" or source == "mitre":
            results["mitre"] = await self.fetch_from_api("mitre", query)
        if source == "all" or source == "local":
            results["local_db"] = self.fetch_from_db(query)

        return results

# Global instance
mcp_router = MCPRouter()
