# AGENTS.md

## Project Overview

Dis na wan educational curriculum repository wey dem dey use teach web development fundamentals to beginners. Di curriculum na big 12-week course wey Microsoft Cloud Advocates make, get 24 hands-on lessons covering JavaScript, CSS, and HTML.

### Key Components

- **Educational Content**: 24 structured lessons wey dem organize inside project-based modules
- **Practical Projects**: Terrarium, Typing Game, Browser Extension, Space Game, Banking App, Code Editor, and AI Chat Assistant
- **Interactive Quizzes**: 48 quizzes wey get 3 questions each (pre/post-lesson assessments)
- **Multi-language Support**: Automated translations for 50+ languages through GitHub Actions
- **Technologies**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (for AI projects)

### Architecture

- Educational repository wey get lesson-based structure
- Every lesson folder get README, code examples, and solutions
- Standalone projects dey for separate directories (quiz-app, various lesson projects)
- Translation system dey use GitHub Actions (co-op-translator)
- Documentation dey serve through Docsify and e dey available as PDF

## Setup Commands

Dis repository na mainly for educational content consumption. For to work with specific projects:

### Main Repository Setup

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App Setup (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Start di development server
npm run build      # Build for production
npm run lint       # Run ESLint
```

### Bank Project API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Start API server
npm run lint       # Run ESLint
npm run format     # Format wit Prettier
```

### Browser Extension Projects

```bash
cd 5-browser-extension/solution
npm install
# Follow di browser-specific extension loading instructions
```

### Space Game Projects

```bash
cd 6-space-game/solution
npm install
# Open index.html for browser or use Live Server
```

### Chat Project (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Set GITHUB_TOKEN environment variable
python api.py
```

## Development Workflow

### For Content Contributors

1. **Fork di repository** go your GitHub account
2. **Clone your fork** for your machine
3. **Create new branch** for your changes
4. Make changes for lesson content or code examples
5. Test any code changes inside the relevant project directories
6. Submit pull requests based on contribution guidelines

### For Learners

1. Fork or clone di repository
2. Go through lesson directories one by one
3. Read README files for each lesson
4. Do pre-lesson quizzes at https://ff-quizzes.netlify.app/web/
5. Work through code examples inside lesson folders
6. Finish assignments and challenges
7. Do post-lesson quizzes

### Live Development

- **Documentation**: Run `docsify serve` for root (port 3000)
- **Quiz App**: Run `npm run dev` inside quiz-app directory
- **Projects**: Use VS Code Live Server extension for HTML projects
- **API Projects**: Run `npm start` for the API directories

## Testing Instructions

### Quiz App Testing

```bash
cd quiz-app
npm run lint       # Check for code style wahala
npm run build      # Make sure build dey successful
```

### Bank API Testing

```bash
cd 7-bank-project/api
npm run lint       # Check for code style wahala
node server.js     # Make sure say server fit start without any kasala
```

### General Testing Approach

- Dis na educational repository wey no get full automatic tests
- Manual testing dey focus on:
  - Code examples dey run without wahala
  - Links for documentation dey work well
  - Project build dey complete successful
  - Examples follow best practices

### Pre-submission Checks

- Run `npm run lint` for directories wey get package.json
- Check say markdown links dey valid
- Test code examples for browser or Node.js
- Confirm say translations keep correct structure

## Code Style Guidelines

### JavaScript

- Use modern ES6+ syntax
- Follow standard ESLint config wey projects get
- Use meaningful variable and function names for educational clarity
- Add comments wey explain concepts for learners
- Format using Prettier if e dey setup

### HTML/CSS

- Use semantic HTML5 elements
- Responsive design principles
- Clear class naming conventions
- Comments wey dey explain CSS techniques for learners

### Python

- PEP 8 style guidelines
- Clear, educational code examples
- Type hints where e go help learning

### Markdown Documentation

- Clear heading hierarchy
- Code blocks with language specification
- Links to extra resources
- Screenshots and images inside `images/` directories
- Alt text for images to support accessibility

### File Organization

- Lessons dey numbered one by one (1-getting-started-lessons, 2-js-basics, etc.)
- Every project get `solution/` and sometimes `start/` or `your-work/` directories
- Images for lesson-specific `images/` folders
- Translations dey inside `translations/{language-code}/` structure

## Build and Deployment

### Quiz App Deployment (Azure Static Web Apps)

The quiz-app dey configured for Azure Static Web Apps deployment:

```bash
cd quiz-app
npm run build      # Dey create dist/ folder
# Dey put for ground wit GitHub Actions workflow wen dem push for main
```

Azure Static Web Apps configuration:
- **App location**: `/quiz-app`
- **Output location**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Documentation PDF Generation

```bash
npm install                    # Install docsify-to-pdf
npm run convert               # Make PDF from docs
```

### Docsify Documentation

```bash
npm install -g docsify-cli    # Install Docsify all over di system
docsify serve                 # Run for localhost:3000
```

### Project-specific Builds

Every project directory fit get their own build process:
- Vue projects: `npm run build` dey create production bundles
- Static projects: No build step, just serve files directly

## Pull Request Guidelines

### Title Format

Use clear, descriptive titles wey show wetin change be:
- `[Quiz-app] Add new quiz for lesson X`
- `[Lesson-3] Fix typo for terrarium project`
- `[Translation] Add Spanish translation for lesson 5`
- `[Docs] Update setup instructions`

### Required Checks

Before you submit PR:

1. **Code Quality**:
   - Run `npm run lint` for the project directories wey e concern
   - Fix all lint errors and warnings

2. **Build Verification**:
   - Run `npm run build` if e necessary
   - Make sure no build errors

3. **Link Validation**:
   - Test all markdown links
   - Confirm image refs work

4. **Content Review**:
   - Proofread for spelling and grammar
   - Ensure code examples correct and educational
   - Confirm translations keep original meaning

### Contribution Requirements

- Agree to Microsoft CLA (automatic check for first PR)
- Follow [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- See [CONTRIBUTING.md](./CONTRIBUTING.md) for details
- Reference issue numbers for PR description if e get

### Review Process

- PRs go through maintainer and community review
- Educational clarity dey important
- Code examples suppose follow current best practices
- Translations go through accuracy and cultural appropriateness check

## Translation System

### Automated Translation

- Dey use GitHub Actions with co-op-translator workflow
- Translates to 50+ languages automatically
- Source files dey main directories
- Translated files dey inside `translations/{language-code}/`

### Adding Manual Translation Improvements

1. Find file for `translations/{language-code}/`
2. Make improvements but keep structure intact
3. Make sure code examples still dey run well
4. Test any quiz content wey localized

### Translation Metadata

Translated files get metadata header:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Debugging and Troubleshooting

### Common Issues

**Quiz app no fit start**:
- Check Node.js version (v14+ recommended)
- Delete `node_modules` and `package-lock.json`, run `npm install` again
- Check for port wahala (default: Vite dey use port 5173)

**API server no go start**:
- Confirm Node.js version dey at least (node >=10)
- Check if port don already dey use
- Make sure all dependencies install with `npm install`

**Browser extension no go load**:
- Confirm manifest.json format correct
- Check browser console for errors
- Follow browser extension installation instructions

**Python chat project wahala**:
- Confirm OpenAI package install: `pip install openai`
- Confirm GITHUB_TOKEN environment variable set
- Check GitHub Models permission

**Docsify no dey serve docs**:
- Install docsify-cli globally: `npm install -g docsify-cli`
- Run am from root directory
- Check say `docs/_sidebar.md` dey

### Development Environment Tips

- Use VS Code with Live Server extension for HTML projects
- Install ESLint and Prettier extensions for proper formatting
- Use browser DevTools for JavaScript debugging
- For Vue projects, install Vue DevTools browser extension

### Performance Considerations

- Plenty translated files (50+ languages) mean big clones
- Use shallow clone if na content only: `git clone --depth 1`
- Exclude translations from searches if you dey focus on English
- Build steps fit slow for first time (npm install, Vite build)

## Security Considerations

### Environment Variables

- API keys no suppose commit to repository
- Use `.env` files (already for `.gitignore`)
- Document needed environment variables inside project READMEs

### Python Projects

- Use virtual environments: `python -m venv venv`
- Keep dependencies updated
- GitHub tokens need minimal permissions

### GitHub Models Access

- Personal Access Tokens (PAT) required for GitHub Models
- Tokens suppose dey stored as environment variables
- Never commit tokens or credentials

## Additional Notes

### Target Audience

- Complete beginners to web development
- Students and self-learners
- Teachers wey use the curriculum for classroom
- Content dey designed for accessibility and gradual skill building

### Educational Philosophy

- Project-based learning style
- Frequent knowledge checks (quizzes)
- Hands-on coding exercises
- Real-life application examples
- Focus on fundamentals before frameworks

### Repository Maintenance

- Active learner and contributor community
- Regular updates to content and dependencies
- Maintainers dey monitor issues and discussions
- Translation updates automated via GitHub Actions

### Related Resources

- [Microsoft Learn modules](https://docs.microsoft.com/learn/)
- [Student Hub resources](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) dey recommended for learners
- Other courses: Generative AI, Data Science, ML, IoT curricula dey available

### Working with Specific Projects

For detailed instructions on individual projects, check README files for:
- `quiz-app/README.md` - Vue 3 quiz application
- `7-bank-project/README.md` - Banking app with authentication
- `5-browser-extension/README.md` - Browser extension development
- `6-space-game/README.md` - Canvas-based game development
- `9-chat-project/README.md` - AI chat assistant project

### Monorepo Structure

Even though dis no be traditional monorepo, dis repository get many independent projects:
- Every lesson dey self-contained
- Projects no dey share dependencies
- You fit work on individual projects without affect others
- Clone whole repo for full curriculum experience

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Disclaimer**:  
Dis dokument don translate wit AI translation service [Co-op Translator](https://github.com/Azure/co-op-translator). Even tho we dey try make am correct, abeg sabi say automated translations fit get errors or mistakes. Di original dokument for im own language na di correct source. For important information, better human translation na di best. We no get fault if any misunderstanding or wrong understanding happen because of dis translation.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->