"""
ARDA Agent - Quick Start Guide
Run this file for a 5-minute demonstration
"""

import sys
import os
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import ARDAAgent


def print_banner():
    """Print welcome banner"""
    print("\n")
    print("=" * 70)
    print("  🤖 ARDA - AUTONOMOUS RESEARCH & DECISION AGENT")
    print("  Production-Ready Agentic AI with Jac/Jaseci")
    print("=" * 70)
    print()


def run_demo():
    """Run demonstration with preset queries"""
    print_banner()

    print("📋 Quick Start Demo - 5 Minutes\n")

    # Initialize agent
    print("⏳ Initializing ARDA Agent...")
    try:
        agent = ARDAAgent()
        print("✅ Agent initialized successfully\n")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("\n⚠️  Make sure you have:")
        print("   1. Set GROQ_API_KEY in .env file")
        print("   2. Installed all requirements: pip install -r requirements.txt")
        print("   3. Have internet connection for web search")
        return

    # Demo queries
    demo_queries = [
        {
            "query": "What are the key developments in AI in 2024-2025?",
            "description": "AI Landscape Analysis",
            "depth": "standard"
        },
        {
            "query": "Should I invest in renewable energy stocks?",
            "description": "Investment Decision",
            "depth": "standard"
        },
    ]

    # Run first query as demo
    print("🚀 Running First Query as Demo...\n")
    demo = demo_queries[0]

    print(f"📊 Query: {demo['query']}")
    print(f"📈 Depth: {demo['depth']}")
    print(f"⏱️  Estimated time: 30-45 seconds\n")

    try:
        result = agent.research(demo['query'], depth=demo['depth'])

        print("\n✨ Demo Complete! Summary:\n")
        print(f"  Session ID: {result['session_id']}")
        print(f"  Execution Time: {result['execution_time']:.2f}s")
        print(f"  Tasks Completed: {result['phases']['execution']['tasks_completed']}/{result['phases']['execution']['tasks_total']}")
        print(f"  Success Rate: {result['phases']['execution']['success_rate']:.0f}%")

        print("\n📋 Final Report Preview:")
        print(f"  {result['final_report']['recommendation'][:150]}...")

        print("\n" + "=" * 70)
        print("🎉 Demo Complete!")
        print("=" * 70)

        print("\n💡 Next Steps:\n")
        print("  1. Try CLI: python main.py")
        print("     - Runs with interactive queries")
        print("  2. Start API Server: python app.py")
        print("     - Provides REST endpoints at http://localhost:8000")
        print("  3. Use Streamlit UI: streamlit run frontend/app.py")
        print("     - Beautiful interactive dashboard")
        print("  4. Check memory: curl http://localhost:8000/memory/stats")
        print("     - View stored findings and sessions")

        print("\n📚 Try These Queries:")
        print("  • 'What is the latest news about SpaceX?'")
        print("  • 'Compare Python vs Go for backend development'")
        print("  • 'What are risks of cryptocurrency investment?'")

        print("\n🔍 Explore the Code:")
        print("  • main.py - Core agent orchestration")
        print("  • tools/*.py - LLM, search, memory modules")
        print("  • jac_app/*.jac - Agent walkers and graph structure")
        print("  • api/routes.py - FastAPI endpoints")

        print("\n📖 Documentation:")
        print("  • README.md - Full documentation")
        print("  • API Docs: http://localhost:8000/docs (after starting server)")

        print()

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("\n🆘 Troubleshooting:")
        print("  1. Check Groq API key is valid")
        print("  2. Verify internet connection")
        print("  3. Check logs for detailed errors")
        print("  4. Read README.md troubleshooting section")


def interactive_mode():
    """Run interactive query mode"""
    print_banner()

    try:
        agent = ARDAAgent()

        print("🎯 Interactive Mode - Enter queries (type 'exit' to quit)\n")

        while True:
            query = input("📝 Enter research query: ").strip()

            if query.lower() == 'exit':
                print("\n👋 Goodbye!")
                break

            if not query:
                print("⚠️  Please enter a query\n")
                continue

            depth = input("📊 Research depth (standard/deep/expert) [standard]: ").strip() or "standard"

            if depth not in ["standard", "deep", "expert"]:
                depth = "standard"

            try:
                result = agent.research(query, depth=depth)
                print("\n✅ Research completed successfully!\n")

            except KeyboardInterrupt:
                print("\n⚠️  Interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_mode()
        elif sys.argv[1] == "--help":
            print("""
ARDA - Autonomous Research & Decision Agent

Usage:
  python quickstart.py              Run 5-minute demo
  python quickstart.py --interactive  Interactive query mode
  python quickstart.py --help         Show this help
  
  python main.py                    Run CLI agent
  python app.py                     Run FastAPI server
  streamlit run frontend/app.py     Run web UI
            """)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for available options")
    else:
        run_demo()


if __name__ == "__main__":
    main()
