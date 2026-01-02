const fs = require('fs');
const path = require('path');

try {
  const envPath = path.resolve(process.cwd(), '.env');
  const envConfig = fs.readFileSync(envPath, 'utf8');
  console.log('Keys in .env:');
  envConfig.split('\n').forEach(line => {
    const match = line.match(/^([^=]+)=/);
    if (match) {
      console.log(match[1]);
    }
  });
} catch (e) {
  console.error(e);
}
