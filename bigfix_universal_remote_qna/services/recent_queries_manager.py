from typing import List
import json


class RecentQueriesManager:
    """Manages recent queries using ConfigManager"""
    
    def __init__(self, config_manager, max_queries: int = 10):
        self.config_manager = config_manager
        self.max_queries = max_queries
    
    def get_recent_queries(self) -> List[str]:
        """Get list of recent queries"""
        try:
            queries_json = self.config_manager.get_setting("recent_queries")
            return json.loads(queries_json) if queries_json else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_query(self, query: str):
        """Add a query to recent queries"""
        if not query.strip():
            return
        
        queries = self.get_recent_queries()
        
        # Remove if already exists
        if query in queries:
            queries.remove(query)
        
        # Add to beginning
        queries.insert(0, query)
        
        # Keep only max_queries
        queries = queries[:self.max_queries]
        
        # Save back to config
        queries_json = json.dumps(queries)
        try:
            self.config_manager.define_setting(
                "recent_queries", False, queries_json, str,
                "JSON array of recent queries (max 10)"
            )
        except:
            pass