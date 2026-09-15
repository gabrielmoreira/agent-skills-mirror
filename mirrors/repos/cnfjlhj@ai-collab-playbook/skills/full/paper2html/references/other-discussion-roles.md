# Other Discussion Roles — Source Prompts

## Source boundary

- Course: MIT MAS.S60, *How to AI (Almost) Anything*, Spring 2025
- Slide deck: `lec1 - introduction.pdf`
- Slide: 26, **Other Discussion Roles**
- Official URL: <https://mit-mi.github.io/how2ai-course/spring2025/schedule/lec1%20-%20introduction.pdf>
- Verified from the official URL: 2026-09-14
- Slide credit: “Thanks to Alec Jacobson and Colin Raffel”

The seven prompts below are transcribed verbatim from the official slide. Do
not shorten, paraphrase, merge, rename, or silently omit them in a paper2html
page.

## Verbatim prompts

### Scientific Peer Reviewer

> The paper has not been published yet and is currently submitted to a top conference where you’ve been assigned as a peer reviewer. Complete a full review of the paper answering all prompts of the official review form of the top venue in this research area (e.g., NeurIPS). This includes recommending whether to accept or reject the paper.

### Archaeologist

> This paper was found buried under ground in the desert. You’re an archeologist who must determine where this paper sits in the context of previous and subsequent work. Find and report on one older paper cited within the current paper that substantially influenced the current paper and one newer paper that cites this current paper.

### Academic Researcher

> You’re a researcher who is working on a new project in this area. Propose an imaginary follow-up project not just based on the current but only possible due to the existence and success of the current paper.

### Industry Practitioner

> You work at a company or organization developing an application or product of your choice (that has not already been suggested in a prior session). Bring a convincing pitch for why you should be paid to implement the method in the paper, and discuss at least one positive and negative impact of this application.

### Hacker

> You’re a hacker who needs a demo of this paper ASAP. Implement a small part or simplified version of the paper on a small dataset or toy problem. Prepare to share the core code of the algorithm to the class and demo your implementation. Do not simply download and run an existing implementation – though you are welcome to use (and give credit to) an existing implementation for “backbone” code.

### Private Investigator

> You are a detective who needs to run a background check on one of the paper’s authors. Where have they worked? What did they study? What previous projects might have led to working on this one? What motivated them to work on this project? Feel free to contact the authors, but remember to be courteous, polite, and on-topic.

### Social Impact Assessor

> Identify how this paper self-assesses its (likely positive) impact on the world. Have any additional positive social impacts left out? What are possible negative social impacts that were overlooked or omitted?

## Paper2HTML rendering contract

- Make **Other Discussion Roles / 其他讨论角色** the last substantive section.
  Only `Reference / Evidence` may follow it.
- Show all seven roles explicitly, using the exact English role names above.
- Under every role, show its complete original English prompt verbatim, then a
  substantial Chinese response grounded in the paper and public evidence.
- A response must execute every instruction in its role prompt. It may not be
  replaced by a generic summary, one-line opinion, or “not applicable” without
  an evidence-backed explanation.
- Keep facts, hypotheses, and recommendations distinct. Cite public sources for
  later papers, author backgrounds, products, social impacts, and other facts
  not established by the focal paper.
- For **Scientific Peer Reviewer**, use the actual review dimensions of the
  most plausible top venue when available and finish with an explicit
  accept/reject recommendation plus confidence.
- For **Archaeologist**, identify both required works: one older cited paper
  that substantially influenced the focal paper and one newer paper that cites
  it. If no newer citing paper can be verified, state the search boundary and
  the absence of verified evidence; do not invent one.
- For **Academic Researcher**, the follow-up must be enabled by the focal
  paper’s existence and success, not merely be a small extension named in its
  future-work section.
- For **Industry Practitioner**, give a concrete product/application pitch and
  at least one positive and one negative impact.
- For **Hacker**, specify or implement a small-data/toy-problem demonstration,
  expose the core algorithm/code path, and distinguish original work from
  credited backbone code. Do not claim execution unless it was actually run.
- For **Private Investigator**, use public professional/academic sources only.
  The original prompt is preserved verbatim, including its invitation to
  contact authors, but paper2html must not contact anyone without the user’s
  explicit approval.
- For **Social Impact Assessor**, first report the paper’s own impact framing,
  then identify additional positive impacts and overlooked/omitted negative
  impacts.
