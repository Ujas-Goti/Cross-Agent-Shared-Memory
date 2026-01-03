"""Simple example client for CASM API."""
import requests
import json

# CASM API configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "test-api-key-change-in-production"  # Change this to match your .env

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def create_memory(content: str, metadata: dict = None, created_by: str = None):
    """Create a new memory item."""
    url = f"{API_BASE_URL}/memory"
    data = {
        "content": content,
        "metadata": metadata or {},
        "created_by": created_by
    }
    
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def get_memory(memory_id: str):
    """Get a memory item by ID."""
    url = f"{API_BASE_URL}/memory/{memory_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def search_memories(query: str, limit: int = 10):
    """Search memories semantically."""
    url = f"{API_BASE_URL}/memory/search"
    data = {
        "query": query,
        "limit": limit,
        "threshold": 0.7
    }
    
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def list_memories(skip: int = 0, limit: int = 10):
    """List all memories."""
    url = f"{API_BASE_URL}/memory"
    params = {"skip": skip, "limit": limit}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print("CASM Example Client")
    print("=" * 50)
    
    # Example 1: Create a memory
    print("\n1. Creating a memory...")
    memory1 = create_memory(
        content="The user prefers dark mode for all applications.",
        metadata={"category": "preference", "priority": "high"},
        created_by="Agent1"
    )
    print(f"Created memory: {memory1['id']}")
    print(f"Content: {memory1['content']}")
    
    # Example 2: Create another memory
    print("\n2. Creating another memory...")
    memory2 = create_memory(
        content="The project deadline is next Friday.",
        metadata={"category": "task", "priority": "urgent"},
        created_by="Agent2"
    )
    print(f"Created memory: {memory2['id']}")
    
    # Example 3: Search memories
    print("\n3. Searching for memories about preferences...")
    results = search_memories("user preferences", limit=5)
    print(f"Found {results['count']} results:")
    for result in results['results']:
        print(f"  - {result['content'][:60]}...")
    
    # Example 4: List all memories
    print("\n4. Listing all memories...")
    all_memories = list_memories(limit=10)
    print(f"Total memories: {len(all_memories)}")
    for mem in all_memories:
        print(f"  - [{mem['id']}] {mem['content'][:50]}...")
    
    print("\n" + "=" * 50)
    print("Example completed!")

