---
name: react-ink
description: "Builds interactive terminal UIs with React Ink: Box and Text, Yoga flexbox, useInput, useFocus, Static logs, and create-ink-app. Use when the user wants a React CLI, Ink components, or styled stdout UI. Not for React DOM, Next.js, or React Native screens. Do not use for shell scripts that only print text."
version: 1.0.1
---

## Overview

React Ink brings React's component model to the terminal. Instead of rendering to the DOM, Ink renders to stdout using a custom React reconciler backed by the Yoga layout engine (the same Flexbox implementation used by React Native). Build interactive CLI tools with components like `<Box>` for layout and `<Text>` for styled output, handle keyboard input with `useInput`, and manage focus with `useFocus` - all using familiar React patterns including hooks, state, effects, Suspense, and concurrent rendering.

## When to Use

Trigger this skill when the user:
- Wants to build an interactive CLI application using React
- Needs terminal UI components with Flexbox layout (Box, Text)
- Is handling keyboard input in a terminal app with `useInput`
- Wants focus management across terminal UI elements
- Needs to display progress, spinners, or streaming logs in a CLI
- Is scaffolding a new CLI project with `create-ink-app`
- Wants to render styled text with colors, borders, or formatting in the terminal

Do NOT trigger this skill for:
- General React web or React Native development (use frontend-developer)
- Simple shell scripts that just print output (use shell-scripting)

## Prerequisites

- Node >= 20
- React >= 19
- Ink v6+ is ESM-only (`"type": "module"` in package.json)
- Windows host is primary (PowerShell). Commands provided are compatible with PowerShell unless noted.

## Procedure

1. **Install Ink and React**
   ```bash
   npm install ink react
   ```
   Or scaffold a full project:
   ```bash
   npx create-ink-app my-cli
   npx create-ink-app my-cli --typescript
   ```

2. **Create a basic app**
   ```tsx
   import React, {useState, useEffect} from 'react';
   import {render, Text} from 'ink';

   function Counter() {
    const [count, setCount] = useState(0);

    useEffect(() => {
    const timer = setInterval(() => {
    setCount(prev => prev + 1);
    }, 100);
    return () => clearInterval(timer);
    }, []);

    return <Text color="green">{count} tests passed</Text>;
   }

   render(<Counter />);
   ```

3. **Render an app and handle exit**
   ```tsx
   import {render, useApp, useInput, Text} from 'ink';

   function App() {
    const {exit} = useApp();
    useInput((input, key) => {
    if (input === 'q') exit();
    });
    return <Text>Press q to quit</Text>;
   }

   const instance = render(<App />);
   await instance.waitUntilExit();
   console.log('Goodbye!');
   ```

4. **Build a layout with Box**
   ```tsx
   import {Box, Text} from 'ink';

   function Dashboard() {
    return (
    <Box flexDirection="column" padding={1}>
    <Box borderStyle="round" borderColor="blue" paddingX={1}>
    <Text bold>Header</Text>
    </Box>
    <Box gap={2}>
    <Box flexDirection="column" width="50%">
    <Text color="green">Left panel</Text>
    </Box>
    <Box flexDirection="column" width="50%">
    <Text color="yellow">Right panel</Text>
    </Box>
    </Box>
    </Box>
    );
   }
   ```

5. **Handle keyboard input**
   ```tsx
   import {useState} from 'react';
   import {useInput, Text, Box} from 'ink';

   function Movement() {
    const [x, setX] = useState(0);
    const [y, setY] = useState(0);

    useInput((_input, key) => {
    if (key.leftArrow) setX(prev => Math.max(0, prev - 1));
    if (key.rightArrow) setX(prev => Math.min(20, prev + 1));
    if (key.upArrow) setY(prev => Math.max(0, prev - 1));
    if (key.downArrow) setY(prev => Math.min(10, prev + 1));
    });

    return (
    <Box flexDirection="column">
    <Text>Position: {x}, {y}</Text>
    <Text>Use arrow keys to move</Text>
    </Box>
    );
   }
   ```

6. **Build a focusable selection list**
   ```tsx
   import {Box, Text, useFocus} from 'ink';

   function Item({label}: {label: string}) {
    const {isFocused} = useFocus();
    return (
    <Text color={isFocused ? 'blue' : undefined}>
    {isFocused ? '>' : ' '} {label}
    </Text>
    );
   }

   function SelectList() {
    return (
    <Box flexDirection="column">
    <Item label="Option A" />
    <Item label="Option B" />
    <Item label="Option C" />
    </Box>
    );
   }
   ```
   Tab and Shift+Tab cycle focus. Use `useFocusManager().focus(id)` for programmatic control.

7. **Display streaming logs with Static**
   ```tsx
   import {useState, useEffect} from 'react';
   import {render, Static, Box, Text} from 'ink';

   function BuildOutput() {
    const [logs, setLogs] = useState<string[]>([]);
    const [current, setCurrent] = useState('Starting...');

    useEffect(() => {
    const timer = setInterval(() => {
    setLogs(prev => [...prev, current]);
    setCurrent(`Building step ${prev.length + 1}...`);
    }, 500);
    return () => clearInterval(timer);
    }, []);

    return (
    <Box flexDirection="column">
    <Static items={logs}>
    {(log, i) => <Text key={i} color="green"> {log}</Text>}
    </Static>
    <Text color="yellow"> {current}</Text>
    </Box>
    );
   }
   ```

