#!/usr/bin/env node
/**
 * Quick check that Vercel Analytics loads without errors
 */
import { chromium } from 'playwright';

const PORT = process.env.PORT || 8080;
const BASE_URL = `http://localhost:${PORT}`;

async function checkAnalytics() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  page.on('pageerror', err => {
    errors.push(err.message);
  });

  try {
    console.log('Loading page...');
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    // Wait a bit for modules to load
    await page.waitForTimeout(2000);
    
    // Check if analytics was initialized
    const analyticsLoaded = await page.evaluate(() => {
      return typeof window.va === 'function';
    });
    
    if (errors.length > 0) {
      console.error('❌ Errors detected:');
      errors.forEach(err => console.error('  ', err));
      await browser.close();
      process.exit(1);
    }
    
    if (analyticsLoaded) {
      console.log('✅ Vercel Analytics loaded successfully!');
      console.log('✅ window.va function is available');
    } else {
      console.log('⚠️  window.va not found (may be expected in local dev)');
    }
    
  } catch (err) {
    console.error('❌ Test failed:', err.message);
    await browser.close();
    process.exit(1);
  }
  
  await browser.close();
  console.log('✅ Analytics check passed - no console errors');
}

checkAnalytics().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
