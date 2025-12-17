// 设备列表界面 - 表驱动版本 + 完美居中
async function generate() {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  
  // 颜色配置
  const C = {
    white: {r:1, g:1, b:1},
    gray: {r:0.8, g:0.8, b:0.8},
    dark: {r:0.1, g:0.1, b:0.1},
    grayText: {r:0.4, g:0.4, b:0.4},
    blue: {r:0.2, g:0.4, b:0.8}
  };
  
  // 创建按钮
  const btn = (text) => {
    const f = figma.createFrame();
    f.resize(80, 28);
    f.layoutMode = 'HORIZONTAL';
    f.fills = [{type: 'SOLID', color: C.white}];
    f.strokes = [{type: 'SOLID', color: C.gray}];
    f.strokeWeight = 1;
    f.strokeAlign = 'INSIDE';
    f.paddingLeft = 12;
    f.paddingRight = 12;
    f.primaryAxisAlignItems = 'CENTER';
    f.counterAxisAlignItems = 'CENTER';
    const t = figma.createText();
    t.characters = text;
    t.fontSize = 12;
    t.fills = [{type: 'SOLID', color: C.dark}];
    f.appendChild(t);
    return f;
  };
  
  // 创建输入框
  const input = (text) => {
    const f = figma.createFrame();
    f.resize(50, 24);
    f.layoutMode = 'HORIZONTAL';
    f.fills = [{type: 'SOLID', color: C.white}];
    f.strokes = [{type: 'SOLID', color: C.gray}];
    f.strokeWeight = 1;
    f.strokeAlign = 'INSIDE';
    f.paddingLeft = 8;
    f.paddingRight = 8;
    f.primaryAxisAlignItems = 'CENTER';
    f.counterAxisAlignItems = 'CENTER';
    const t = figma.createText();
    t.characters = text;
    t.fontSize = 11;
    t.fills = [{type: 'SOLID', color: C.grayText}];
    f.appendChild(t);
    return f;
  };
  
  // 创建文本
  const txt = (text, size = 12, color = C.dark) => {
    const t = figma.createText();
    t.characters = text;
    t.fontSize = size;
    t.fills = [{type: 'SOLID', color}];
    return t;
  };
  
  // 主容器
  const toolbar = figma.createFrame();
  toolbar.name = "工具栏";
  toolbar.layoutMode = 'VERTICAL';
  toolbar.primaryAxisSizingMode = 'AUTO';
  toolbar.counterAxisSizingMode = 'AUTO';
  toolbar.fills = [];
  toolbar.paddingLeft = 16;
  toolbar.paddingRight = 16;
  toolbar.paddingTop = 12;
  toolbar.paddingBottom = 12;
  toolbar.itemSpacing = 8;
  
  // 内容行
  const row = figma.createFrame();
  row.layoutMode = 'HORIZONTAL';
  row.primaryAxisSizingMode = 'AUTO';
  row.counterAxisSizingMode = 'AUTO';
  row.fills = [];
  row.itemSpacing = 12;
  row.primaryAxisAlignItems = 'CENTER'; // 关键：垂直居中
  
  // 表驱动：按钮
  ['开始扫描', '停止扫描'].forEach(text => row.appendChild(btn(text)));
  
  // 站号区域
  const station = figma.createFrame();
  station.layoutMode = 'HORIZONTAL';
  station.primaryAxisSizingMode = 'AUTO';
  station.counterAxisSizingMode = 'AUTO';
  station.fills = [];
  station.itemSpacing = 8;
  station.primaryAxisAlignItems = 'CENTER'; // 关键：垂直居中
  
  // 表驱动：站号区域元素
  [
    {type: 'text', text: '站号范围'},
    {type: 'input', text: '1'},
    {type: 'text', text: '-'},
    {type: 'input', text: '16'}
  ].forEach(item => {
    station.appendChild(item.type === 'input' ? input(item.text) : txt(item.text));
  });
  
  row.appendChild(station);
  
  // 右对齐占位
  const spacer = figma.createFrame();
  spacer.fills = [];
  spacer.layoutGrow = 1;
  row.appendChild(spacer);
  
  // 链接
  row.appendChild(txt('设备无法连接？', 12, C.blue));
  
  toolbar.appendChild(row);
  
  // 添加到画布
  figma.currentPage.appendChild(toolbar);
  figma.currentPage.selection = [toolbar];
  figma.viewport.scrollAndZoomIntoView([toolbar]);
}

generate();
