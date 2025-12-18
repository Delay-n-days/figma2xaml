# Figma2XAML 生成器已发现的Bug列表

## 通过测试驱动发现的问题

### 🐛 Bug #1: HUG sizing被错误转换为*
**测试用例**: 06_button_group  
**症状**: 
```xaml
<!-- 错误: 第二个HUG按钮变成了* -->
<ColumnDefinition Width="Auto"/>
<ColumnDefinition Width="*"/>
```
**预期**:
```xaml
<ColumnDefinition Width="Auto"/>
<ColumnDefinition Width="Auto"/>
```
**原因分析**: 生成器可能在Grid列生成时,把最后一个Auto列错误地转换为*  
**影响范围**: 所有包含多个HUG子元素的水平Grid布局  
**优先级**: 🔴 HIGH - 影响布局尺寸计算

---

### 🐛 Bug #2: gridColumnGap间距错误平分
**测试用例**: 09_form_row  
**症状**:
```xaml
<!-- 错误: 11px间距被拆成5.5px + 5.5px -->
<TextBlock Margin="0,0,5.5,0"/>
<Border Margin="5.5,0,0,0"/>
```
**预期**:
```xaml
<TextBlock Margin="0,0,11,0"/>
<Border Margin="0"/>
```
**原因分析**: Gap处理逻辑错误地在两个元素之间平均分配  
**影响范围**: 所有使用gridColumnGap/gridRowGap的Grid布局  
**优先级**: 🟡 MEDIUM - 影响间距精度,但不影响功能

---

### 🐛 Bug #3: 单子元素被冗余包装在StackPanel中
**测试用例**: 06_button_group, 09_form_row  
**症状**:
```xaml
<!-- 冗余结构 -->
<Border>
    <StackPanel HorizontalAlignment="Center">
        <TextBlock Text="开始扫描"/>
    </StackPanel>
</Border>
```
**预期**:
```xaml
<Border>
    <TextBlock Text="开始扫描" HorizontalAlignment="Center" VerticalAlignment="Center"/>
</Border>
```
**原因分析**: 容器生成逻辑未检测子元素数量,总是包装StackPanel  
**影响范围**: 所有Border/Grid单元格只有一个Text子元素的情况  
**优先级**: 🟢 LOW - 不影响功能,但增加XAML冗余度

---

### 🐛 Bug #4: 有fills的Grid根容器被包装在Border中
**测试用例**: 11_complex_nested_grid  
**症状**:
```xaml
<!-- 根容器错误地变成Border包装Grid -->
<Border Background="#F9FAFB">
    <Grid>
        ...
    </Grid>
</Border>
```
**预期**:
```xaml
<!-- 根Grid应该直接设置Background -->
<Grid Background="#F9FAFB">
    ...
</Grid>
```
**原因分析**: 容器选择规则优先级问题,fills属性触发Border包装  
**影响范围**: layoutMode=GRID但有背景色的根Frame  
**优先级**: 🟡 MEDIUM - 影响XAML结构层次

---

### 🐛 Bug #5: 缺少VerticalAlignment属性
**测试用例**: 09_form_row  
**症状**:
```xaml
<!-- Label缺少垂直居中 -->
<TextBlock Text="工程名称:" Grid.Column="0"/>
```
**预期**:
```xaml
<TextBlock Text="工程名称:" Grid.Column="0" VerticalAlignment="Center"/>
```
**原因分析**: gridChildVerticalAlign: CENTER未被转换  
**影响范围**: Grid子元素的垂直对齐  
**优先级**: 🟡 MEDIUM - 影响视觉对齐

---

## 测试覆盖不足的场景

### ❌ 未测试: Grid.RowSpan / Grid.ColumnSpan
- Figma的gridRowSpan, gridColumnSpan  
- 跨行/跨列单元格

### ❌ 未测试: 复杂strokeWeight处理
- strokeTopWeight, strokeRightWeight, strokeBottomWeight, strokeLeftWeight不同值  
- 应转换为BorderThickness="left,top,right,bottom"

### ❌ 未测试: FontWeight映射
- Figma fontWeight: 400, 600, 700  
- WPF: Normal, SemiBold, Bold

### ❌ 未测试: 深度嵌套(4层以上)
- Grid → Grid → Grid → Grid  
- 测试AST递归深度

### ❌ 未测试: SPACE_BETWEEN in VERTICAL
- 垂直布局的两端对齐  
- 应生成3行Grid (Auto-*-Auto)

---

## 建议的修复优先级

1. **立即修复** (影响核心功能):
   - Bug #1: HUG sizing转换错误
   
2. **短期修复** (影响质量):
   - Bug #2: Gap间距计算
   - Bug #4: Grid根容器包装
   - Bug #5: VerticalAlignment缺失
   
3. **长期优化** (代码质量):
   - Bug #3: 冗余StackPanel包装
   
4. **增强测试覆盖**:
   - 添加RowSpan/ColumnSpan测试
   - 添加复杂strokeWeight测试
   - 添加垂直SPACE_BETWEEN测试
