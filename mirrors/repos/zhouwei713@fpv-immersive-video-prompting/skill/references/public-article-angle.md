# Public article angle: action trajectory as the core of FPV video prompts

This reference captures the public-facing explanation of the FPV immersive video prompting workflow after writing a WeChat article from the skill.

## Article-level framing

The strongest general-audience angle is:

AI video prompts are not only about visual quality. For FPV / image-to-video scenes, the most fragile part is the action trajectory: who/what the camera is, where it starts, which stops it visits, how each segment is physically reachable, and where it ends.

Use this framing when the user asks for an explanatory article, X thread, tutorial intro, or demo write-up about this skill.

## Key narrative lessons

1. Treat FPV video as a small playable scene or game level.
   - Start point, route, stop order, target count, POV physics, and final reveal matter as much as style words.

2. For indoor / close character interaction scenes, numbered stop markers are usually easier to explain than a continuous red route line.
   - A bad red line can cross furniture, water, railings, people, or walls and then mislead the video model.
   - Numbered markers can be paired with strong prompt language: move from 1 to 2 to 3 in order, follow visible floor/corridor paths, no teleporting, no cuts, no obstacle crossing.

3. For world-scale routes, red-line path control remains useful.
   - Fantasy continent flythroughs, city-to-landmark routes, racing lines, canyon flights, world maps, and Seedance 2.0 path-control demos are better candidates for red-line route images.

4. Design the space before placing characters.
   - Example: for a modern living room, first define an open route from entrance → sofa → window → coffee table → bar → balcony, then place people along that route.
   - If characters are placed first as a beautiful group portrait, route continuity often breaks.

5. Count, duration, and interaction density must be linked.
   - 15 seconds with 5 people can support short individual beats.
   - 8 or 12 people should become zones/groups or quick gestures, not full dialogue for everyone.

6. POV identity can make or break the route.
   - Human: eye height, walking bob, hands/sleeves.
   - Cat: low height, furniture legs, paws/tail, no flying.
   - Robot vacuum: floor-only gliding, cannot climb stairs or jump.
   - Drone/bird/spirit: aerial arcs, banking, altitude changes, no footstep bob.

## Reusable quote-style lines

- FPV video prompts should describe action, not only images.
- If the model does not know how the camera moves, it will invent movement for you.
- Skill value is not storing one universal prompt; it is storing the judgment process: numbered stops or red line, how many targets, which POV, what timeline, what constraints.

## When writing examples

For public articles, avoid dumping full giant prompts unless the user explicitly wants templates. It is usually better to explain the decision logic with concrete scene snippets:

- modern living room: entrance → sofa → window → tea table → bar → balcony
- palace courtyard: gate → corridor column → flower tree → central steps → side corridor → pond
- fantasy map: snowfield → wall → valley → capital → strait → volcano

Then mention that the actual Skill can generate the full GPT Image asset-pack prompt and video prompt from these decisions.