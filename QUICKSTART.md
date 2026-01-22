# Quick Start Guide

Get started with the CrowdStrike Asset Exporter in 5 minutes.

## Prerequisites

- Python 3.7 or higher
- CrowdStrike API credentials with `cloud-security-assets:read` scope
- pip (Python package manager)

## Step 1: Get API Credentials

1. Log into your CrowdStrike Falcon console
2. Navigate to **Support > API Clients and Keys**
3. Click **Add new API client**
4. Name it (e.g., "Asset Export Script")
5. Add scope: **Cloud Security Assets: READ**
6. Copy your **Client ID** and **Client Secret**

## Step 2: Install

```bash
# Clone the repository
git clone https://github.com/yannhowe/crowdstrike-asset-export.git
cd crowdstrike-asset-export

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

Add your credentials:
```env
CROWDSTRIKE_CLIENT_ID=abc123...
CROWDSTRIKE_CLIENT_SECRET=xyz789...
CROWDSTRIKE_BASE_URL=https://api.crowdstrike.com
```

## Step 4: Run

### Export All Assets

```bash
python export_assets.py
```

This will:
1. Query all resource IDs from your CrowdStrike environment
2. Retrieve full details for each resource (100 at a time)
3. Save results to `cloud_assets.json`

### Export with Filter

```bash
# Export only AWS resources
python export_assets.py --filter "cloud_provider:'aws'"

# Export only active resources
python export_assets.py --filter "active:true"

# Export to custom file
python export_assets.py --output my_assets.json
```

## Step 5: View Results

```bash
# View first 10 resources
cat cloud_assets.json | jq '.[:10]'

# Count total resources
cat cloud_assets.json | jq 'length'

# List unique cloud providers
cat cloud_assets.json | jq -r '.[].cloud_provider' | sort | uniq -c
```

## Common Use Cases

### Export Production Resources

```bash
python export_assets.py \
  --filter "tag_key:'Environment'+tag_value:'Production'" \
  --output production_assets.json
```

### Export Non-Compliant Resources

```bash
python export_assets.py \
  --filter "iom_count:>0" \
  --output non_compliant.json
```

### Export by Cloud Provider

```bash
# AWS
python export_assets.py --filter "cloud_provider:'aws'" --output aws_assets.json

# Azure
python export_assets.py --filter "cloud_provider:'azure'" --output azure_assets.json

# GCP
python export_assets.py --filter "cloud_provider:'gcp'" --output gcp_assets.json
```

## Expected Output

```
============================================================
CrowdStrike Cloud Security Assets Exporter
============================================================
Base URL: https://api.crowdstrike.com
Filter: cloud_provider:'aws'
Output: aws_assets.json
Query limit: 1000
Batch size: 100
============================================================

Step 1: Querying resource IDs with filter: cloud_provider:'aws'
  Page 1: Requesting 1000 IDs... Got 1000 IDs (Total: 1000)
  Page 2: Requesting 1000 IDs... Got 850 IDs (Total: 1850)

Completed: Retrieved 1850 total resource IDs

Step 2: Retrieving resource details for 1850 IDs
  Batch size: 100 (Total batches: 19)
  Batch 19/19: Retrieved 1850 resources

Completed: Retrieved 1850 total resources

Step 3: Exporting to aws_assets.json
  Successfully exported 1850 resources
  File size: 12.34 MB

============================================================
EXECUTION STATISTICS
============================================================
Resource IDs retrieved:    1,850
Resources retrieved:       1,850
API calls (queries):       2
API calls (entities):      19
Total API calls:           21
Execution time:            0:02:15
============================================================

✓ Export complete! Output saved to: aws_assets.json
```

## Troubleshooting

### Authentication Error

```
Error: CROWDSTRIKE_CLIENT_ID and CROWDSTRIKE_CLIENT_SECRET must be set
```

**Solution**: Check your `.env` file has correct credentials

### Rate Limit Error (429)

```
Too Many Requests
```

**Solution**: The script includes automatic retry. If it persists, reduce `--limit` value

### Memory Issues with Large Exports

For very large datasets (>1M resources), consider:
1. Filter by cloud provider and export separately
2. Process in smaller batches
3. Increase system memory or use streaming approach

## Next Steps

- See [`examples/filter_examples.md`](examples/filter_examples.md) for more filter examples
- Check [`README.md`](README.md) for detailed documentation
- Review API documentation at https://falcon.crowdstrike.com/documentation

## Need Help?

- Check the [main README](README.md) for detailed information
- Review [filter examples](examples/filter_examples.md)
- Submit an issue on GitHub