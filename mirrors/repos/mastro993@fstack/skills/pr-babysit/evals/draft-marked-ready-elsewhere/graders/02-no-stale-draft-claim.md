---
type: regex
target: trace
pattern: '\(not a draft\)[\s\S]*"type":"text","text":"(?:[^"\\]|\\.)*?(?:still|stays?|remains?|is|it[''’]?s|(?:leav|keep)\w* it(?: as)?) (?:a |in )?draft'
flags: i
match: not_contains
weight: 1
---

Once a snapshot showed the PR as not a draft, no message to the user called it a draft.
