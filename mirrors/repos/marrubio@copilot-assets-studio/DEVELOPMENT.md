# Local Development

Requires Node.js, npm, and Visual Studio Code 1.106.0 or newer. The extension
does not require a build step.

## Install dependencies

From the project root, run:

```bash
npm install
```

## Run the extension locally

1. Open this project in Visual Studio Code.
2. Press `F5`, or open **Run and Debug** and select **Run Extension**. This opens
   an **Extension Development Host** window with the extension loaded.
3. In the development host, create `.github/agents/test.agent.md` with:

   ```markdown
   ---
   name: Test Agent
   description: A test agent for Copilot Assets Studio
   tools:
     - read
     - search
   ---

   You are a test agent.
   ```

4. Open **Copilot Assets** in the activity bar and select the test agent.
5. Change a field, click **Save**, and verify that the Markdown file was updated.

To debug the extension, set breakpoints in `src/extension.js` and reload the
Extension Development Host with `Ctrl+R`.

## Tests and lint

```bash
npm test
npm run lint
```

## Package and install a VSIX

Create a package from the project root:

```bash
npx --yes @vscode/vsce package
```

In VS Code, open **Extensions** (`Ctrl+Shift+X`), select the `...` menu, and
choose **Install from VSIX...**. Select the generated
`copilot-assets-studio-x.y.z.vsix` file and reload VS Code if prompted.
