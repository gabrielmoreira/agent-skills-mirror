---
name: sudoku-post-batch
api: Sudoku
method: POST
path: /v1/entertainment/sudoku/batch
base_url: https://api.requiems.xyz
description: Generate up to 20 Sudoku puzzles in a single request. Results are returned in the same order as the input array. Each puzzle in the batch counts as one unit of API usage.
---

## Endpoint

**POST https://api.requiems.xyz/v1/entertainment/sudoku/batch**

## Batch Generate Sudoku Puzzles

Generate up to 20 Sudoku puzzles in a single request. Results are returned in the same order as the input array. Each puzzle in the batch counts as one unit of API usage.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `puzzles` | array | yes | body | Array of difficulty levels to generate (min: 1, max: 20). Each must be one of: easy, medium, hard. |

## Request Example

```json
{
  "puzzles": ["easy", "hard"]
}
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "difficulty": "easy",
        "puzzle": [
          [5, 3, 0, 0, 7, 0, 0, 0, 0],
          [6, 0, 0, 1, 9, 5, 0, 0, 0],
          [0, 9, 8, 0, 0, 0, 0, 6, 0],
          [8, 0, 0, 0, 6, 0, 0, 0, 3],
          [4, 0, 0, 8, 0, 3, 0, 0, 1],
          [7, 0, 0, 0, 2, 0, 0, 0, 6],
          [0, 6, 0, 0, 0, 0, 2, 8, 0],
          [0, 0, 0, 4, 1, 9, 0, 0, 5],
          [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ],
        "solution": [
          [5, 3, 4, 6, 7, 8, 9, 1, 2],
          [6, 7, 2, 1, 9, 5, 3, 4, 8],
          [1, 9, 8, 3, 4, 2, 5, 6, 7],
          [8, 5, 9, 7, 6, 1, 4, 2, 3],
          [4, 2, 6, 8, 5, 3, 7, 9, 1],
          [7, 1, 3, 9, 2, 4, 8, 5, 6],
          [9, 6, 1, 5, 3, 7, 2, 8, 4],
          [2, 8, 7, 4, 1, 9, 6, 3, 5],
          [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
      }
    ],
    "total": 1
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | Generated puzzles in the same order as the input array. Each item has the same fields as the single-puzzle endpoint. |
| `results[].difficulty` | string | The difficulty level of the puzzle (easy, medium, or hard) |
| `results[].puzzle` | array[array[integer]] | 9×9 grid representing the puzzle — 0 means an empty cell to be filled in |
| `results[].solution` | array[array[integer]] | 9×9 grid containing the complete, valid solution |
| `total` | integer | Number of puzzles returned. Matches the length of the input array. |

## Errors

- `400` **bad_request** — The request body is missing or contains malformed JSON.
- `422` **validation_failed** — The puzzles array is missing, empty, exceeds 20 items, or contains a value other than easy, medium, or hard.
- `401` **unauthorized** — Missing API key
- `403` **forbidden** — Invalid or revoked API key