8. **Use Suspense for async data**
   ```tsx
   import React, {Suspense} from 'react';
   import {render, Text} from 'ink';

   let data: string | undefined;
   let promise: Promise<void> | undefined;

   function fetchData() {
    if (data) return data;
    if (!promise) {
    promise = new Promise(resolve => {
    setTimeout(() => { data = 'Loaded!'; resolve(); }, 1000);
    });
    }
    throw promise;
   }

   function DataView() {
    const result = fetchData();
    return <Text color="green">{result}</Text>;
   }

   render(
    <Suspense fallback={<Text color="yellow">Loading...</Text>}>
    <DataView />
    </Suspense>
   );
   ```

9. **Respond to terminal resize**
   ```tsx
   import {useWindowSize, Box, Text} from 'ink';

   function ResponsiveLayout() {
    const {columns, rows} = useWindowSize();
    return (
    <Box flexDirection="column">
    <Text>Terminal: {columns}x{rows}</Text>
    <Box width={columns > 80 ? '50%' : '100%'}>
    <Text>Content adapts to terminal size</Text>
    </Box>
    </Box>
    );
   }
   ```

## Pitfalls

1. **Raw text inside `<Box>` silently breaks rendering** - Placing a string directly inside `<Box>` without wrapping it in `<Text>` causes a runtime error. Unlike web React where a `<div>` can contain bare text, Ink enforces that only `<Text>` components hold text content. Always wrap strings in `<Text>`.

2. **`useInput` does nothing without raw mode on stdin** - If stdin is not in raw mode (e.g., piped input in CI, non-TTY environments), `useInput` never fires. Check `useStdin().isRawModeSupported` before relying on keyboard input, and provide a non-interactive fallback for CI/piped contexts.

3. **Ink v6 is ESM-only and breaks CommonJS imports** - Importing Ink with `require('ink')` throws `require() of ES Module`. You must use `import` syntax and set `"type": "module"` in your `package.json`. This also means Ink v6 cannot be used in projects that are stuck on CommonJS without a build step.

4. **`<Static>` items must have stable keys or they re-render** - The `<Static>` component renders each item exactly once and never updates it. If you pass items without stable `key` props or if you mutate the items array in place instead of appending, previously rendered lines can disappear or duplicate.

5. **The app stays alive as long as stdin listeners or timers exist** - Ink's `render()` keeps the process running while there are pending timers, promises, or stdin listeners. Forgetting to call `clearInterval`, `clearTimeout`, or `exit()` from `useApp()` results in a CLI tool that hangs after the work is done.

6. **`stdin.setRawMode is not a function`** - Running in non-TTY environment (piped input, CI). Check `isRawModeSupported` from `useStdin()` before enabling.

7. **`React is not defined`** - Missing React import with JSX transform. Add `import React from 'react'` or configure JSX automatic runtime.

## Verification

1. Check Node version: `node -v` (must be >= 20)
2. Check package.json for `"type": "module"` if using Ink v6+
3. Run the CLI app: `node dist/index.js` or `npm start`
4. Verify interactive input works in a real terminal (not piped)
5. Verify the process exits cleanly after completion (no hanging)
6. Verify no raw text is placed directly inside `<Box>` components

## UI/UX 2026 Guidelines

This skill also covers interface design, UX review, accessibility, responsive layouts, design systems, mobile/web UI, component behavior, interaction states, visual hierarchy, usability improvements, and frontend implementation guidance.

**Workflow:**
1. Start from the user task and information architecture, not decoration.
2. Map key states: empty, loading, success, error, disabled, permission-limited, offline, and responsive variants.
3. Apply accessibility requirements early: keyboard flow, focus visibility, labels, contrast, reduced motion, touch targets, text resizing, and semantic structure.
4. Use design-system primitives where available; otherwise define tokens for spacing, color, type, elevation, radius, and motion.
5. Design responsive layouts with stable dimensions and no text overlap across desktop and mobile.
6. Validate with realistic content, long labels, error text, and touch/keyboard interaction.
7. Deliver concrete implementation guidance, not vague aesthetic notes.

**Quality Checklist:**
- User can complete the core task quickly and repeatedly.
- UI supports keyboard, screen readers, visible focus, and sufficient contrast.
- Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
- Controls use familiar affordances and expose state clearly.
- Motion is purposeful and respects reduced-motion preferences.
- Visual direction is intentional and consistent with the product domain.

**Failure Handling:**
If requirements conflict, prioritize usability, accessibility, and product fit over novelty. If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant. Verify current platform guidance when building for Apple, Android, or a specific design system.

**Current References:**
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html

## References

This skill does not ship a companion pack. Box/Text/hooks usage is in Procedure above. Full props, community components, and example apps:

- Ink README (components + hooks): https://github.com/vadimdemedes/ink
- Examples: https://github.com/vadimdemedes/ink/tree/master/examples

## Related skills

- frontend-developer: For general React web or React Native development.
- shell-scripting: For simple shell scripts that just print output.
