#!/usr/bin/env python3
"""
CrowdStrike Cloud Security Assets Exporter

Exports large datasets (2M+ records) from CrowdStrike using proper pagination.
Uses token-based pagination to bypass 10,000 offset limit.
Streams results directly to file to handle large exports.
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
    """Handles exporting CrowdStrike cloud security assets with streaming."""
    
    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api.crowdstrike.com"):
        """Initialize the exporter with API credentials."""
        self.falcon = CloudSecurityAssets(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url
        )
        self.stats = {
            'ids_retrieved': 0,
            'resources_written': 0,
            'api_calls_queries': 0,
            'api_calls_entities': 0,
            'start_time': datetime.now(),
            'last_update_time': None
        }
    
    def query_all_ids(self, filter_expr: Optional[str], limit: int, output_file: str):
        """
        Query all resource IDs and stream resource details directly to file.
        
        Args:
            filter_expr: FQL filter string
            limit: Number of IDs per request (max 1000)
            output_file: Path to output JSON file
        """
        print(f"Step 1: Querying resource IDs with filter: {filter_expr or 'None'}")
        
        # Create output file with write mode
        with open(output_file, 'w') as f:
            f.write('[\n')  # Start JSON array
            
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
                
                print(f"  Page {page}: Requesting {limit} IDs...", end='', flush=True)
                
                try:
                    response = self.falcon.query_assets(**params)
                    self.stats['api_calls_queries'] += 1
                    
                    if response['status_code'] != 200:
                        print(f"\n  Error: {response['body']}")
                        break
                    
                    body = response['body']
                    ids = body.get('resources', [])
                    self.stats['ids_retrieved'] += len(ids)
                    
                    # Get details for this batch of IDs
                    resources = self.get_resource_details(ids)
                    self.stats['resources_written'] += len(resources)
                    
                    # Write resources to file
                    for i, resource in enumerate(resources):
                        json.dump(resource, f, indent=2 if i == 0 else None)
                        if i < len(resources) - 1 or after_token:
                            f.write(',\n')
                    
                    print(f" Got {len(ids)} IDs (Total: {self.stats['ids_retrieved']:,})")
                    
                    # Check for next page
                    after_token = body.get('meta', {}).get('next')
                    
                    if not after_token or len(ids) == 0:
                        break
                    
                    # Simple rate limiting
                    time.sleep(0.05)
                    
                except Exception as e:
                    print(f"\n  Error: {e}")
                    break
            
            f.write('\n]')  # Close JSON array
        
        print(f"\nCompleted: Retrieved {self.stats['ids_retrieved']:,} total resource IDs")
        print(f"Exported {self.stats['resources_written']:,} resources to {output_file}")
    
    def get_resource_details(self, ids: List[str]) -> List[Dict]:
        """
        Retrieve full resource details for given IDs in batches of 100.
        
        Args:
            ids: List of resource IDs
            
        Returns:
            List of resource objects
        """
        all_resources = []
        batch_size = 100
        
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i+batch_size]
            
            try:
                response = self.falcon.get_assets(ids=batch_ids)
                self.stats['api_calls_entities'] += 1
                
                if response['status_code'] == 200:
                    resources = response['body'].get('resources', [])
                    all_resources.extend(resources)
                
            except Exception:
                continue
            
            # Simple rate limiting
            time.sleep(0.05)
        
        return all_resources
    
    def print_stats(self):
        """Print execution statistics."""
        end_time = datetime.now()
        duration = end_time - self.stats['start_time']
        duration_str = str(duration).split('.')[0]
        
        print("\n" + "="*60)
        print("EXECUTION STATISTICS")
        print("="*60)
        print(f"Resource IDs retrieved:    {self.stats['ids_retrieved']:,}")
        print(f"Resources exported:        {self.stats['resources_written']:,}")
        print(f"API calls (queries):       {self.stats['api_calls_queries']:,}")
        print(f"API calls (entities):      {self.stats['api_calls_entities']:,}")
        print(f"Total API calls:           {self.stats['api_calls_queries'] + self.stats['api_calls_entities']:,}")
        print(f"Execution time:            {duration_str}")
        print("="*60)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Export CrowdStrike Cloud Security Assets to JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        help='Output JSON file path'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Limit per query request (max 1000)'
    )
    
    args = parser.parse_args()
    
    # Validate limit
    if args.limit > 1000:
        args.limit = 1000
    
    # Load credentials
    if HAS_DOTENV:
        load_dotenv(override=True)
    
    client_id = os.getenv('CROWDSTRIKE_CLIENT_ID')
    client_secret = os.getenv('CROWDSTRIKE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Error: Missing API credentials")
        sys.exit(1)
    
    exporter = AssetExporter(client_id, client_secret)
    
    try:
        exporter.query_all_ids(
            filter_expr=args.filter,
            limit=args.limit,
            output_file=args.output
        )
        
        exporter.print_stats()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()