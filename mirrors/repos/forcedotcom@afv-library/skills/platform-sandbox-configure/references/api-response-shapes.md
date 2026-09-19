# Sandbox API Response Shapes

## Sandbox Reports — `GET /sandbox/reports`

```json
{
  "count": 3,
  "sandboxes": [
    {
      "sandbox": {
        "sandboxId": "07E...",
        "sandboxName": "DevBox1",
        "license": "Developer",
        "isPendingActivation": false,
        "canActivate": true,
        "canDelete": true,
        "canDiscard": false
      }
    }
  ]
}
```

## Sandbox Licenses — `GET /sandbox/licenses`

```json
{
  "count": 4,
  "licenses": [
    {
      "label": "Developer",
      "licenseType": "DEVELOPER",
      "limit": 35,
      "used": 11,
      "available": 24
    }
  ]
}
```
