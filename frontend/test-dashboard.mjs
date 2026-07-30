import { getPortfolioItems, getPerformance } from './src/services/index.js';

async function testDashboard() {
  try {
    console.log('Testing portfolio items fetch...');
    const items = await getPortfolioItems();
    console.log(`✓ Portfolio items: ${items.length} items loaded`);
    
    const nonCashItems = items.filter(i => i.assetType !== 'cash');
    console.log(`  - Non-cash holdings: ${nonCashItems.length}`);
    console.log(`  - Tickers: ${nonCashItems.map(i => i.ticker).join(', ')}`);
    
    const totalValue = items.reduce((sum, item) => sum + (item.marketValue || 0), 0);
    console.log(`  - Total portfolio value: $${totalValue.toFixed(2)}`);
    
    const cashItem = items.find(i => i.ticker === 'CASH');
    if (cashItem) {
      console.log(`  - Cash balance: $${cashItem.quantity.toFixed(2)}`);
    }
    
    console.log('\nTesting performance data fetch...');
    const performance = await getPerformance('all');
    console.log(`✓ Performance data: ${performance.length} days loaded`);
    console.log(`  - Date range: ${performance[0].date} to ${performance[performance.length-1].date}`);
    console.log(`  - Value range: $${Math.min(...performance.map(d => d.totalValue)).toFixed(0)} - $${Math.max(...performance.map(d => d.totalValue)).toFixed(0)}`);
    
    console.log('\n✓ All dashboard data loaded successfully!');
    process.exit(0);
  } catch (error) {
    console.error('✗ Error:', error.message);
    process.exit(1);
  }
}

testDashboard();
