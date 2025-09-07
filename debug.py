diff --git a/debug.py b/debug.py
index e7c838be84210ee12ef0812bb9c7dfba92f0873b..9402fb10996790a49d31d7d5b3b86e34499dd114 100644
--- a/debug.py
+++ b/debug.py
@@ -137,52 +137,53 @@ def check_ports():
         result = s.connect_ex(('localhost', port))
         if result == 0:
             print(f"⚠️  Port {port} is already in use")
             return False
         else:
             print(f"✅ Port {port} is available")
             return True

 def run_basic_import_test():
     """Test basic imports."""
     try:
         sys.path.append(str(Path(__file__).parent / "backend"))
         from backend.app import app
         print("✅ App imports successfully")
         return True
     except Exception as e:
         print(f"❌ App import failed: {e}")
         return False

 def suggest_fixes():
     """Suggest common fixes."""
     print("\n🔧 Common fixes:")
     print("1. Install dependencies: cd backend && pip install -r requirements.txt")
     print("2. Run in simple mode: USE_DATABASE=false python -m uvicorn app:app --reload")
     print("3. Enable database mode: USE_DATABASE=true python -m uvicorn app:app --reload")
-    print("4. Check logs for detailed errors")
-    print("5. Ensure you're in a virtual environment")
+    print("4. On macOS run ./start-mac.sh or double-click MindForge.app")
+    print("5. Check logs for detailed errors")
+    print("6. Ensure you're in a virtual environment")

 def main():
     """Main debug function."""
     print("🔍 MindForge Casey - Debug Check")
     print("=" * 40)

     checks = [
         ("Python Version", check_python_version),
         ("File Structure", check_file_structure),
         ("Dependencies", check_dependencies),
         ("Database Setup", check_database_setup),
         ("Environment", check_environment),
         ("Port Availability", check_ports),
         ("Basic Import", run_basic_import_test),
     ]

     results = []
     for name, check_func in checks:
         print(f"\n{name}:")
         try:
             result = check_func()
             results.append(result)
         except Exception as e:
             print(f"❌ {name} check failed: {e}")
             results.append(False)
