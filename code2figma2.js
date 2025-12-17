// 工程向导界面生成器 - Auto Layout 版本
async function loadFont() {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
}

function rect(w, h, c, r = 0) {
  const el = figma.createRectangle();
  el.resize(w, h);
  el.fills = [{type: 'SOLID', color: c}];
  if (r) el.cornerRadius = r;
  return el;
}

function txt(s, sz, c) {
  const t = figma.createText();
  t.characters = s;
  t.fontSize = sz;
  t.fontName = {family: "Inter", style: "Regular"};
  t.fills = [{type: 'SOLID', color: c}];
  return t;
}

function hStack(spacing = 0, padding = 0) {
  const f = figma.createFrame();
  f.layoutMode = 'HORIZONTAL';
  f.itemSpacing = spacing;
  f.paddingLeft = f.paddingRight = f.paddingTop = f.paddingBottom = padding;
  f.primaryAxisSizingMode = 'AUTO';
  f.counterAxisSizingMode = 'AUTO';
  return f;
}

function vStack(spacing = 0, padding = 0) {
  const f = figma.createFrame();
  f.layoutMode = 'VERTICAL';
  f.itemSpacing = spacing;
  f.paddingLeft = f.paddingRight = f.paddingTop = f.paddingBottom = padding;
  f.primaryAxisSizingMode = 'AUTO';
  f.counterAxisSizingMode = 'AUTO';
  return f;
}

function fill(node) {
  node.layoutGrow = 1;
  return node;
}

