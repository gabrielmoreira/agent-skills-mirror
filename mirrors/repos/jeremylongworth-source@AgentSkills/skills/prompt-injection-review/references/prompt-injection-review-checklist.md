# Prompt Injection Review Checklist

## Search For

- "ignore previous"
- "system message"
- "developer message"
- "do not tell the user"
- "secretly"
- "exfiltrate"
- "send to"
- "download and run"
- "bypass"
- base64 or encoded instruction blocks
- hidden HTML comments or metadata
- instructions inside examples or test data

## Review Questions

- Does the skill distinguish trusted instructions from untrusted content?
- Does it tell the agent to quote or summarize external text rather than obey
  it?
- Does it require approval before tool escalation or outbound actions?
- Could examples be mistaken for operating instructions?
- Are conflicting host or vendor instructions present?

## Mitigations

- Remove unsafe instructions.
- Mark sample content as examples, not commands.
- Add untrusted-content handling guidance.
- Narrow trigger descriptions.
- Require human review for high-risk actions.
