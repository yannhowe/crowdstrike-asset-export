# CrowdStrike Cloud Security Assets Exporter

A simple Python script to export large datasets (2M+ records) from CrowdStrike Cloud Security Assets API using proper pagination techniques.

## Problem Statement

The CrowdStrike Cloud Security Assets API has specific pagination limits:
- **Queries endpoint**: 10,000 offset limit, requires token-based pagination for larger datasets
- **Entities endpoint**: 100 IDs maximum per GET request
- **Target**: Extract 2M+ cloud security assets efficiently

## Solution

This script uses:
1. **Token-based pagination** (`after` parameter) to bypass the 10,000 offset limit
2. **Batch processing** to retrieve entity details 100 IDs at a time
3. **Filtering** to optimize queries by cloud provider
4. **Progress tracking** and error handling

## Requirements

- Python 3.7+
- CrowdStrike API credentials with `cloud-security-assets:read` scope

## Installation

```bash
# Clone the repository
git clone https://github.com/yannhowe/crowdstrike-asset-export.git
cd crowdstrike-asset-export

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment file
cp .env.example .env
# Edit .env with your API credentials
```

## Configuration

Create a `.env` file with your CrowdStrike API credentials:

```env
CROWDSTRIKE_CLIENT_ID=your_client_id_here
CROWDSTRIKE_CLIENT_SECRET=your_client_secret_here
CROWDSTRIKE_BASE_URL=https://api.crowdstrike.com
```

## Usage

### Basic Usage

```bash
python export_assets.py
```

### With Custom Filters

```bash
# Export only AWS resources
python export_assets.py --filter "cloud_provider:'aws'"

# Export only active resources
python export_assets.py --filter "active:true"

# Export to custom output file
python export_assets.py --output my_assets.json
```

### Available Options

```
--filter TEXT       FQL filter string (e.g., "cloud_provider:'aws'")
--output TEXT       Output JSON file path (default: cloud_assets.json)
--batch-size INT    Batch size for entity retrieval (default: 100, max: 100)
--limit INT         Limit per query request (default: 1000, max: 1000)
--verbose          Enable verbose logging
```

## How It Works

### Step 1: Query Resource IDs (Token-Based Pagination)

The script uses the `after` parameter for token-based pagination, which bypasses the 10,000 offset limit:

```python
GET /cloud-security-assets/queries/resources/v1
  ?filter=cloud_provider:'aws'
  &limit=1000
  &after=<pagination_token>
```

### Step 2: Retrieve Resource Details (Batch Processing)

For each batch of 100 IDs, the script retrieves full resource details:

```python
GET /cloud-security-assets/entities/resources/v1
  ?ids=id1&ids=id2&...&ids=id100
```

## Performance

For 2M assets:
- **Total API calls**: ~22,000 (2,000 queries + 20,000 entity requests)
- **Estimated time**: 3-6 hours (depends on rate limits)
- **Output size**: ~1-5GB JSON file

## API References

- [CrowdStrike API Documentation](https://falcon.crowdstrike.com/documentation/page/a2a7fc0e/crowdstrike-oauth2-based-apis)
- [Cloud Security Assets API Swagger](https://assets.falcon.crowdstrike.com/support/api/swagger.html)
- JIRA CSPG-57039: POST endpoint for bulk entity retrieval (pending)

## Limitations

- **No POST endpoint**: The documented POST method for retrieving >100 entities doesn't exist yet (JIRA CSPG-57039)
- **Rate limits**: Respect CrowdStrike API rate limits (typically 600 requests/minute)
- **Memory usage**: Large exports may require streaming to avoid memory issues

## Troubleshooting

### "405 Method Not Allowed" for POST entities

The POST endpoint mentioned in Swagger docs doesn't exist yet. Use GET with 100 ID batches instead.

### "Offset cannot exceed 10000"

Use the `after` parameter instead of `offset` for pagination.

### Rate limit errors (429)

The script includes automatic retry with exponential backoff. Reduce `--limit` if needed.

## Contributing

Contributions welcome! Please submit issues or pull requests.

## License

MIT License - See LICENSE file for details