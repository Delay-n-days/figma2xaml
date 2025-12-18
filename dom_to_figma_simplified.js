// ============================================
// 简化版：浏览器DOM → Figma Plugin 代码生成器
// ============================================

// ========== 第一步：浏览器端解析DOM ==========
function analyzeDOMNode(element) {
  const computed = window.getComputedStyle(element);
  const bounds = element.getBoundingClientRect();
  
  // 判断节点类型
  const nodeType = inferNodeType(element, computed);
  
  // 提取样式
  const styles = {
    // 尺寸
    width: Math.round(bounds.width),
    height: Math.round(bounds.height),
    
    // 颜色
    bgColor: cssToFigmaColor(computed.backgroundColor),
    textColor: cssToFigmaColor(computed.color),
    borderColor: cssToFigmaColor(computed.borderTopColor),
    
    // 布局
    display: computed.display,
    flexDirection: computed.flexDirection,
    gap: parseFloat(computed.gap) || 0,
    padding: parsePadding(computed),
    
    // 边框圆角
    borderWidth: parseFloat(computed.borderTopWidth) || 0,
    borderRadius: parseFloat(computed.borderRadius) || 0,
    
    // 文本
    fontSize: parseFloat(computed.fontSize) || 14,
    text: element.textContent?.trim() || ''
  };
  
  // 递归处理子节点
  const children = [];
  if (nodeType === 'container') {
    for (let child of element.children) {
      children.push(analyzeDOMNode(child));
    }
  }
  
  return {
    type: nodeType,
    styles: styles,
    children: children
  };
}

// 推断节点类型
function inferNodeType(element, computed) {
  // 纯文本节点
  if (element.children.length === 0 && element.textContent.trim()) {
    return 'text';
  }
  
  // 有背景色但无子元素 → 矩形
  const hasBg = computed.backgroundColor !== 'rgba(0, 0, 0, 0)';
  if (hasBg && element.children.length === 0) {
    return 'rectangle';
  }
  
  // 有子元素 → 容器
  return 'container';
}

// CSS颜色转Figma格式
function cssToFigmaColor(cssColor) {
  if (!cssColor || cssColor === 'rgba(0, 0, 0, 0)') {
    return null;
  }
  
  // rgba(r, g, b, a)
  const match = cssColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    return {
      r: parseInt(match[1]) / 255,
      g: parseInt(match[2]) / 255,
      b: parseInt(match[3]) / 255
    };
  }
  
  return {r: 0.5, g: 0.5, b: 0.5}; // 默认灰色
}

// 解析padding
function parsePadding(computed) {
  const top = parseFloat(computed.paddingTop) || 0;
  const right = parseFloat(computed.paddingRight) || 0;
  const bottom = parseFloat(computed.paddingBottom) || 0;
  const left = parseFloat(computed.paddingLeft) || 0;
  
  // 简化：如果四边相同，返回一个值
  if (top === right && right === bottom && bottom === left) {
    return top;
  }
  
  return {top, right, bottom, left};
}

// ========== 第二步：生成Figma Plugin代码 ==========
function generateFigmaPluginCode(layoutTree) {
  let code = `// Auto-generated Figma Plugin Code
async function loadFont() {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
}

function rect(w, h, c, r = 0) {
  const el = figma.createRectangle();
  el.resize(w, h);
  if (c) el.fills = [{type: 'SOLID', color: c}];
  if (r) el.cornerRadius = r;
  return el;
}

function txt(s, sz, c) {
  const t = figma.createText();
  t.characters = s;
  t.fontSize = sz;
  t.fontName = {family: "Inter", style: "Regular"};
  if (c) t.fills = [{type: 'SOLID', color: c}];
  return t;
}

function hStack(spacing = 0, padding = 0) {
  const f = figma.createFrame();
  f.layoutMode = 'HORIZONTAL';
  f.itemSpacing = spacing;
  f.paddingLeft = f.paddingRight = f.paddingTop = f.paddingBottom = padding;
  f.primaryAxisSizingMode = 'AUTO';
  f.counterAxisSizingMode = 'AUTO';
  f.fills = [];
  return f;
}

function vStack(spacing = 0, padding = 0) {
  const f = figma.createFrame();
  f.layoutMode = 'VERTICAL';
  f.itemSpacing = spacing;
  f.paddingLeft = f.paddingRight = f.paddingTop = f.paddingBottom = padding;
  f.primaryAxisSizingMode = 'AUTO';
  f.counterAxisSizingMode = 'AUTO';
  f.fills = [];
  return f;
}

async function generate() {
  await loadFont();
  
`;

  // 生成主逻辑
  code += generateNodeCode(layoutTree, 'root', 0);
  
  code += `
  figma.currentPage.appendChild(root);
  figma.viewport.scrollAndZoomIntoView([root]);
  figma.notify("✅ 界面生成完成!");
  figma.closePlugin();
}

generate();
`;

  return code;
}

