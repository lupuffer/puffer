// 数据生成脚本 - 生成10万条商品数据
// 运行方式: node generateData.js

const fs = require('fs');
const path = require('path');

const TOTAL_COUNT = 100000;
const books = [];

for (let i = 1; i <= TOTAL_COUNT; i++) {
    books.push({
        id: i,
        name: `商品${i}`,
        price: parseFloat((Math.random() * 200 + 10).toFixed(2)),
        img: `./images/book${((i - 1) % 6) + 1}.jpg`
    });
}

const data = JSON.stringify(books, null, 2);
const outputPath = path.join(__dirname, 'data.json');

fs.writeFileSync(outputPath, data);

console.log(`✅ 数据生成完成！`);
console.log(`📊 总数量: ${TOTAL_COUNT} 条`);
console.log(`📁 文件路径: ${outputPath}`);
console.log(`📈 文件大小: ${(fs.statSync(outputPath).size / 1024 / 1024).toFixed(2)} MB`);
console.log('');
console.log('示例数据:', books[0]);