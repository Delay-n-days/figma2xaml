# 测试用例说明

## 📁 目录结构

```
test_cases/
├── inputs/              # 测试输入 (Figma JSON)
├── expected/            # 预期输出 (XAML)
└── outputs/             # 实际输出 (自动生成)
```

## 🧪 测试用例列表

### 1. `01_horizontal_stack` - 水平 StackPanel
- **布局**: HORIZONTAL
- **对齐**: MIN, CENTER
- **间距**: 16px
- **预期**: `<StackPanel Orientation="Horizontal">`

### 2. `02_vertical_stack` - 垂直 StackPanel
- **布局**: VERTICAL
- **对齐**: MIN, MIN
- **间距**: 8px
- **预期**: `<StackPanel Orientation="Vertical">`

### 3. `03_space_between` - 两端对齐 (Grid)
- **布局**: HORIZONTAL + SPACE_BETWEEN
- **预期**: `<Grid>` with Auto-*-Auto 列定义
- **重要**: 测试两端对齐的核心场景

### 4. `04_grid_layout` - Grid 布局
- **布局**: GRID (2x3)
- **间距**: 行间距 10px, 列间距 10px
- **预期**: `<Grid>` with RowDefinitions & ColumnDefinitions

### 5. `05_horizontal_fill` - 水平布局 + FILL 元素
- **布局**: HORIZONTAL with FILL child
- **预期**: `<Grid>` with Auto-* 列定义
- **重要**: 测试 FILL 模式的转换

## 🚀 运行测试

### 运行所有测试
```powershell
python run_tests.py
```

### 运行单个测试
```powershell
python run_tests.py 01_horizontal_stack
```

### 运行多个测试
```powershell
python run_tests.py 01_horizontal_stack 03_space_between
```

## ✅ 测试通过标准

1. ✅ **元素类型正确**: StackPanel, Grid, TextBlock, Rectangle 等
2. ✅ **布局属性正确**: Orientation, RowDefinitions, ColumnDefinitions
3. ✅ **对齐方式正确**: HorizontalAlignment, VerticalAlignment
4. ✅ **间距正确**: Margin, Padding
5. ✅ **颜色正确**: Foreground, Background, Fill
6. ✅ **文本正确**: Text, FontSize, FontWeight

## 📝 添加新测试用例

### 步骤:

1. **创建输入 JSON** (在 `inputs/` 目录)
   ```json
   {
     "compressed_data": [
       {
         "id": "test:XX",
         "type": "FRAME",
         "layoutMode": "HORIZONTAL",
         ...
       }
     ]
   }
   ```

2. **创建预期 XAML** (在 `expected/` 目录)
   ```xml
   <StackPanel Orientation="Horizontal">
     ...
   </StackPanel>
   ```

3. **运行测试**
   ```powershell
   python run_tests.py XX_test_name
   ```

4. **对比结果**
   - 查看 `outputs/` 目录下的实际输出
   - 对比差异,调整转换脚本

## 🔄 迭代优化流程

```
1. 编写测试用例 (inputs/ + expected/)
   ↓
2. 运行测试 (python run_tests.py)
   ↓
3. 查看失败原因
   ↓
4. 修改 figma_to_xaml_v2.py
   ↓
5. 重新运行测试
   ↓
6. 循环直到全部通过 ✅
```

## 💡 测试技巧

### 调试单个用例
```powershell
# 查看详细差异
python run_tests.py 03_space_between
```

### 对比输出
```powershell
# 手动对比预期和实际输出
code test_cases/expected/03_space_between.xaml
code test_cases/outputs/03_space_between.xaml
```

### 更新预期结果
如果生成的结果是正确的,可以更新预期:
```powershell
cp test_cases/outputs/03_space_between.xaml test_cases/expected/
```

## 📊 测试覆盖率目标

- [x] 基础 StackPanel (水平/垂直)
- [x] 两端对齐 (SPACE_BETWEEN)
- [x] Grid 布局
- [x] FILL 模式
- [ ] WrapPanel (待添加)
- [ ] 嵌套布局 (待添加)
- [ ] 复杂样式 (待添加)
- [ ] 边框和圆角 (待添加)

## 🎯 下一步

1. 运行现有测试,看通过率
2. 根据失败用例,修复转换脚本
3. 添加更多边缘场景测试
4. 达到 100% 通过率! 🎉
