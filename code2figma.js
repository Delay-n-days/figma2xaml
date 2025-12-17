// ========================================
// 快速绘图代码示例 - 直接复制使用
// 复制以下任意代码到 code.js，保存后按 Ctrl/Cmd + Alt + P 运行
// ========================================

// 示例1: 画一个红色矩形
const rect = figma.createRectangle();
rect.x = 100;
rect.y = 100;
rect.resize(200, 150);
rect.fills = [{type: 'SOLID', color: {r: 1, g: 0, b: 0}}];
figma.currentPage.appendChild(rect);
figma.closePlugin();

// ========================================

// 示例2: 画多个不同颜色的圆形
const colors = [
  {r: 1, g: 0, b: 0},    // 红
  {r: 0, g: 1, b: 0},    // 绿
  {r: 0, g: 0, b: 1},    // 蓝
  {r: 1, g: 1, b: 0},    // 黄
  {r: 1, g: 0, b: 1}     // 紫
];

colors.forEach((color, i) => {
  const circle = figma.createEllipse();
  circle.x = i * 120;
  circle.y = 100;
  circle.resize(100, 100);
  circle.fills = [{type: 'SOLID', color: color}];
  figma.currentPage.appendChild(circle);
});

figma.closePlugin();

// ========================================

// 示例3: 画一个带阴影的卡片
const card = figma.createRectangle();
card.x = 100;
card.y = 100;
card.resize(300, 200);
card.cornerRadius = 12;
card.fills = [{type: 'SOLID', color: {r: 1, g: 1, b: 1}}];
card.effects = [{
  type: 'DROP_SHADOW',
  color: {r: 0, g: 0, b: 0, a: 0.2},
  offset: {x: 0, y: 4},
  radius: 8,
  visible: true,
  blendMode: 'NORMAL'
}];
figma.currentPage.appendChild(card);
figma.closePlugin();

// ========================================

// 示例4: 画一个渐变矩形
const gradient = figma.createRectangle();
gradient.x = 100;
gradient.y = 100;
gradient.resize(400, 200);
gradient.fills = [{
  type: 'GRADIENT_LINEAR',
  gradientStops: [
    {position: 0, color: {r: 1, g: 0, b: 0.5, a: 1}},
    {position: 1, color: {r: 0, g: 0.5, b: 1, a: 1}}
  ],
  gradientTransform: [[1, 0, 0], [0, 1, 0]]
}];
figma.currentPage.appendChild(gradient);
figma.closePlugin();

// ========================================

// 示例5: 画一个网格
const rows = 5;
const cols = 5;
const size = 50;
const gap = 10;

for (let row = 0; row < rows; row++) {
  for (let col = 0; col < cols; col++) {
    const square = figma.createRectangle();
    square.x = col * (size + gap);
    square.y = row * (size + gap);
    square.resize(size, size);
    square.fills = [{
      type: 'SOLID', 
      color: {
        r: row / rows, 
        g: col / cols, 
        b: 0.5
      }
    }];
    figma.currentPage.appendChild(square);
  }
}
figma.closePlugin();

// ========================================

// 示例6: 添加文本（需要先加载字体）
figma.loadFontAsync({ family: "Inter", style: "Regular" }).then(() => {
  const text = figma.createText();
  text.x = 100;
  text.y = 100;
  text.characters = "Hello Figma!";
  text.fontSize = 48;
  text.fills = [{type: 'SOLID', color: {r: 0, g: 0, b: 0}}];
  figma.currentPage.appendChild(text);
  figma.closePlugin();
});

// ========================================

// 示例7: 创建一组按钮
const buttonColors = [
  {name: '主要', color: {r: 0.2, g: 0.4, b: 1}},
  {name: '成功', color: {r: 0.2, g: 0.8, b: 0.4}},
  {name: '警告', color: {r: 1, g: 0.7, b: 0}},
  {name: '危险', color: {r: 1, g: 0.3, b: 0.3}}
];

figma.loadFontAsync({ family: "Inter", style: "Medium" }).then(() => {
  buttonColors.forEach((btn, i) => {
    const button = figma.createRectangle();
    button.x = i * 150;
    button.y = 100;
    button.resize(130, 40);
    button.cornerRadius = 6;
    button.fills = [{type: 'SOLID', color: btn.color}];
    
    const label = figma.createText();
    label.characters = btn.name;
    label.fontSize = 14;
    label.fontName = { family: "Inter", style: "Medium" };
    label.fills = [{type: 'SOLID', color: {r: 1, g: 1, b: 1}}];
    label.x = button.x + (button.width - label.width) / 2;
    label.y = button.y + (button.height - label.height) / 2;
    
    figma.currentPage.appendChild(button);
    figma.currentPage.appendChild(label);
  });
  figma.closePlugin();
});

// ========================================

// 示例8: 随机生成图形
function randomColor() {
  return {
    r: Math.random(),
    g: Math.random(),
    b: Math.random()
  };
}

for (let i = 0; i < 20; i++) {
  const shape = figma.createEllipse();
  shape.x = Math.random() * 800;
  shape.y = Math.random() * 600;
  const size = 30 + Math.random() * 70;
  shape.resize(size, size);
  shape.fills = [{type: 'SOLID', color: randomColor()}];
  shape.opacity = 0.6;
  figma.currentPage.appendChild(shape);
}
figma.closePlugin();

// ========================================

// 示例9: 画一个星形图案（用线条）
const centerX = 200;
const centerY = 200;
const radius = 100;
const points = 8;

for (let i = 0; i < points; i++) {
  const line = figma.createLine();
  const angle = (i * 2 * Math.PI) / points;
  
  line.x = centerX;
  line.y = centerY;
  line.resize(
    Math.cos(angle) * radius,
    Math.sin(angle) * radius
  );
  
  line.strokes = [{type: 'SOLID', color: {r: 0, g: 0, b: 0}}];
  line.strokeWeight = 2;
  
  figma.currentPage.appendChild(line);
}
figma.closePlugin();

// ========================================

// 示例10: 复制当前选中的元素
const selection = figma.currentPage.selection;

if (selection.length > 0) {
  selection.forEach(node => {
    const clone = node.clone();
    clone.x = node.x + 50;
    clone.y = node.y + 50;
    figma.currentPage.appendChild(clone);
  });
  figma.notify(`✅ 已复制 ${selection.length} 个元素`);
} else {
  figma.notify('⚠️ 请先选择要复制的元素');
}
figma.closePlugin();

// ========================================
// 使用说明：
// 1. 复制上面任意一段代码
// 2. 粘贴到你的 code.js 文件
// 3. 保存文件
// 4. 在 Figma 中按 Ctrl/Cmd + Alt + P
// 5. 就能看到效果了！
// ========================================