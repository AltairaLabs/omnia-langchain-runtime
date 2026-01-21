/**
 * Link checker script for documentation
 * Starts preview server and checks for broken links
 */

import { spawn } from 'node:child_process';
import { LinkChecker } from 'linkinator';

const PORT = 4322;
const BASE_URL = `http://localhost:${PORT}`;

async function startPreviewServer() {
  return new Promise((resolve, reject) => {
    const server = spawn('npm', ['run', 'preview', '--', '--port', PORT.toString()], {
      stdio: ['ignore', 'pipe', 'pipe'],
      shell: true,
    });

    let started = false;

    server.stdout.on('data', (data) => {
      const output = data.toString();
      if (output.includes('localhost') && !started) {
        started = true;
        setTimeout(() => resolve(server), 1000);
      }
    });

    server.stderr.on('data', (data) => {
      console.error(data.toString());
    });

    server.on('error', reject);

    setTimeout(() => {
      if (!started) {
        reject(new Error('Server failed to start'));
      }
    }, 30000);
  });
}

async function checkLinks() {
  console.log('Building documentation...');

  const build = spawn('npm', ['run', 'build'], {
    stdio: 'inherit',
    shell: true,
  });

  await new Promise((resolve, reject) => {
    build.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`Build failed with code ${code}`));
    });
  });

  console.log('\nStarting preview server...');
  const server = await startPreviewServer();

  console.log(`\nChecking links at ${BASE_URL}...`);

  const checker = new LinkChecker();
  const results = await checker.check({
    path: BASE_URL,
    recurse: true,
    linksToSkip: [
      /^mailto:/,
      /^tel:/,
      /github\.com.*\/edit\//,
    ],
  });

  server.kill();

  const broken = results.links.filter((link) => link.state === 'BROKEN');
  const skipped = results.links.filter((link) => link.state === 'SKIPPED');

  console.log(`\n${'='.repeat(60)}`);
  console.log('Link Check Results');
  console.log('='.repeat(60));
  console.log(`Total links checked: ${results.links.length}`);
  console.log(`Broken links: ${broken.length}`);
  console.log(`Skipped links: ${skipped.length}`);

  if (broken.length > 0) {
    console.log('\n--- Broken Links ---');

    const groupedByUrl = {};
    for (const link of broken) {
      if (!groupedByUrl[link.url]) {
        groupedByUrl[link.url] = [];
      }
      groupedByUrl[link.url].push(link.parent);
    }

    for (const [url, parents] of Object.entries(groupedByUrl)) {
      console.log(`\n${url}`);
      console.log(`  Status: ${broken.find((l) => l.url === url).status || 'N/A'}`);
      console.log('  Found on:');
      for (const parent of parents) {
        console.log(`    - ${parent}`);
      }
    }

    process.exit(1);
  }

  console.log('\nAll links are valid!');
  process.exit(0);
}

checkLinks().catch((error) => {
  console.error('Error:', error.message);
  process.exit(1);
});
