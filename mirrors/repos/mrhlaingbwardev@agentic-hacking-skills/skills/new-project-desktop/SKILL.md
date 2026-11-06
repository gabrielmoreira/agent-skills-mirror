---
name: new-project-desktop
description: Automatically creates a new project folder on Desktop when user asks to create or start a new project. Use when user says "create new project", "start new project", or similar requests.
---

# New Project on Desktop

When the user requests to create a new project, this skill ensures the project is created in a clean, organized folder on the Desktop.

## Workflow

1. **Ask for project name** (if not provided)
   - If the user hasn't specified a project name, ask them what to name the project
   - Use the project name exactly as provided

2. **Create project folder on Desktop**
   - Create a new folder at: `C:\Users\YourUser\Desktop\{project-name}`
   - If the folder already exists, ask the user if they want to:
     - Use the existing folder
     - Choose a different name
     - Overwrite the existing folder

3. **Navigate to the new folder**
   - Change the working directory to the newly created project folder

4. **Initialize the project**
   - Based on the project type requested (React, Node.js, Python, etc.), run the appropriate initialization commands
   - Create necessary files and folder structure
   - Install dependencies if applicable

5. **Confirm completion**
   - Show the user the full path of the created project
   - List the initial files/folders created

## Examples

**User**: "Create a new React project called my-app"
- Create folder: `C:\Users\YourUser\Desktop\my-app`
- Navigate to: `cd "C:\Users\YourUser\Desktop\my-app"`
- Run: `npx create-react-app .`

**User**: "Start a new Python project"
- Ask: "What would you like to name this project?"
- User responds: "data-analyzer"
- Create folder: `C:\Users\YourUser\Desktop\data-analyzer`
- Navigate and set up Python project structure

**User**: "Make a new Node.js API"
- Ask for project name if not specified
- Create Desktop folder
- Initialize with `npm init -y`
- Set up basic Express structure

## Important Notes

- Always create projects on Desktop: `C:\Users\YourUser\Desktop\`
- Always ask for confirmation before overwriting existing folders
- Keep folder names clean (lowercase, hyphens instead of spaces recommended)
- After creation, verify the folder exists and show the full path to the user
