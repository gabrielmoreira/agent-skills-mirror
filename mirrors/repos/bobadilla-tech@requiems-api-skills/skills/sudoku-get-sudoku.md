---
name: sudoku-get-sudoku
api: Sudoku
method: GET
path: /v1/entertainment/sudoku
base_url: https://api.requiems.xyz
description: Returns a randomly generated Sudoku puzzle and its solution. Difficulty defaults to medium when not specified.
---

## Endpoint

**GET https://api.requiems.xyz/v1/entertainment/sudoku**

## Get Sudoku Puzzle

Returns a randomly generated Sudoku puzzle and its solution. Difficulty defaults
to medium when not specified.

## Parameters

| Name         | Type   | Required | Location | Description                                                              |
| ------------ | ------ | -------- | -------- | ------------------------------------------------------------------------ |
| `difficulty` | string | no       | query    | Puzzle difficulty level. One of: easy, medium, hard. Defaults to medium. |

## Response Example

```json
{
  "data": {
    "difficulty": "hard",
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
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field        | Type                  | Description                                                              |
| ------------ | --------------------- | ------------------------------------------------------------------------ |
| `difficulty` | string                | The difficulty level of the returned puzzle (easy, medium, or hard)      |
| `puzzle`     | array[array[integer]] | 9×9 grid representing the puzzle — 0 means an empty cell to be filled in |
| `solution`   | array[array[integer]] | 9×9 grid containing the complete, valid solution                         |

## Errors

- `400` **bad_request** — The difficulty parameter is not one of easy, medium,
  or hard
- `401` **unauthorized** — Missing API key
- `403` **forbidden** — Invalid or revoked API key
