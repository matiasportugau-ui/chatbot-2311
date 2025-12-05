#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Find all TypeScript files with merge conflicts
const files = execSync('grep -rl "^<<<<<<< Updated upstream" src/', { encoding: 'utf8' })
  .trim()
  .split('\n')
  .filter(Boolean);

console.log(`Found ${files.length} files with merge conflicts`);

files.forEach(file => {
  console.log(`Processing ${file}...`);
  let content = fs.readFileSync(file, 'utf8');

  // Remove merge conflict markers and keep the "Stashed changes" version
  // This is a simple approach - remove everything between <<<<<<< and ======= (Updated upstream)
  // and keep everything between ======= and >>>>>>> (Stashed changes)

  // Pattern: <<<<<<< Updated upstream ... ======= ... >>>>>>> Stashed changes
  content = content.replace(
    /<<<<<<< Updated upstream[\s\S]*?=======([\s\S]*?)>>>>>>> Stashed changes/g,
    '$1'
  );

  fs.writeFileSync(file, content, 'utf8');
  console.log(`  ✓ Resolved conflicts in ${file}`);
});

console.log('\nDone! Please review the changes and test the build.');


