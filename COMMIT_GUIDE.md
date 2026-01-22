# Git Commit Guide

## Files to COMMIT ✅ (Production-ready)

### Core Project Files:
```
✅ README.md                    # Main documentation
✅ QUICKSTART.md               # Quick start guide
✅ LICENSE                      # MIT license
✅ requirements.txt            # Python dependencies
✅ .gitignore                  # Git ignore rules
✅ .env.example                # Environment template (NO SECRETS)
✅ export_assets.py            # Main export script
✅ test_connection.py          # Connection tester
✅ examples/filter_examples.md # Filter examples
```

## Files to SKIP ❌ (Debug/Testing Only)

### Debug Scripts (created during troubleshooting):
```
❌ quick_test.py               # Quick debugging test
❌ diagnose_access.py          # API access diagnostic
❌ verify_endpoint.py          # Endpoint verification
❌ test_working.py             # Test with hardcoded creds
❌ export_all_assets.py        # Hardcoded credentials version
❌ manual_curl_test.sh         # Manual curl test
```

## Files NEVER COMMIT 🚫 (Secrets/Output)

### Already in .gitignore:
```
🚫 .env                        # YOUR API CREDENTIALS!
🚫 *.json                      # Export output files
🚫 __pycache__/               # Python cache
🚫 *.pyc                       # Python compiled
```

---

## Quick Commit Commands

### Initialize Git:
```bash
cd crowdstrike-asset-export
git init
```

### Stage Production Files Only:
```bash
git add README.md
git add QUICKSTART.md
git add LICENSE
git add requirements.txt
git add .gitignore
git add .env.example
git add export_assets.py
git add test_connection.py
git add examples/filter_examples.md
```

### Commit:
```bash
git commit -m "Initial commit: CrowdStrike Cloud Security Assets Exporter

- Export 2M+ cloud security assets using proper API pagination
- Token-based pagination to bypass 10K offset limit
- Batch processing for entity details (100 per request)
- Complete documentation and examples
- Handles large datasets efficiently"
```

### Add Remote & Push:
```bash
git remote add origin https://github.com/yannhowe/crowdstrike-asset-export.git
git branch -M main
git push -u origin main
```

---

## Clean Up Debug Files (Optional)

If you want to remove the debug files:
```bash
rm quick_test.py
rm diagnose_access.py
rm verify_endpoint.py
rm test_working.py
rm export_all_assets.py
rm manual_curl_test.sh
```

Or keep them locally for future debugging (they won't be committed).