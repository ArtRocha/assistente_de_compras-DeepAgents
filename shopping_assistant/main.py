import asyncio
import sys
import json
from shopping_assistant.agents.orchestrator import OrchestratorAgent

async def main():
    if len(sys.argv) < 2:
        query = "iPhone 13"
    else:
        query = " ".join(sys.argv[1:])
        
    print(f"🚀 Shopping Assistant - Query: '{query}'")
    
    orchestrator = OrchestratorAgent()
    
    try:
        results = await orchestrator.process_query(query)
        
        print("\n--- Top Recommended Products ---")
        print(json.dumps(results, indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
