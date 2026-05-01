---
name: "n8n-photo-report"
description: "Automate construction photo report generation using n8n with AI-powered image analysis."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🔧", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# n8n Photo Report Automation

## Business Case

Site photos require organization, analysis, and reporting. This workflow automates photo collection, AI analysis, and report generation.

## Workflow Overview

```
[Photo Upload] → [AI Analysis] → [Categorization] → [Report Generation] → [Distribution]
```

## n8n Workflow Configuration

### 1. Photo Input Triggers

```json
{
  "nodes": [
    {
      "name": "Photo Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "photo-upload",
        "options": {
          "binaryData": true
        }
      }
    },
    {
      "name": "Watch Dropbox Folder",
      "type": "n8n-nodes-base.dropbox",
      "parameters": {
        "operation": "listFolder",
        "path": "/SitePhotos/{{$today}}"
      }
    }
  ]
}
```

### 2. AI Image Analysis

```json
{
  "name": "Analyze with Claude Vision",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.anthropic.com/v1/messages",
    "headers": {
      "x-api-key": "={{$env.ANTHROPIC_API_KEY}}",
      "anthropic-version": "2023-06-01"
    },
    "body": {
      "model": "claude-3-5-sonnet-20241022",
      "max_tokens": 1024,
      "messages": [{
        "role": "user",
        "content": [
          {
            "type": "image",
            "source": {
              "type": "base64",
              "media_type": "image/jpeg",
              "data": "={{$binary.data.toString('base64')}}"
            }
          },
          {
            "type": "text",
            "text": "Analyze this construction site photo. Identify: 1) Work activity visible, 2) Approximate completion status, 3) Any safety concerns, 4) Weather conditions. Return JSON format."
          }
        ]
      }]
    }
  }
}
```

### 3. Categorize and Store

```json
{
  "nodes": [
    {
      "name": "Parse AI Response",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const response = JSON.parse($json.content[0].text);\n\nreturn [{\n  json: {\n    filename: $('Photo Webhook').first().json.filename,\n    timestamp: new Date().toISOString(),\n    activity: response.work_activity,\n    completion: response.completion_status,\n    safety_issues: response.safety_concerns,\n    weather: response.weather,\n    category: response.work_activity.includes('concrete') ? 'CONCRETE' :\n              response.work_activity.includes('steel') ? 'STEEL' :\n              response.work_activity.includes('mep') ? 'MEP' : 'GENERAL'\n  }\n}];"
      }
    },
    {
      "name": "Store in Airtable",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "create",
        "table": "Site Photos",
        "fields": {
          "Filename": "={{$json.filename}}",
          "Date": "={{$json.timestamp}}",
          "Activity": "={{$json.activity}}",
          "Category": "={{$json.category}}",
          "Completion": "={{$json.completion}}",
          "Safety Issues": "={{$json.safety_issues}}"
        }
      }
    }
  ]
}
```

### 4. Generate Photo Report

```json
{
  "nodes": [
    {
      "name": "Schedule Report",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {"interval": [{"field": "cronExpression", "expression": "0 18 * * 1-5"}]}
      }
    },
    {
      "name": "Get Today Photos",
      "type": "n8n-nodes-base.airtable",
      "parameters": {
        "operation": "list",
        "table": "Site Photos",
        "filterByFormula": "IS_SAME({Date}, TODAY(), 'day')"
      }
    },
    {
      "name": "Generate Report",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const photos = $input.all();\n\nconst byCategory = {};\nlet safetyIssues = [];\n\nphotos.forEach(p => {\n  const cat = p.json.fields.Category;\n  if (!byCategory[cat]) byCategory[cat] = [];\n  byCategory[cat].push(p.json.fields);\n  \n  if (p.json.fields['Safety Issues'] && p.json.fields['Safety Issues'] !== 'None') {\n    safetyIssues.push({\n      photo: p.json.fields.Filename,\n      issue: p.json.fields['Safety Issues']\n    });\n  }\n});\n\nreturn [{\n  json: {\n    date: new Date().toISOString().split('T')[0],\n    total_photos: photos.length,\n    by_category: byCategory,\n    safety_issues: safetyIssues,\n    safety_count: safetyIssues.length\n  }\n}];"
      }
    }
  ]
}
```

### 5. Distribution

```json
{
  "name": "Send Report Email",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "toEmail": "={{$env.PHOTO_REPORT_RECIPIENTS}}",
    "subject": "Site Photo Report - {{$json.date}} ({{$json.total_photos}} photos)",
    "html": "<h2>Daily Photo Report</h2><p>Total Photos: {{$json.total_photos}}</p><h3>Safety Issues: {{$json.safety_count}}</h3>{{#if $json.safety_issues.length}}<ul>{{#each $json.safety_issues}}<li>{{photo}}: {{issue}}</li>{{/each}}</ul>{{/if}}"
  }
}
```

## Python Helper

```python
import requests
import base64

def upload_photo_to_workflow(image_path: str, webhook_url: str, metadata: dict):
    """Upload photo to n8n workflow."""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()

    payload = {
        'filename': image_path.split('/')[-1],
        'image_data': image_data,
        'project_id': metadata.get('project_id'),
        'location': metadata.get('location'),
        'captured_by': metadata.get('captured_by')
    }

    response = requests.post(webhook_url, json=payload)
    return response.json()


def batch_upload_photos(photo_paths: list, webhook_url: str, project_id: str):
    """Batch upload multiple photos."""
    results = []
    for path in photo_paths:
        result = upload_photo_to_workflow(path, webhook_url, {'project_id': project_id})
        results.append(result)
    return results
```

## Quick Start

1. Import workflow to n8n
2. Configure API keys:
   - `ANTHROPIC_API_KEY` for Claude Vision
   - Airtable credentials
   - Email configuration
3. Create Airtable base with "Site Photos" table
4. Test with sample photo upload

## Resources
- **n8n Documentation**: https://docs.n8n.io
- **Claude Vision API**: https://docs.anthropic.com
- **DDC Book**: Chapter 4.2 - Workflow Automation