async function generate() {
  await loadFont();
  
  const white = {r:1, g:1, b:1}, gray = {r:.95, g:.95, b:.95};
  const blue = {r:0, g:.4, b:1}, dark = {r:.2, g:.2, b:.2};
  const border_c = {r:.88, g:.88, b:.88}, gray2 = {r:.8, g:.8, b:.8};
  const textGray = {r:.4, g:.4, b:.4};
  
  // 主容器
  const main = figma.createFrame();
  main.name = "工程向导";
  main.resize(1024, 680);
  main.fills = [{type: 'SOLID', color: gray}];
  main.layoutMode = 'VERTICAL';
  main.itemSpacing = 0;
  
  // 标题栏
  const titleBar = hStack(0, 0);
  titleBar.resize(1024, 45);
  titleBar.fills = [{type: 'SOLID', color: white}];
  titleBar.primaryAxisSizingMode = 'FIXED';
  titleBar.counterAxisSizingMode = 'FIXED';
  titleBar.paddingLeft = 15;
  titleBar.paddingTop = 12;
  titleBar.paddingRight = 15;
  titleBar.primaryAxisAlignItems = 'SPACE_BETWEEN';
  titleBar.counterAxisAlignItems = 'CENTER';
  
  titleBar.appendChild(txt("工程向导", 16, dark));
  titleBar.appendChild(rect(20, 20, gray2)); // 关闭按钮
  main.appendChild(titleBar);
  
  // 内容区域 (左侧菜单 + 右侧内容)
  const content = hStack(0, 0);
  fill(content);
  
  // 左侧菜单
  const leftMenu = vStack(0, 0);
  leftMenu.resize(140, 635);
  leftMenu.fills = [{type: 'SOLID', color: white}];
  leftMenu.primaryAxisSizingMode = 'FIXED';
  leftMenu.counterAxisSizingMode = 'FIXED';
  
  // 在线按钮
  const onlineBtn = hStack(0, 0);
  onlineBtn.resize(140, 40);
  onlineBtn.fills = [{type: 'SOLID', color: blue}];
  onlineBtn.primaryAxisSizingMode = 'FIXED';
  onlineBtn.counterAxisSizingMode = 'FIXED';
  onlineBtn.paddingLeft = 15;
  onlineBtn.paddingTop = 10;
  onlineBtn.counterAxisAlignItems = 'CENTER';
  onlineBtn.appendChild(txt("在线", 14, white));
  leftMenu.appendChild(onlineBtn);
  
  // 离线按钮
  const offlineBtn = hStack(10, 0);
  offlineBtn.resize(140, 40);
  offlineBtn.fills = [{type: 'SOLID', color: white}];
  offlineBtn.strokes = [{type: 'SOLID', color: border_c}];
  offlineBtn.strokeWeight = 1;
  offlineBtn.primaryAxisSizingMode = 'FIXED';
  offlineBtn.counterAxisSizingMode = 'FIXED';
  offlineBtn.paddingLeft = 15;
  offlineBtn.paddingTop = 10;
  offlineBtn.counterAxisAlignItems = 'CENTER';
  offlineBtn.appendChild(rect(20, 20, gray2));
  offlineBtn.appendChild(txt("离线", 14, dark));
  leftMenu.appendChild(offlineBtn);
  
  content.appendChild(leftMenu);
  
  // 右侧内容区
  const rightContent = vStack(20, 20);
  fill(rightContent);
  
  // 产品网格容器
  const productArea = vStack(20, 0);
  
  const products = ["IS580", "IS580-1M", "ES100", "ES100-MVSY2", "ES510", "ES510-1M", "ES590", "ES590H"];
  
  // 第一行产品
  const row1 = hStack(20, 0);
  for (let i = 0; i < 4; i++) {
    const card = vStack(10, 10);
    card.resize(140, 180);
    card.fills = [{type: 'SOLID', color: white}];
    card.strokes = [{type: 'SOLID', color: border_c}];
    card.strokeWeight = 1;
    card.cornerRadius = 4;
    card.primaryAxisSizingMode = 'FIXED';
    card.counterAxisSizingMode = 'FIXED';
    card.effects = [{type: 'DROP_SHADOW', color: {r:0, g:0, b:0, a:.08}, offset: {x:0, y:2}, radius: 6, visible: true, blendMode: 'NORMAL'}];
    
    card.appendChild(rect(120, 130, gray2));
    card.appendChild(txt(products[i], 12, dark));
    row1.appendChild(card);
  }
  productArea.appendChild(row1);
  
  // 第二行产品
  const row2 = hStack(20, 0);
  for (let i = 4; i < 8; i++) {
    const card = vStack(10, 10);
    card.resize(140, 180);
    card.fills = [{type: 'SOLID', color: white}];
    card.strokes = [{type: 'SOLID', color: border_c}];
    card.strokeWeight = 1;
    card.cornerRadius = 4;
    card.primaryAxisSizingMode = 'FIXED';
    card.counterAxisSizingMode = 'FIXED';
    card.effects = [{type: 'DROP_SHADOW', color: {r:0, g:0, b:0, a:.08}, offset: {x:0, y:2}, radius: 6, visible: true, blendMode: 'NORMAL'}];
    
    card.appendChild(rect(120, 130, gray2));
    card.appendChild(txt(products[i], 12, dark));
    row2.appendChild(card);
  }
  productArea.appendChild(row2);
  
  // 将产品区和配置面板横向排列
  const mainArea = hStack(30, 0);
  mainArea.appendChild(productArea);
  
  // 配置面板
  const configPanel = vStack(15, 0);
  
  const configs = [
    ["通讯类型:", "串口"],
    ["串口号:", "COM3"],
    ["波特率:", "115200"],
    ["数据位:", "8"],
    ["校验位:", "None"],
    ["停止位:", "1"]
  ];
  
  configs.forEach(cfg => {
    const row = hStack(10, 0);
    row.counterAxisAlignItems = 'CENTER';
    
    const label = txt(cfg[0], 13, textGray);
    label.resize(80, 20);
    label.textAlignHorizontal = 'RIGHT';
    row.appendChild(label);
    
    const combo = hStack(10, 0);
    combo.resize(150, 32);
    combo.fills = [{type: 'SOLID', color: white}];
    combo.strokes = [{type: 'SOLID', color: border_c}];
    combo.strokeWeight = 1;
    combo.cornerRadius = 4;
    combo.primaryAxisSizingMode = 'FIXED';
    combo.counterAxisSizingMode = 'FIXED';
    combo.paddingLeft = 10;
    combo.paddingRight = 10;
    combo.primaryAxisAlignItems = 'SPACE_BETWEEN';
    combo.counterAxisAlignItems = 'CENTER';
    
    combo.appendChild(txt(cfg[1], 13, dark));
    combo.appendChild(rect(8, 8, gray2));
    row.appendChild(combo);
    
    configPanel.appendChild(row);
  });
  
  // 复选框
  const checkbox = hStack(8, 0);
  checkbox.counterAxisAlignItems = 'CENTER';
  checkbox.paddingLeft = 80;
  
  const chk = figma.createFrame();
  chk.resize(16, 16);
  chk.fills = [{type: 'SOLID', color: white}];
  chk.strokes = [{type: 'SOLID', color: border_c}];
  chk.strokeWeight = 1;
  
  checkbox.appendChild(chk);
  checkbox.appendChild(txt("自速应漏特率", 12, dark));
  configPanel.appendChild(checkbox);
  
  mainArea.appendChild(configPanel);
  rightContent.appendChild(mainArea);
  
  // 下一页按钮
  const btnArea = hStack(0, 0);
  btnArea.primaryAxisAlignItems = 'CENTER';
  btnArea.paddingTop = 20;
  
  const btn = hStack(0, 0);
  btn.resize(100, 36);
  btn.fills = [{type: 'SOLID', color: white}];
  btn.strokes = [{type: 'SOLID', color: border_c}];
  btn.strokeWeight = 1;
  btn.cornerRadius = 4;
  btn.primaryAxisSizingMode = 'FIXED';
  btn.counterAxisSizingMode = 'FIXED';
  btn.primaryAxisAlignItems = 'CENTER';
  btn.counterAxisAlignItems = 'CENTER';
  btn.appendChild(txt("下一页", 14, dark));
  
  btnArea.appendChild(btn);
  rightContent.appendChild(btnArea);
  
  content.appendChild(rightContent);
  main.appendChild(content);
  
  figma.currentPage.appendChild(main);
  figma.viewport.scrollAndZoomIntoView([main]);
  figma.notify("✅ 界面生成完成!");
  figma.closePlugin();
}

generate();