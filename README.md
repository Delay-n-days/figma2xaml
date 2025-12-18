# Figma to XAML Converter V2

## 📐 架构升级

**V2 架构**: AST + 规则引擎 + Jinja2 模板

### 🎯 核心优势

1. **分离关注点**: 逻辑(Python) + 配置(YAML) + 视图(Jinja2)
2. **高可维护性**: 修改规则只需编辑 YAML,无需改代码
3. **高可扩展性**: 新增控件只需添加模板
4. **高可测试性**: 每个模块可独立测试
5. **零优化**: 第一版与原脚本输出完全一致

---

## 📁 项目结构

```
figma2xaml/
├── config/                          # 配置文件 (YAML)
│   ├── figma_wpf_mapping.yaml      # Figma → WPF 属性映射
│   └── layout_rules.yaml            # 布局规则和容器选择规则
│
├── templates/                       # Jinja2 模板
│   ├── base.xaml.j2                # UserControl 基础模板
│   ├── macros/
│   │   └── helpers.j2               # 辅助宏
│   └── controls/
│       ├── Border.xaml.j2           # Border 控件模板
│       ├── StackPanel.xaml.j2       # StackPanel 控件模板
│       ├── Grid.xaml.j2             # Grid 控件模板
│       ├── WrapPanel.xaml.j2        # WrapPanel 控件模板
│       └── TextBlock.xaml.j2        # TextBlock 控件模板
│
├── src/                             # 源代码 (Python)
│   ├── rule_engine.py               # 规则引擎 (条件求值)
│   ├── wpf_ast.py                   # WPF AST 模型
│   ├── ast_builder.py               # Figma → WPF AST 构建器
│   └── xaml_renderer.py             # XAML 渲染器 (Jinja2)
│
├── figma_to_xaml_v2.py              # 主入口 (V2)
├── figma_to_xaml.py                 # 原脚本 (V1,保留)
├── requirements.txt                 # Python 依赖
└── README_V2.md                     # 本文档
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行转换

```bash
# 方式 1: 使用默认输入文件 (injson_compressed.json)
python figma_to_xaml_v2.py

# 方式 2: 指定输入文件
python figma_to_xaml_v2.py your_file.json

# 方式 3: 指定输入和输出文件
python figma_to_xaml_v2.py input.json output.xaml
```

---

## 🔧 工作流程

```
┌──────────────────┐
│ Figma JSON       │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────┐
│ AST Builder                 │  ← 读取 YAML 规则
│  - 读取 Figma JSON          │
│  - 规则引擎匹配             │
│  - 构建 WPF AST             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ AST Optimizer               │
│  - Level 0: 不优化 (V1)     │
│  - Level 1: 基础优化 (未来) │
│  - Level 2: 激进优化 (未来) │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ XAML Renderer               │  ← 使用 Jinja2 模板
│  - 加载模板                 │
│  - 渲染 XAML                │
└────────┬────────────────────┘
         │
         ▼
┌──────────────────┐
│ XAML 输出        │
└──────────────────┘
```

---

## 📝 配置文件说明

### 1. `figma_wpf_mapping.yaml`

定义 Figma 属性到 WPF 属性的映射:

- **对齐方式**: MIN → Left/Top, CENTER → Center, MAX → Right/Bottom
- **尺寸模式**: FIXED/HUG/FILL → 是否设置宽高
- **字体粗细**: fontWeight ≥ 700 → Bold

### 2. `layout_rules.yaml`

定义布局容器选择规则和属性生成规则:

- **容器选择**: 根据 layoutMode, layoutWrap, has_fill_child 选择容器类型
- **属性规则**: 根据条件生成 Width, Height, HorizontalAlignment 等属性

---

## 🧪 测试对比

```bash
# 运行原脚本
python figma_to_xaml.py injson_compressed.json out_v1.xaml

# 运行新脚本
python figma_to_xaml_v2.py injson_compressed.json out_v2.xaml

# 对比输出
# 期望: 完全一致 (或只有空格/注释的微小差异)
```

---

## 🔍 调试技巧

### 1. 查看 AST 结构

```python
from src.ast_builder import FigmaToWpfBuilder
import json

builder = FigmaToWpfBuilder()
ast = builder.build(figma_node, is_root=True)

# 输出 AST 为 JSON
print(json.dumps(ast.to_dict(), indent=2, ensure_ascii=False))
```

### 2. 测试规则引擎

```python
from src.rule_engine import RuleEngine

engine = RuleEngine('config')

# 测试容器选择
context = {
    'layout_mode': 'HORIZONTAL',
    'layout_wrap': 'WRAP',
    'has_fill_child': False,
    'visible_children_count': 3
}
result = engine.select_container(context)
print("容器选择结果:", result)
```

### 3. 单独渲染节点

```python
from src.xaml_renderer import XamlRenderer
from src.wpf_ast import create_border, create_textblock

renderer = XamlRenderer('templates')

border = create_border(Width='100', Height='50')
text = create_textblock(text='Hello', FontSize='16')
border.add_child(text)

xaml = renderer.render_node(border, indent_level=0)
print(xaml)
```

---

## 📈 未来扩展

### Phase 1: 基础功能 (已完成 ✅)
- [x] AST 模型
- [x] 规则引擎
- [x] Jinja2 模板
- [x] 与 V1 输出一致

### Phase 2: 优化增强 (可选)
- [ ] AST 优化器 Level 1 (去除默认值)
- [ ] AST 优化器 Level 2 (合并容器)
- [ ] 性能优化 (并行构建)

### Phase 3: 功能扩展 (可选)
- [ ] 支持更多 WPF 控件
- [ ] 支持样式和资源
- [ ] 支持数据绑定

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

---

## 📄 许可证

MIT License
