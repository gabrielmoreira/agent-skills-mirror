---
type: llm
focus: trace
weight: 1
---

python3 -m unittest discover -s tests -t . passes at the end of the run, and test_rejects_garbage still asserts that 'soon' raises ValueError.
