"""Quick setup verification script."""
import sys

def check_imports():
    """Check if all required packages can be imported."""
    print("Checking Python package imports...")
    try:
        import fastapi
        print(f"  ✓ FastAPI {fastapi.__version__}")
    except ImportError:
        print("  ✗ FastAPI not installed")
        return False
    
    try:
        import sqlalchemy
        print(f"  ✓ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError:
        print("  ✗ SQLAlchemy not installed")
        return False
    
    try:
        import sentence_transformers
        print(f"  ✓ sentence-transformers installed")
    except ImportError:
        print("  ✗ sentence-transformers not installed")
        return False
    
    try:
        import pgvector
        print(f"  ✓ pgvector installed")
    except ImportError:
        print("  ✗ pgvector not installed")
        return False
    
    return True


def check_app_structure():
    """Check if app structure is correct."""
    print("\nChecking application structure...")
    import os
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "app/models.py",
        "app/schemas.py",
        "app/api/v1/memory.py",
        "app/services/memory.py",
        "app/services/embedding.py",
        "app/services/auth.py",
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} missing")
            all_present = False
    
    return all_present


def check_config():
    """Check if configuration can be loaded."""
    print("\nChecking configuration...")
    try:
        from app.config import settings
        print(f"  ✓ Configuration loaded")
        print(f"    Database URL: {settings.database_url[:30]}...")
        print(f"    Embedding Model: {settings.embedding_model}")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


def main():
    """Run all checks."""
    print("CASM Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Package Imports", check_imports),
        ("App Structure", check_app_structure),
        ("Configuration", check_config),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("Summary:")
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All checks passed! System is ready.")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

