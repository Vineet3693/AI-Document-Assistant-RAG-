"""
DocuMind AI - Main Application Entry Point
Version: 3.0.0 Enterprise

Usage:
    python main.py --mode frontend    # Start Streamlit UI
    python main.py --mode api         # Start FastAPI server
    python main.py --mode both        # Start both
    python main.py --mode test        # Run tests
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def load_environment():
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Loaded environment from .env")
    else:
        print("⚠ No .env file found. Using system environment variables.")
        print("  Copy .env.example to .env and configure your API keys.")


def setup_logging():
    """Initialize logging system."""
    from src.utils.logger import setup_logging
    
    log_config = project_root / "config" / "logging.yaml"
    if log_config.exists():
        setup_logging(str(log_config))
        print("✓ Logging configured")
    else:
        setup_logging()
        print("✓ Logging configured (default)")


def start_frontend():
    """Start Streamlit frontend."""
    print("\n🚀 Starting DocuMind AI Frontend...")
    print("=" * 60)
    
    try:
        import streamlit.web.cli as stcli
        from streamlit import config
        
        # Set configuration
        config.set_option("server.port", 8501)
        config.set_option("server.address", "0.0.0.0")
        config.set_option("browser.gatherUsageStats", False)
        
        frontend_app = project_root / "frontend" / "app.py"
        
        if not frontend_app.exists():
            print("❌ Frontend app not found at frontend/app.py")
            return False
        
        sys.argv = ["streamlit", "run", str(frontend_app)]
        stcli.main()
        return True
        
    except ImportError as e:
        print(f"❌ Streamlit not installed: {e}")
        print("   Install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False


def start_api():
    """Start FastAPI backend."""
    print("\n🚀 Starting DocuMind AI API Server...")
    print("=" * 60)
    
    try:
        import uvicorn
        
        api_app = project_root / "api" / "app.py"
        
        if not api_app.exists():
            print("❌ API app not found at api/app.py")
            return False
        
        # Import and run
        sys.path.insert(0, str(project_root / "api"))
        from app import app
        
        uvicorn.run(
            app,
            host=os.getenv("APP_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_PORT", 8000)),
            reload=os.getenv("DEBUG", "false").lower() == "true",
        )
        return True
        
    except ImportError as e:
        print(f"❌ FastAPI or uvicorn not installed: {e}")
        print("   Install with: pip install fastapi uvicorn")
        return False
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return False


def run_tests():
    """Run test suite."""
    print("\n🧪 Running DocuMind AI Tests...")
    print("=" * 60)
    
    try:
        import pytest
        
        test_dir = project_root / "tests"
        
        if not test_dir.exists():
            print("❌ Test directory not found")
            return False
        
        pytest.main([
            str(test_dir),
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
        ])
        return True
        
    except ImportError as e:
        print(f"❌ pytest not installed: {e}")
        print("   Install with: pip install pytest pytest-asyncio")
        return False


def show_info():
    """Show application information."""
    print("\n" + "=" * 60)
    print("  📄 DocuMind AI - Industry Grade Document Assistant")
    print("  Version: 3.0.0 Enterprise")
    print("=" * 60)
    
    print("\n📋 Available Modes:")
    print("  --mode frontend   Start Streamlit web interface (port 8501)")
    print("  --mode api        Start FastAPI REST API (port 8000)")
    print("  --mode both       Start both frontend and API")
    print("  --mode test       Run test suite")
    print("  --mode info       Show this information")
    
    print("\n🔧 Quick Start:")
    print("  1. Copy .env.example to .env")
    print("  2. Add your API keys (OPENAI_API_KEY, etc.)")
    print("  3. Install dependencies: pip install -r requirements.txt")
    print("  4. Run: python main.py --mode frontend")
    
    print("\n📚 Documentation:")
    print("  - API Docs: http://localhost:8000/docs (when API is running)")
    print("  - Frontend: http://localhost:8501 (when frontend is running)")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="DocuMind AI - Industry Grade Document Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        default="info",
        choices=["frontend", "api", "both", "test", "info"],
        help="Application mode to run",
    )
    
    args = parser.parse_args()
    
    print("\n" + "🤖" * 30)
    print("  DocuMind AI v3.0.0 Enterprise")
    print("🤖" * 30 + "\n")
    
    # Load environment
    load_environment()
    
    # Setup logging
    setup_logging()
    
    # Run based on mode
    if args.mode == "info":
        show_info()
    
    elif args.mode == "frontend":
        success = start_frontend()
        sys.exit(0 if success else 1)
    
    elif args.mode == "api":
        success = start_api()
        sys.exit(0 if success else 1)
    
    elif args.mode == "both":
        import multiprocessing
        
        print("\n🚀 Starting both API and Frontend...")
        
        # Start API in separate process
        api_process = multiprocessing.Process(target=start_api)
        api_process.start()
        
        # Start frontend in main process
        try:
            import time
            time.sleep(2)  # Wait for API to start
            start_frontend()
        finally:
            api_process.terminate()
            api_process.join()
    
    elif args.mode == "test":
        success = run_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
