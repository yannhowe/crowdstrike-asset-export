# Filter Examples

This document provides common FQL filter examples for the CrowdStrike Cloud Security Assets API.

## Basic Filters

### Filter by Cloud Provider

```bash
# AWS only
python export_assets.py --filter "cloud_provider:'aws'"

# Azure only
python export_assets.py --filter "cloud_provider:'azure'"

# GCP only
python export_assets.py --filter "cloud_provider:'gcp'"
```

### Filter by Active Status

```bash
# Active resources only
python export_assets.py --filter "active:true"

# Inactive resources only
python export_assets.py --filter "active:false"
```

### Filter by Resource Type

```bash
# EC2 instances only
python export_assets.py --filter "resource_type:'aws-ec2-instance'"

# S3 buckets only
python export_assets.py --filter "resource_type:'aws-s3-bucket'"

# Azure VMs only
python export_assets.py --filter "resource_type:'azure-vm'"
```

## Combined Filters

Use `+` to combine multiple filters (AND operation):

```bash
# Active AWS resources
python export_assets.py --filter "cloud_provider:'aws'+active:true"

# AWS EC2 instances in us-east-1
python export_assets.py --filter "cloud_provider:'aws'+resource_type:'aws-ec2-instance'+region:'us-east-1'"

# Non-compliant resources
python export_assets.py --filter "iom_count:>0"

# Publicly exposed resources
python export_assets.py --filter "publicly_exposed:true"
```

## Advanced Filters

### Resources with IOMs (Indicators of Misconfiguration)

```bash
# Any IOMs
python export_assets.py --filter "iom_count:>0"

# Critical severity IOMs
python export_assets.py --filter "non_compliant.severity:'CRITICAL'"

# Specific framework compliance
python export_assets.py --filter "non_compliant.framework:'CIS'"
```

### Resources by Region

```bash
# AWS us-east-1
python export_assets.py --filter "cloud_provider:'aws'+region:'us-east-1'"

# Azure eastus
python export_assets.py --filter "cloud_provider:'azure'+region:'eastus'"
```

### Resources by Tags

```bash
# Resources with specific tag key
python export_assets.py --filter "tag_key:'Environment'"

# Resources with specific tag value
python export_assets.py --filter "tag_value:'Production'"

# Combined tag filter
python export_assets.py --filter "tag_key:'Environment'+tag_value:'Production'"
```

### Resources by Instance State

```bash
# Running instances
python export_assets.py --filter "instance_state:'running'"

# Stopped instances
python export_assets.py --filter "instance_state:'stopped'"
```

## Date-Based Filters

```bash
# Resources created after a specific date
python export_assets.py --filter "creation_time:>'2025-01-01T00:00:00Z'"

# Resources first seen in last 7 days
python export_assets.py --filter "first_seen:>'2025-01-15T00:00:00Z'"
```

## Security-Focused Filters

```bash
# Publicly exposed resources with IOMs
python export_assets.py --filter "publicly_exposed:true+iom_count:>0"

# Unmanaged resources (no CrowdStrike sensor)
python export_assets.py --filter "managed_by:null"

# Resources with vulnerabilities
python export_assets.py --filter "snapshot_detections:>0"

# Resources accessing sensitive data (requires DSPM)
python export_assets.py --filter "data_classifications.found:true"
```

## Full Export Examples

### Export All AWS Production Resources

```bash
python export_assets.py \
  --filter "cloud_provider:'aws'+tag_key:'Environment'+tag_value:'Production'" \
  --output aws_production.json
```

### Export Non-Compliant Resources

```bash
python export_assets.py \
  --filter "iom_count:>0" \
  --output non_compliant_resources.json
```

### Export Publicly Exposed Critical Resources

```bash
python export_assets.py \
  --filter "publicly_exposed:true+non_compliant.severity:'CRITICAL'" \
  --output exposed_critical.json
```

## Filterable Fields Reference

From the Swagger documentation, you can filter on these fields:

- `account_id`, `account_name`
- `active`
- `cloud_provider`, `cloud_scope`
- `region`, `zone`
- `resource_id`, `resource_name`, `resource_type`, `resource_type_name`
- `service`, `service_category`
- `instance_id`, `instance_state`
- `creation_time`, `first_seen`, `updated_at`
- `ioa_count`, `iom_count`
- `publicly_exposed`
- `managed_by`
- `tag_key`, `tag_value`, `tags`
- `status`
- `control.framework`, `control.benchmark.name`
- `non_compliant.severity`, `non_compliant.framework`
- `data_classifications.found`, `data_classifications.label`
- And many more...

See the full Swagger documentation for complete list.