#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import gradient from 'gradient-string';
import figlet from 'figlet';
import Conf from 'conf';
import { password } from '@inquirer/prompts';
import { writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { generateCoverImage } from '../src/geminiGenerator.js';
import { fetchLogo } from '../src/logoFetcher.js';
import { validateImage } from '../src/imageValidator.js';

const config = new Conf({ projectName: 'blog-cover-image-cli' });
const program = new Command();

// Display banner
console.log(
  gradient(['#00ff00', '#00cc00', '#009900']).multiline(
    figlet.textSync('Blog Cover CLI', { font: 'ANSI Shadow', horizontalLayout: 'full' })
  )
);

async function getApiKey() {
  let apiKey = config.get('GEMINI_API_KEY');
  if (!apiKey) {
    console.log(chalk.yellow('Gemini API Key not found.'));
    try {
      apiKey = await password({
        message: 'Enter your Gemini API Key:',
        validate: (value) => value.length > 0 || 'API Key cannot be empty',
      });
      config.set('GEMINI_API_KEY', apiKey);
      console.log(chalk.green('API Key saved successfully.'));
    } catch (error) {
      if (error.name === 'ExitPromptError') {
        console.log(chalk.red('\nOperation cancelled.'));
        process.exit(0);
      }
      throw error;
    }
  }
  return apiKey;
}
async function getBrandfetchId() {
  let brandfetchId = config.get('BRANDFETCH_CLIENT_ID');
  if (!brandfetchId) {
    console.log(chalk.yellow('Brandfetch Client ID not found.'));
    try {
      brandfetchId = await password({
        message: 'Enter your Brandfetch Client ID:',
        validate: (value) => value.length > 0 || 'Client ID cannot be empty',
      });
      config.set('BRANDFETCH_CLIENT_ID', brandfetchId);
      console.log(chalk.green('Brandfetch Client ID saved successfully.'));
    } catch (error) {
      if (error.name === 'ExitPromptError') {
        console.log(chalk.red('\nOperation cancelled.'));
        process.exit(0);
      }
      throw error;
    }
  }
  return brandfetchId;
}


program
  .name('blog-cover-cli')
  .description('CLI to generate blog cover images using Gemini')
  .version('1.0.0');

const configCmd = program.command('config').description('Manage configuration');

configCmd
  .command('set-key')
  .description('Set Gemini API Key')
  .argument('<key>', 'Gemini API Key')
  .action((key) => {
    config.set('GEMINI_API_KEY', key);
    console.log(chalk.green('Gemini API Key updated.'));
  });

configCmd
  .command('get-key')
  .description('Get Gemini API Key (masked)')
  .action(() => {
    const key = config.get('GEMINI_API_KEY');
    if (key) {
      const masked = key.slice(0, 4) + '*'.repeat(key.length - 8) + key.slice(-4);
      console.log(`GEMINI_API_KEY: ${chalk.blue(masked)}`);
    } else {
      console.log(chalk.yellow('No API Key set.'));
    }
  });

configCmd
  .command('delete-key')
  .description('Delete Gemini API Key')
  .action(() => {
    config.delete('GEMINI_API_KEY');
    console.log(chalk.green('Gemini API Key deleted.'));
  });
configCmd
  .command('set-brandfetch-id')
  .description('Set Brandfetch Client ID')
  .argument('<id>', 'Brandfetch Client ID')
  .action((id) => {
    config.set('BRANDFETCH_CLIENT_ID', id);
    console.log(chalk.green('Brandfetch Client ID updated.'));
  });

configCmd
  .command('get-brandfetch-id')
  .description('Get Brandfetch Client ID (masked)')
  .action(() => {
    const id = config.get('BRANDFETCH_CLIENT_ID');
    if (id) {
      const masked = id.slice(0, 4) + '*'.repeat(Math.max(0, id.length - 8)) + id.slice(-4);
      console.log(`BRANDFETCH_CLIENT_ID: ${chalk.blue(masked)}`);
    } else {
      console.log(chalk.yellow('No Brandfetch Client ID set.'));
    }
  });

configCmd
  .command('delete-brandfetch-id')
  .description('Delete Brandfetch Client ID')
  .action(() => {
    config.delete('BRANDFETCH_CLIENT_ID');
    console.log(chalk.green('Brandfetch Client ID deleted.'));
  });


program
  .command('generate', { isDefault: true })
  .description('Generate a blog cover image')
  .option('-t, --title <title>', 'Blog post title')
  .option('-l, --logo <logo>', 'Logo domain or URL')
  .option('-o, --output <path>', 'Output file path')
  .action(async (options) => {
    try {
      let { title, logo, output } = options;

      if (!title) {
        console.error(chalk.red('Error: Title is required. Use -t or --title.'));
        process.exit(1);
      }

      const apiKey = await getApiKey();

      console.log(chalk.blue('Fetching logo...'));
      let logoData = null;
      if (logo) {
        const brandfetchId = await getBrandfetchId();
        logoData = await fetchLogo(logo, brandfetchId);
        if (!logoData) {
          console.log(chalk.yellow(`Warning: Could not fetch logo for "${logo}". Proceeding without logo.`));
        }
      }

      console.log(chalk.blue('Generating image...'));
      
      const MAX_RETRIES = 3;
      let attempt = 1;
      let criticalFeedback = null;
      let finalImage = null;
      let finalOutput = null;
      let validation = { isValid: false, issues: '' };

      while (attempt <= MAX_RETRIES) {
        const { base64Image, textOutput } = await generateCoverImage(title, logoData, apiKey, criticalFeedback);
        
        console.log(chalk.blue(`Validating image (Attempt ${attempt}/${MAX_RETRIES})...`));
        validation = await validateImage(base64Image, title, !!logoData, apiKey);

        finalImage = base64Image;
        finalOutput = textOutput;

        if (validation.isValid) {
          break;
        } else if (attempt < MAX_RETRIES) {
          console.log(chalk.yellow(`QA Failed: ${validation.issues}. Regenerating (Attempt ${attempt + 1}/${MAX_RETRIES})...`));
          criticalFeedback = validation.issues;
        }
        attempt++;
      }

      if (!validation.isValid) {
        console.log(chalk.red(`\nWarning: QA failed after ${MAX_RETRIES} attempts. Saving the last generated image anyway.`));
        console.log(chalk.yellow(`Final issues: ${validation.issues}`));
      }

      if (!output) {
        // Smart default filename inside an "output" directory
        const namePart = logo ? logo.split('.')[0] : title.toLowerCase().replace(/[^a-z0-9]/g, '-').slice(0, 20);
        output = path.join(process.cwd(), 'output', `${namePart}-cover.png`);
      } else {
        output = path.resolve(process.cwd(), output);
      }

      // Ensure directory exists
      await mkdir(path.dirname(output), { recursive: true });

      const buffer = Buffer.from(finalImage, 'base64');
      await writeFile(output, buffer);

      console.log(chalk.green(`\nSuccess! Image saved to: ${chalk.bold(output)}`));
      if (finalOutput.trim()) {
        console.log(chalk.gray('\nGemini Output:'));
        console.log(finalOutput);
      }
    } catch (error) {
      console.error(chalk.red('\nError:'), error.message);
      process.exit(1);
    }
  });

// Handle Ctrl+C
process.on('SIGINT', () => {
  console.log(chalk.red('\nProcess terminated.'));
  process.exit(0);
});

program.parse();
