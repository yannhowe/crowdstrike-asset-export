#!/usr/bin/env python3
"""
Simple test script to verify CrowdStrike API connectivity.
Run this before using the main export script.
"""

import os
import sys
from dotenv import load_dotenv
from falconpy import CloudSecurityAssets


def test_connection():
    """Test API connection and credentials."""
    print("="*60)
    print("CrowdStrike API Connection Test")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    client_id = os.getenv('CROWDSTRIKE_CLIENT_ID')
    client_secret = os.getenv('CROWDSTRIKE_CLIENT_SECRET')
    base_url = os.getenv('CROWDSTRIKE_BASE_URL', 'https://api.crowdstrike.com')
    
    # Check credentials
    print("\n1. Checking credentials...")
    if not client_id:
        print("   ✗ CROWDSTRIKE_CLIENT_ID not set")
        return False
    if not client_secret:
        print("   ✗ CROWDSTRIKE_CLIENT_SECRET not set")
        return False
    
    print(f"   ✓ Client ID: {client_id[:8]}...")
    print(f"   ✓ Base URL: {base_url}")
    
    # Test authentication
    print("\n2. Testing authentication...")
    try:
        falcon = CloudSecurityAssets(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url
        )
        print("   ✓ Authentication successful")
    except Exception as e:
        print(f"   ✗ Authentication failed: {e}")
        return False
    
    # Test API call
    print("\n3. Testing API call (querying first 10 resources)...")
    try:
        response = falcon.query_assets(limit=10)
        
        if response['status_code'] == 200:
            body = response['body']
            ids = body.get('resources', [])
            print(f"   ✓ API call successful")
            print(f"   ✓ Retrieved {len(ids)} resource IDs")
            
            # Show sample IDs
            if ids:
                print(f"   ✓ Sample ID: {ids[0]}")
        else:
            print(f"   ✗ API call failed with status {response['status_code']}")
            print(f"   Error: {response['body']}")
            return False
            
    except Exception as e:
        print(f"   ✗ API call failed: {e}")
        return False
    
    # Summary
    print("\n" + "="*60)
    print("✓ All tests passed! You're ready to export assets.")
    print("="*60)
    print("\nNext steps:")
    print("  python export_assets.py --filter \"cloud_provider:'aws'\"")
    print("  python export_assets.py --help")
    
    return True


if __name__ == '__main__':
    try:
        success = test_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)