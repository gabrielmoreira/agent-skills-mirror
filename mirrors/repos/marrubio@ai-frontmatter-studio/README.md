# 🤖 ai-frontmatter-studio

Visually edit the YAML frontmatter of AI artifacts.

## 🚀 Current MVP

This project contains a minimal Visual Studio Code extension that:

- discovers Copilot/Agent Customizations assets in the workspace
- displays a **Copilot Assets** sidebar tree with Agents, Skills, Instructions, Prompts, MCP Servers, and Plugins
- lets you create and edit `*.agent.md` files through a visual form
- shows collapsible, live validation and advice in the agent form (including YAML errors, unknown properties, and GitHub cloud's 30,000-character instruction limit)
- shows separate approximate token counts for YAML frontmatter and Markdown, plus their total, in agent, prompt, and skill forms; each section uses UTF-8 bytes / 4 (rounded up), not a model-specific bill or total conversation cost
- lets you create and edit `SKILL.md` files through a visual form
- lets you create and edit `*.prompt.md` files through a visual form
- supports the officially documented properties for agent frontmatter:
  - `name`
  - `description`
  - `argument-hint`
  - `tools`
  - `agents`
  - `model`
  - `user-invocable`
  - `disable-model-invocation`
  - `infer` (deprecated)
  - `target`
  - `mcp-servers`
  - `handoffs`
  - `hooks` (preview)
  - `metadata`
- preserves extra properties through an advanced YAML block

The `model` field is edited through a selector. The default list can be customized
in VS Code settings with `aiFrontmatterStudio.modelOptions`, for example:

```json
{
  "aiFrontmatterStudio.modelOptions": [
    "GPT-5 (copilot)",
    "Claude Sonnet 4.5 (copilot)"
  ]
}
```

## 🧪 Scripts

```bash
npm test
npm run lint
```

## 🛠️ Test the extension in Visual Studio Code

1. Install the dependencies from the integrated terminal:

  ```bash
  npm install
  ```

2. Press `F5`, or open **Run and Debug** and select **Run Extension**. VS Code will open an **Extension Development Host** window with the extension loaded.

3. In the development window, create a `.github/agents/test.agent.md` file with the following content:

  ```markdown
  ---
  name: Test Agent
  description: A test agent for AI Frontmatter Studio
  tools:
    - read
    - search
  ---

  You are a test agent.
  ```

4. Open the **Copilot Assets** view in the activity bar. The file should appear under **Agents**.

5. Click the agent to open the visual editor, modify a field, and click **Save**. Verify that the Markdown file was updated.

To debug the extension, set breakpoints in `src/extension.js` and reload the **Extension Development Host** window with `Ctrl+R`.

The extension does not require a build step. `npm install` is required because the parser uses the `yaml` package.

## References

- Repository: https://github.com/marrubio/ai-frontmatter-studio
- VS Code extension documentation: https://code.visualstudio.com/api
- Publishing VS Code extensions: https://code.visualstudio.com/api/working-with-extensions/publishing-extension
- GitHub Copilot custom agents: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- VS Code custom agents: https://code.visualstudio.com/docs/agent-customization/custom-agents
- GitHub Copilot agent skills: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- VS Code prompt files: https://code.visualstudio.com/docs/agent-customization/prompt-files
