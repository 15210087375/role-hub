# Skills Hub API Reference

Base URL: `https://apps.habby.com/api/skills-hub`

## Public Endpoints (No Authentication)

### List/Search Skills

```
GET /skills
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| q | string | - | Search query (matches name, description) |
| tags | string | - | Comma-separated tag filter |
| sort | string | downloads | Sort field: `downloads`, `rating`, `createdAt`, `updatedAt` |
| order | string | desc | Sort order: `asc`, `desc` |
| page | number | 1 | Page number |
| limit | number | 20 | Items per page (max 100) |

**Response:**

```json
{
  "skills": [
    {
      "_id": "6789abc123def456",
      "name": "My Skill",
      "slug": "my-skill",
      "description": "Does something useful",
      "version": "1.0.0",
      "author": {
        "_id": "user123",
        "name": "John Doe",
        "email": "john@example.com"
      },
      "tags": ["automation", "productivity"],
      "downloadCount": 150,
      "averageRating": 4.5,
      "ratingCount": 12,
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-20T14:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

### Get Skill Detail

```
GET /skills/:idOrSlug
```

Returns full skill details including file information.

**Response:** Same as list item, plus:

```json
{
  "fileId": "uuid-of-file",
  "fileName": "my-skill.skill",
  "fileSize": 12345
}
```

### Download Skill

```
GET /skills/:id/download
```

Returns a pre-signed URL for downloading the skill file.

**Response:**

```json
{
  "downloadUrl": "https://s3.amazonaws.com/...",
  "fileName": "my-skill.skill",
  "fileSize": 12345,
  "runAfterInstall": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| downloadUrl | string | Time-limited S3 pre-signed URL |
| fileName | string | The .skill filename |
| fileSize | number | File size in bytes |
| runAfterInstall | boolean | If true, skill author recommends running immediately after install |

**Note:** The downloadUrl is a time-limited S3 pre-signed URL. Use it immediately.

### Download Specific Version

```
GET /skills/:id/versions/:version/download
```

**Response:**

```json
{
  "downloadUrl": "https://s3.amazonaws.com/...",
  "fileName": "my-skill.skill",
  "fileSize": 12345,
  "version": 2,
  "runAfterInstall": true
}
```

### List Comments

```
GET /skills/:id/comments
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | number | 1 | Page number |
| limit | number | 20 | Items per page |

**Response:**

```json
{
  "comments": [
    {
      "_id": "comment123",
      "content": "Great skill!",
      "author": {
        "_id": "user456",
        "name": "Jane Doe"
      },
      "createdAt": "2024-01-18T09:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

### List Tags

```
GET /tags
```

Returns all available tags with usage counts.

**Response:**

```json
{
  "tags": [
    { "name": "automation", "count": 25 },
    { "name": "productivity", "count": 18 },
    { "name": "development", "count": 12 }
  ]
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 404 | Skill not found |
| 500 | Server error |