// 递归生成节点代码
function generateNodeCode(node, varName, indent) {
  const ind = '  '.repeat(indent);
  let code = '';
  
  if (node.type === 'text') {
    // 文本节点
    code += `${ind}const ${varName} = txt("${node.styles.text}", ${node.styles.fontSize}, ${colorToString(node.styles.textColor)});\n`;
    
  } else if (node.type === 'rectangle') {
    // 矩形节点
    code += `${ind}const ${varName} = rect(${node.styles.width}, ${node.styles.height}, ${colorToString(node.styles.bgColor)}, ${node.styles.borderRadius});\n`;
    
    // 添加边框
    if (node.styles.borderWidth > 0) {
      code += `${ind}${varName}.strokes = [{type: 'SOLID', color: ${colorToString(node.styles.borderColor)}}];\n`;
      code += `${ind}${varName}.strokeWeight = ${node.styles.borderWidth};\n`;
    }
    
  } else if (node.type === 'container') {
    // 容器节点
    const isHorizontal = node.styles.flexDirection === 'row';
    const stackType = isHorizontal ? 'hStack' : 'vStack';
    const spacing = node.styles.gap;
    const padding = typeof node.styles.padding === 'number' ? node.styles.padding : 0;
    
    code += `${ind}const ${varName} = ${stackType}(${spacing}, ${padding});\n`;
    
    // 设置尺寸
    if (node.styles.width && node.styles.height) {
      code += `${ind}${varName}.resize(${node.styles.width}, ${node.styles.height});\n`;
      code += `${ind}${varName}.primaryAxisSizingMode = 'FIXED';\n`;
      code += `${ind}${varName}.counterAxisSizingMode = 'FIXED';\n`;
    }
    
    // 设置背景色
    if (node.styles.bgColor) {
      code += `${ind}${varName}.fills = [{type: 'SOLID', color: ${colorToString(node.styles.bgColor)}}];\n`;
    }
    
    // 设置边框
    if (node.styles.borderWidth > 0) {
      code += `${ind}${varName}.strokes = [{type: 'SOLID', color: ${colorToString(node.styles.borderColor)}}];\n`;
      code += `${ind}${varName}.strokeWeight = ${node.styles.borderWidth};\n`;
    }
    
    // 设置圆角
    if (node.styles.borderRadius > 0) {
      code += `${ind}${varName}.cornerRadius = ${node.styles.borderRadius};\n`;
    }
    
    // 生成子节点
    node.children.forEach((child, idx) => {
      const childVar = `${varName}_child${idx}`;
      code += '\n';
      code += generateNodeCode(child, childVar, indent);
      code += `${ind}${varName}.appendChild(${childVar});\n`;
    });
  }
  
  return code;
}

// 颜色对象转字符串
function colorToString(color) {
  if (!color) return 'null';
  return `{r:${color.r.toFixed(2)}, g:${color.g.toFixed(2)}, b:${color.b.toFixed(2)}}`;
}

// ========== 使用示例 ==========
// 在浏览器控制台执行：
// const layoutTree = analyzeDOMNode(document.querySelector('.your-container'));
// const figmaCode = generateFigmaPluginCode(layoutTree);
// console.log(figmaCode);
// 然后复制代码到Figma Plugin中运行

// 导出函数（如果在Node环境）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    analyzeDOMNode,
    generateFigmaPluginCode
  };
}
