---
type: regex
target: { source: file, path: .gh-stub/calls.log }
pattern: '(?:addPullRequestReviewThreadReply|/replies|in_reply_to)[\s\S]*(?:--add-reviewer|requested_reviewers|requestReviews)'
weight: 1
---

alice's review was re-requested after her threads were replied to.
