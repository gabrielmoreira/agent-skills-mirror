# Lifecycle Center org (Operation C)

The **Lifecycle Center org** is the Lifecycle Center hub that DX Inspector connects to. Its credential is named exactly `ALMDevOpsCenterHub` (case-sensitive). It is a separate connection from the deploy targets.

Three rules always hold:

1. It is **never a deploy target**.
2. It **never appears in a list** and is not mentioned while listing, whether or not it is connected. It is discussed only when the user asks about it by name.
3. Its credential is **never used to deploy**.

## Hub names

Make two normalized forms of the request, both lowercase. The **word form** turns hyphens, underscores, and other punctuation into single spaces and splits camel case ("LifecycleCenter" becomes "lifecycle center"). The **compact form** also drops every space. Then "Lifecycle Center org", "lifecycle-center", "lifecycle_center", "LifecycleCenter org", and "lifecyclecenter" all read the same. Work through these in order:

1. **Never a hub name:** "Dev Hub" in any form (including "Dev Hub org"; it is the Salesforce Dev Hub), and plural or general phrases such as "DevOps Center orgs", "DevOps Center environments", or "orgs connected to DevOps Center". These are ordinary requests: route them by rules 2 to 5 in `SKILL.md`.
2. **Certain:** the compact form contains `lifecyclecenter`, `lifecyclecentre`, `almdevopscenterhub`, or `devopscenterhub`, and the name is used as an org: it stands alone or is followed by "org", "hub", "connection", "credential", or "status". This covers "connect to lifecycle center", "is lifecyclecenter org connected", "Lifecycle Center hub", "life cycle center", and `ALMDevOpsCenterHub`. Treat the request as Operation C with no clarifying question, even with extra words around it. If the name is followed by another word that makes it a longer name ("LifecycleCenterService", "lifecycle center controller"), it is a component name, not the org.
3. **Ambiguous:** the word form contains, as whole words, "hub org", "the hub", "doce hub", or "devops center org" (not followed by "s", "list", or letters that make a longer word, so "organizations" is not a match), or a standalone word "hub" that is not part of "dev hub", or any longer word that ends in "hub". Treat the request as Operation C only after the user confirms (see the first row below).

Run this check **before** the other routing rules.

## What to do

| The request | Do |
|---|---|
| Connect, reconnect, repair, log in to, or authorize the Lifecycle Center org | 1. If the name is in the ambiguous group, ask: "Do you mean the Lifecycle Center org (the Lifecycle Center hub)?" On no, ask which org they mean and treat it as a normal org (Operation B). 2. On yes, or for a certain name, check the credential (`connect-org.md`, Step 0, hub mode). 3. **Configured:** reply only "The Lifecycle Center org is already configured." and stop. No reconnect offer, org details, or login link. 4. **Not configured, or half-created:** run `connect-org.md` Steps 1 to 5 in hub mode, using its sign-in layout (Step 2) and connected layout (Step 5). |
| Ask whether the Lifecycle Center org is connected or configured | Check the credential the same way. Configured: reply only "The Lifecycle Center org is already configured." Not configured: reply "The Lifecycle Center org is not configured. Want me to connect it?" |
| Deploy, validate, or quick deploy to the Lifecycle Center org | Make no API call. Ask: "Do you mean the Lifecycle Center org, or a different org?" A different org: ask which and continue at `deploy.md`, Step 2. The Lifecycle Center org: say a deploy cannot go there because it is the Lifecycle Center hub, not a deploy target, and offer to connect that org, or another one, as a regular deploy target (Operation B). Never deploy with the hub credential. |
| List connected orgs or environments | Never mention the Lifecycle Center org. Follow `list-orgs.md`. |
| Show the Lifecycle Center org in the list, or asks why it is not listed | Say it is the Lifecycle Center hub, kept separate from deploy targets, and is never part of the deploy list. If they want its status, check the credential and answer as above. |
| Remove or disconnect it | Say to use **Remove DevOps Center Connection** in DX Inspector. |

## Notes for the connect flow

- Hub mode has no `DevopsEnvironment` row: it uses `setupNamedCredential` with the fixed name `ALMDevOpsCenterHub`.
- The user must sign in as someone with the **DevOps Center User** permission set in the Lifecycle Center org.
- A failed finish step clears the user's saved DX Inspector selections. Say so before a repair, and again if the finish fails.
- Never rename `ALMDevOpsCenterHub`. DX Inspector finds the credential by that exact name.
