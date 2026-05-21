# Blog Cover Generator Skill

This directory contains an OpenCode Skill for the `blog-cover-image-cli`. It allows AI agents to automatically generate blog cover images using the CLI tool.

## Overview

The skill provides a structured interface for agents to:
1. Generate cover images with specific titles and subtitles.
2. Use predefined themes (e.g., 'modern', 'minimal', 'tech').
3. Handle output paths and file naming conventions.

## Installation & Distribution

### For Users
To use this skill in your OpenCode environment:

1. **Direct Path**: Point your agent to this directory path in your configuration.
2. **Skill Package**: Zip the contents of this folder (including `SKILL.md`) into a `.skill` file.
   ```bash
   zip -r blog-cover-generator.skill agent-skill/blog-cover-generator/*
   ```
3. **Import**: Use the OpenCode skill import command to add it to your library.

### For Developers
- `SKILL.md`: This is the core definition file used by the AI agent to understand its capabilities. **Do not modify its structure unless you are updating the skill's logic.**
- `README.md`: This file (you are reading it) is for human developers and users to understand deployment.

## Requirements
- `blog-cover-image-cli` must be installed and available in the system PATH.
- Node.js environment for running the CLI.
