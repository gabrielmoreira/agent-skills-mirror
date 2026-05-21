# API Response Structures

Full response examples for each Google Trends data type.

## RELATED_QUERIES

```json
{
  "search_metadata": {
    "status": "Success",
    "id": "...",
    "google_trends_url": "..."
  },
  "search_parameters": {
    "engine": "google_trends",
    "q": "sustainable fashion",
    "data_type": "RELATED_QUERIES",
    "date": "today 3-m"
  },
  "related_queries": {
    "rising": [
      {
        "query": "eco friendly clothing brands",
        "value": 345600,
        "extracted_value": 345600,
        "formatted_value": "Breakout"
      },
      {
        "query": "sustainable fashion 2024",
        "value": 18050,
        "extracted_value": 18050,
        "formatted_value": "+180%"
      }
    ],
    "top": [
      {
        "query": "sustainable fashion brands",
        "value": 100,
        "extracted_value": 100
      },
      {
        "query": "ethical fashion",
        "value": 82,
        "extracted_value": 82
      }
    ]
  }
}
```

### Key Fields

- `rising[].formatted_value`:
  - `"Breakout"` = 5000%+ growth (highest priority)
  - `"+N%"` = year-over-year growth percentage
- `top[].value`: Relative interest score (0-100 scale, 100 = most popular)

## RELATED_TOPICS

```json
{
  "search_metadata": {"status": "Success"},
  "related_topics": {
    "rising": [
      {
        "topic": {
          "mid": "/m/...",
          "title": "Organic Cotton",
          "type": "Topic"
        },
        "value": 345600,
        "formatted_value": "Breakout",
        "link": "/trends/explore?..."
      }
    ],
    "top": [
      {
        "topic": {
          "mid": "/m/...",
          "title": "Ethical Fashion",
          "type": "Topic"
        },
        "value": 82,
        "extracted_value": 82,
        "link": "/trends/explore?..."
      }
    ]
  }
}
```

### Key Fields

- `topic.title`: Human-readable topic name
- `topic.type`: Usually "Topic" or a specific category
- `formatted_value`: Same growth indicators as RELATED_QUERIES

## TIMESERIES

```json
{
  "search_metadata": {"status": "Success"},
  "interest_over_time": {
    "timeline_data": [
      {
        "date": "Jan 1 - 7, 2024",
        "timestamp": "1704067200",
        "values": [
          {
            "query": "react",
            "value": "85",
            "extracted_value": 85
          },
          {
            "query": "vue",
            "value": "32",
            "extracted_value": 32
          }
        ]
      },
      {
        "date": "Jan 8 - 14, 2024",
        "timestamp": "1704672000",
        "values": [
          {
            "query": "react",
            "value": "88",
            "extracted_value": 88
          },
          {
            "query": "vue",
            "value": "30",
            "extracted_value": 30
          }
        ]
      }
    ]
  }
}
```

### Key Fields

- `timeline_data[].date`: Human-readable date range
- `timeline_data[].timestamp`: Unix timestamp
- `values[].extracted_value`: Interest score (0-100, relative to peak)

## GEO_MAP_0

```json
{
  "search_metadata": {"status": "Success"},
  "interest_by_region": [
    {
      "geo": "US-CA",
      "location": "California",
      "max_value_index": 0,
      "value": 100,
      "extracted_value": 100
    },
    {
      "geo": "US-NY",
      "location": "New York",
      "max_value_index": 0,
      "value": 85,
      "extracted_value": 85
    }
  ]
}
```

## GEO_MAP (multi-query)

```json
{
  "search_metadata": {"status": "Success"},
  "compared_breakdown_by_region": [
    {
      "geo": "US-CA",
      "location": "California",
      "values": [
        {"query": "react", "value": "72%", "extracted_value": 72},
        {"query": "vue", "value": "28%", "extracted_value": 28}
      ]
    }
  ]
}
```
