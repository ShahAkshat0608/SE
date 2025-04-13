# Analytics Microservice Output Information

## Overview
This document describes the output formats and information provided by the analytics microservice.

## Output Formats
The analytics microservice provides data in the following formats:
- JSON
- CSV (for data exports)
- Visualization-ready datasets

## API Endpoints Output

### GET /analytics/summary
**Description**: Provides summary statistics of user activities and system usage.

**Response Format**:
```json
{
    "activeUsers": 1250,
    "totalTransactions": 5678,
    "averageResponseTime": 235,
    "timeUnit": "ms",
    "periodCovered": "last 24 hours",
    "timestamp": "2023-11-15T14:30:00Z"
}
```

### GET /analytics/trends
**Description**: Returns trend data for specified metrics.

**Response Format**:
```json
{
    "metric": "userEngagement",
    "timeScale": "daily",
    "data": [
        {"date": "2023-11-14", "value": 456},
        {"date": "2023-11-15", "value": 492}
    ],
    "changeSinceLastPeriod": "+7.89%"
}
```

### POST /analytics/custom
**Description**: Returns custom analytics based on provided parameters.

**Response Format**:
```json
{
    "queryId": "a1b2c3d4",
    "results": [...],
    "processingTime": 1.25,
    "resultCount": 42,
    "hasMoreData": false
}
```

## Error Response Format
When an error occurs, the service returns:

```json
{
    "error": true,
    "code": 400,
    "message": "Invalid date range specified",
    "details": "Start date must be before end date",
    "requestId": "req-123456"
}
```

## Data Retention
- Aggregated analytics data is retained for 12 months
- Raw data points are retained for 30 days
- Exported reports are available for download for 7 days

## Notes
- All timestamps are provided in UTC (ISO 8601 format)
- Numerical metrics include precision to 2 decimal places unless otherwise specified
- Percentage changes are relative to the previous comparable time period
