#!/usr/bin/env node

/**
 * Build analysis script for monitoring code splitting effectiveness
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DIST_DIR = path.join(__dirname, '../dist');
const ASSETS_DIR = path.join(DIST_DIR, 'assets');
const JS_DIR = path.join(ASSETS_DIR, 'js');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function formatBytes(bytes) {
  const sizes = ['B', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 B';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
}

function getChunkInfo() {
  if (!fs.existsSync(JS_DIR)) {
    console.error(`${colors.red}Build directory not found. Run 'npm run build' first.${colors.reset}`);
    process.exit(1);
  }

  const chunks = [];
  const files = fs.readdirSync(JS_DIR);

  files.forEach(file => {
    if (file.endsWith('.js')) {
      const filePath = path.join(JS_DIR, file);
      const stats = fs.statSync(filePath);
      const content = fs.readFileSync(filePath, 'utf-8');
      
      // Extract chunk name from filename
      const chunkName = file.replace(/\.[a-f0-9]+\.js$/, '');
      
      // Count imports and exports
      const imports = (content.match(/import\s+/g) || []).length;
      const exports = (content.match(/export\s+/g) || []).length;
      
      chunks.push({
        name: chunkName,
        file: file,
        size: stats.size,
        gzipSize: getGzipSize(filePath),
        imports,
        exports,
      });
    }
  });

  return chunks.sort((a, b) => b.size - a.size);
}

function getGzipSize(filePath) {
  try {
    const gzipFile = `${filePath}.gz`;
    if (fs.existsSync(gzipFile)) {
      return fs.statSync(gzipFile).size;
    }
    // Estimate gzip size if .gz file doesn't exist
    const content = fs.readFileSync(filePath);
    const zlib = require('zlib');
    return zlib.gzipSync(content).length;
  } catch {
    return 0;
  }
}

function analyzeChunks(chunks) {
  const analysis = {
    totalSize: 0,
    totalGzipSize: 0,
    chunkCount: chunks.length,
    largestChunk: null,
    smallestChunk: null,
    vendorChunks: [],
    appChunks: [],
    recommendations: [],
  };

  chunks.forEach(chunk => {
    analysis.totalSize += chunk.size;
    analysis.totalGzipSize += chunk.gzipSize;

    if (!analysis.largestChunk || chunk.size > analysis.largestChunk.size) {
      analysis.largestChunk = chunk;
    }
    if (!analysis.smallestChunk || chunk.size < analysis.smallestChunk.size) {
      analysis.smallestChunk = chunk;
    }

    // Categorize chunks
    if (chunk.name.includes('vendor') || chunk.name.includes('node_modules')) {
      analysis.vendorChunks.push(chunk);
    } else {
      analysis.appChunks.push(chunk);
    }

    // Generate recommendations
    if (chunk.size > 244 * 1024) { // 244KB warning threshold
      analysis.recommendations.push({
        type: 'warning',
        chunk: chunk.name,
        message: `Chunk exceeds recommended size (${formatBytes(chunk.size)}). Consider splitting.`,
      });
    }
  });

  return analysis;
}

function printReport(chunks, analysis) {
  console.log(`\n${colors.bright}${colors.blue}📊 Build Analysis Report${colors.reset}\n`);
  
  // Summary
  console.log(`${colors.cyan}Summary:${colors.reset}`);
  console.log(`  Total chunks: ${analysis.chunkCount}`);
  console.log(`  Total size: ${formatBytes(analysis.totalSize)}`);
  console.log(`  Total gzip size: ${formatBytes(analysis.totalGzipSize)}`);
  console.log(`  Compression ratio: ${((1 - analysis.totalGzipSize / analysis.totalSize) * 100).toFixed(1)}%`);
  console.log('');

  // Chunk details
  console.log(`${colors.cyan}Chunks (sorted by size):${colors.reset}`);
  console.log('  ' + '-'.repeat(80));
  console.log('  ' + 
    'Chunk Name'.padEnd(30) + 
    'Size'.padEnd(12) + 
    'Gzip'.padEnd(12) + 
    'Ratio'.padEnd(8) +
    'Type'
  );
  console.log('  ' + '-'.repeat(80));

  chunks.forEach(chunk => {
    const ratio = ((1 - chunk.gzipSize / chunk.size) * 100).toFixed(1);
    const type = chunk.name.includes('vendor') ? 'vendor' : 'app';
    const sizeColor = chunk.size > 244 * 1024 ? colors.yellow : colors.green;
    
    console.log('  ' +
      chunk.name.padEnd(30) +
      (sizeColor + formatBytes(chunk.size) + colors.reset).padEnd(20) +
      formatBytes(chunk.gzipSize).padEnd(12) +
      (ratio + '%').padEnd(8) +
      type
    );
  });
  console.log('  ' + '-'.repeat(80));

  // Recommendations
  if (analysis.recommendations.length > 0) {
    console.log(`\n${colors.cyan}Recommendations:${colors.reset}`);
    analysis.recommendations.forEach(rec => {
      const icon = rec.type === 'warning' ? '⚠️ ' : 'ℹ️ ';
      const color = rec.type === 'warning' ? colors.yellow : colors.blue;
      console.log(`  ${color}${icon} ${rec.chunk}: ${rec.message}${colors.reset}`);
    });
  }

  // Build strategy effectiveness
  console.log(`\n${colors.cyan}Code Splitting Effectiveness:${colors.reset}`);
  const avgChunkSize = analysis.totalSize / analysis.chunkCount;
  console.log(`  Average chunk size: ${formatBytes(avgChunkSize)}`);
  console.log(`  Vendor/App ratio: ${analysis.vendorChunks.length}:${analysis.appChunks.length}`);
  
  const vendorSize = analysis.vendorChunks.reduce((sum, c) => sum + c.size, 0);
  const appSize = analysis.appChunks.reduce((sum, c) => sum + c.size, 0);
  console.log(`  Vendor size: ${formatBytes(vendorSize)} (${(vendorSize / analysis.totalSize * 100).toFixed(1)}%)`);
  console.log(`  App size: ${formatBytes(appSize)} (${(appSize / analysis.totalSize * 100).toFixed(1)}%)`);

  // Success metrics
  console.log(`\n${colors.cyan}Success Metrics:${colors.reset}`);
  const metrics = {
    'Chunks under 244KB': chunks.filter(c => c.size < 244 * 1024).length,
    'Chunks under 100KB': chunks.filter(c => c.size < 100 * 1024).length,
    'Chunks under 50KB': chunks.filter(c => c.size < 50 * 1024).length,
  };
  
  Object.entries(metrics).forEach(([label, count]) => {
    const percentage = (count / chunks.length * 100).toFixed(1);
    console.log(`  ${label}: ${count}/${chunks.length} (${percentage}%)`);
  });
}

function generateHTMLReport(chunks, analysis) {
  const html = `
<!DOCTYPE html>
<html>
<head>
  <title>Build Analysis Report</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
    h1 { color: #333; }
    .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
    .metric { background: #f8f9fa; padding: 15px; border-radius: 4px; }
    .metric h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
    .metric .value { font-size: 24px; font-weight: bold; color: #333; }
    .chart-container { width: 100%; height: 400px; margin: 20px 0; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #f8f9fa; font-weight: bold; }
    .warning { color: #ff9800; }
    .success { color: #4caf50; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Build Analysis Report</h1>
    <div class="summary">
      <div class="metric">
        <h3>Total Chunks</h3>
        <div class="value">${analysis.chunkCount}</div>
      </div>
      <div class="metric">
        <h3>Total Size</h3>
        <div class="value">${formatBytes(analysis.totalSize)}</div>
      </div>
      <div class="metric">
        <h3>Gzip Size</h3>
        <div class="value">${formatBytes(analysis.totalGzipSize)}</div>
      </div>
      <div class="metric">
        <h3>Compression</h3>
        <div class="value">${((1 - analysis.totalGzipSize / analysis.totalSize) * 100).toFixed(1)}%</div>
      </div>
    </div>
    
    <h2>Chunk Size Distribution</h2>
    <canvas id="chunkChart"></canvas>
    
    <h2>Chunk Details</h2>
    <table>
      <tr>
        <th>Chunk Name</th>
        <th>Size</th>
        <th>Gzip Size</th>
        <th>Compression</th>
        <th>Type</th>
      </tr>
      ${chunks.map(chunk => `
        <tr>
          <td>${chunk.name}</td>
          <td class="${chunk.size > 244 * 1024 ? 'warning' : 'success'}">${formatBytes(chunk.size)}</td>
          <td>${formatBytes(chunk.gzipSize)}</td>
          <td>${((1 - chunk.gzipSize / chunk.size) * 100).toFixed(1)}%</td>
          <td>${chunk.name.includes('vendor') ? 'vendor' : 'app'}</td>
        </tr>
      `).join('')}
    </table>
  </div>
  
  <script>
    const ctx = document.getElementById('chunkChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ${JSON.stringify(chunks.map(c => c.name))},
        datasets: [{
          label: 'Size (KB)',
          data: ${JSON.stringify(chunks.map(c => c.size / 1024))},
          backgroundColor: ${JSON.stringify(chunks.map(c => c.size > 244 * 1024 ? '#ff9800' : '#4caf50'))},
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Size (KB)'
            }
          }
        }
      }
    });
  </script>
</body>
</html>
  `;

  const reportPath = path.join(DIST_DIR, 'build-analysis.html');
  fs.writeFileSync(reportPath, html);
  console.log(`\n${colors.green}✅ HTML report generated: ${reportPath}${colors.reset}`);
}

// Main execution
console.log(`${colors.bright}${colors.cyan}🔍 Analyzing build output...${colors.reset}`);

const chunks = getChunkInfo();
const analysis = analyzeChunks(chunks);

printReport(chunks, analysis);
generateHTMLReport(chunks, analysis);

// Exit with error if there are warnings
const hasWarnings = analysis.recommendations.some(r => r.type === 'warning');
process.exit(hasWarnings ? 1 : 0);