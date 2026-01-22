#!/usr/bin/env python3
"""
CrowdStrike Cloud Security Assets Exporter

Exports large datasets (2M+ records) from CrowdStrike using proper pagination.
Uses token-based pagination to bypass 10,000 offset limit.
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Try to import dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

from falconpy import CloudSecurityAssets


class AssetExporter:
    """Handles exporting CrowdStrike cloud security assets."""
    
    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api.crowdstrike.com"):
        """Initialize the exporter with API credentials."""
        self.falcon = CloudSecurityAssets(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url
        )
        self.stats = {
            'ids_retrieved': 0,
            'resources_retrieved': 0,
            'api_calls_queries': 0,
            'api_calls_entities': 0,
            'start_time': None,
            'end_time': None
        }
    
    def query_all_ids(self, filter_expr: Optional[str] = None, limit: int = 1000) -> List[str]:
        """
        Query all resource IDs using token-based pagination.
        
        Args:
            filter_expr: FQL filter string (e.g., "cloud_provider:'aws'")
            limit: Number of IDs per request (max 1000)
        
        Returns:
            List of all resource IDs
        """
        print(f"Step 1: Querying resource IDs with filter: {filter_expr or 'None'}")
        
        all_ids = []
        after_token = None
        page = 0
        
        while True:
            page += 1
            
            # Build request parameters
            params = {'limit': limit}
            if filter_expr:
                params['filter'] = filter_expr
            if after_token:
                params['after'] = after_token
            
            # Make API call
            print(f"  Page {page}: Requesting {limit} IDs...", end='', flush=True)
            try:
                response = self.falcon.query_assets(**params)
                self.stats['api_calls_queries'] += 1
                
                if response['status_code'] != 200:
                    print(f"\n  Error: {response['body']}")
                    break
                
                # Extract IDs
                body = response['body']
                ids = body.get('resources', [])
                all_ids.extend(ids)
                self.stats['ids_retrieved'] += len(ids)
                
                print(f" Got {len(ids)} IDs (Total: {len(all_ids)})")
                
                # Check for next page token
                # The API returns the next page token in meta.next, not meta.pagination.after
                meta = body.get('meta', {})
                after_token = meta.get('next')  # Correct location for pagination token
                
                # Stop if no more pages
                if not after_token or len(ids) == 0:
                    break
                    
            except Exception as e:
                print(f"\n  Error querying IDs: {e}")
                break
        
        print(f"\nCompleted: Retrieved {len(all_ids)} total resource IDs")
        return all_ids
    
    def get_resource_details(self, ids: List[str], batch_size: int = 100) -> List[Dict]:
        """
        Retrieve full resource details for given IDs.
        
        Args:
            ids: List of resource IDs
            batch_size: Number of IDs per batch (max 100)
        
        Returns:
            List of resource objects
        """
        print(f"\nStep 2: Retrieving resource details for {len(ids)} IDs")
        print(f"  Batch size: {batch_size} (Total batches: {(len(ids) + batch_size - 1) // batch_size})")
        
        all_resources = []
        total_batches = (len(ids) + batch_size - 1) // batch_size
        
        for i in range(0, len(ids), batch_size):
            batch_num = (i // batch_size) + 1
            batch_ids = ids[i:i+batch_size]
            
            try:
                # Make API call
                response = self.falcon.get_assets(ids=batch_ids)
                self.stats['api_calls_entities'] += 1
                
                if response['status_code'] != 200:
                    print(f"  Batch {batch_num}/{total_batches}: Error - {response['body']}")
                    continue
                
                # Extract resources
                resources = response['body'].get('resources', [])
                all_resources.extend(resources)
                self.stats['resources_retrieved'] += len(resources)
                
                # Progress update every 100 batches
                if batch_num % 100 == 0 or batch_num == total_batches:
                    print(f"  Batch {batch_num}/{total_batches}: Retrieved {len(all_resources)} resources")
                
                # Rate limiting (simple delay)
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  Batch {batch_num}/{total_batches}: Error - {e}")
                continue
        
        print(f"\nCompleted: Retrieved {len(all_resources)} total resources")
        return all_resources
    
    def export_to_json(self, resources: List[Dict], output_file: str):
        """Export resources to JSON file."""
        print(f"\nStep 3: Exporting to {output_file}")
        
        try:
            with open(output_file, 'w') as f:
                json.dump(resources, f, indent=2)
            
            file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"  Successfully exported {len(resources)} resources")
            print(f"  File size: {file_size_mb:.2f} MB")
        except Exception as e:
            print(f"  Error writing file: {e}")
            raise
    
    def print_stats(self):
        """Print execution statistics."""
        if self.stats['end_time'] and self.stats['start_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
            duration_str = str(duration).split('.')[0]
        else:
            duration_str = "Unknown"
        
        print("\n" + "="*60)
        print("EXECUTION STATISTICS")
        print("="*60)
        print(f"Resource IDs retrieved:    {self.stats['ids_retrieved']:,}")
        print(f"Resources retrieved:       {self.stats['resources_retrieved']:,}")
        print(f"API calls (queries):       {self.stats['api_calls_queries']:,}")
        print(f"API calls (entities):      {self.stats['api_calls_entities']:,}")
        print(f"Total API calls:           {self.stats['api_calls_queries'] + self.stats['api_calls_entities']:,}")
        print(f"Execution time:            {duration_str}")
        print("="*60)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Export CrowdStrike Cloud Security Assets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --filter "cloud_provider:'aws'"
  %(prog)s --filter "active:true" --output active_assets.json
  %(prog)s --filter "cloud_provider:'aws'+active:true" --verbose
        """
    )
    
    parser.add_argument(
        '--filter',
        type=str,
        help='FQL filter string (e.g., "cloud_provider:\'aws\'")'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='cloud_assets.json',
        help='Output JSON file path (default: cloud_assets.json)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for entity retrieval (default: 100, max: 100)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Limit per query request (default: 1000, max: 1000)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Validate batch size
    if args.batch_size > 100:
        print("Warning: batch_size cannot exceed 100. Setting to 100.")
        args.batch_size = 100
    
    # Validate limit
    if args.limit > 1000:
        print("Warning: limit cannot exceed 1000. Setting to 1000.")
        args.limit = 1000
    
    # Load environment variables from .env file if available
    # Use override=True to force .env file values over cached environment variables
    if HAS_DOTENV:
        load_dotenv(override=True)
    
    # Get credentials from environment (works with or without dotenv)
    client_id = os.getenv('CROWDSTRIKE_CLIENT_ID')
    client_secret = os.getenv('CROWDSTRIKE_CLIENT_SECRET')
    base_url = os.getenv('CROWDSTRIKE_BASE_URL', 'https://api.crowdstrike.com')
    
    if not client_id or not client_secret:
        print("Error: CROWDSTRIKE_CLIENT_ID and CROWDSTRIKE_CLIENT_SECRET must be set")
        print("Please create a .env file or set environment variables")
        sys.exit(1)
    
    # Initialize exporter
    print("="*60)
    print("CrowdStrike Cloud Security Assets Exporter")
    print("="*60)
    print(f"Base URL: {base_url}")
    print(f"Filter: {args.filter or 'None'}")
    print(f"Output: {args.output}")
    print(f"Query limit: {args.limit}")
    print(f"Batch size: {args.batch_size}")
    print("="*60 + "\n")
    
    exporter = AssetExporter(client_id, client_secret, base_url)
    exporter.stats['start_time'] = datetime.now()
    
    try:
        # Step 1: Query all IDs
        all_ids = exporter.query_all_ids(filter_expr=args.filter, limit=args.limit)
        
        if not all_ids:
            print("\nNo resources found. Exiting.")
            return
        
        # Step 2: Get resource details
        all_resources = exporter.get_resource_details(all_ids, batch_size=args.batch_size)
        
        if not all_resources:
            print("\nNo resource details retrieved. Exiting.")
            return
        
        # Step 3: Export to JSON
        exporter.export_to_json(all_resources, args.output)
        
        exporter.stats['end_time'] = datetime.now()
        exporter.print_stats()
        
        print(f"\n✓ Export complete! Output saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\n\nExport interrupted by user")
        exporter.stats['end_time'] = datetime.now()
        exporter.print_stats()
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during export: {e}")
        exporter.stats['end_time'] = datetime.now()
        exporter.print_stats()
        sys.exit(1)


if __name__ == '__main__':
    main()