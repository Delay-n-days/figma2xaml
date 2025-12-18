"""
Figma 到 WPF AST 构建器
作用: 将 Figma JSON 转换为 WPF AST 对象树
"""
from typing import Dict, List, Any, Optional
from src.wpf_ast import WpfNode, create_border, create_stackpanel, create_grid, create_wrappanel, create_textblock
from src.rule_engine import RuleEngine


class FigmaToWpfBuilder:
    """Figma 到 WPF AST 构建器
    
    负责将 Figma JSON 节点转换为 WPF AST 节点
    """
    
    def __init__(self, config_dir: str = 'config'):
        """初始化构建器
        
        Args:
            config_dir: 配置文件目录
        """
        self.rule_engine = RuleEngine(config_dir)
        self.indent_str = "    "  # 4空格缩进
    
    def build(self, figma_node: Dict[str, Any], is_root: bool = False) -> WpfNode:
        """构建 WPF AST
        
        Args:
            figma_node: Figma JSON 节点
            is_root: 是否是根节点
        
        Returns:
            WPF AST 节点
        """
        node_type = figma_node.get('type')
        
        if node_type == 'FRAME':
            return self._build_frame(figma_node, is_root)
        elif node_type == 'RECTANGLE':
            return self._build_rectangle(figma_node)
        elif node_type == 'TEXT':
            return self._build_text(figma_node)
        else:
            # 未知类型,返回空节点
            return WpfNode(type='Unknown', comment=f"未知类型: {node_type}")
    
    def _build_frame(self, node: Dict[str, Any], is_root: bool = False) -> WpfNode:
        """构建 Frame 节点 → Border + 容器"""
        name = node.get('name', 'Frame')
        
        # 获取布局属性
        layout_mode = node.get('layoutMode', 'NONE')
        layout_wrap = node.get('layoutWrap', 'NO_WRAP')
        layout_sizing_horizontal = node.get('layoutSizingHorizontal', 'FIXED')
        layout_sizing_vertical = node.get('layoutSizingVertical', 'FIXED')
        layout_align = node.get('layoutAlign', 'INHERIT')
        item_spacing = node.get('itemSpacing', 0)
        
        # 获取对齐属性
        counter_axis_align = node.get('counterAxisAlignItems', 'MIN')
        primary_axis_align = node.get('primaryAxisAlignItems', 'MIN')
        
        # 获取子元素
        children = node.get('children', [])
        visible_children = [c for c in children if c.get('visible', True)]
        
        # 检查是否有填充子元素
        has_fill_child = any(
            child.get('layoutSizingHorizontal') == 'FILL'
            for child in visible_children
        )
        
        # 根容器特殊处理
        if is_root and layout_mode == 'HORIZONTAL' and len(visible_children) > 1:
            has_fill_child = True
        
        # 创建 Border 节点
        border = self._create_border_for_frame(node, is_root, layout_sizing_horizontal, layout_sizing_vertical, layout_align)
        
        # 选择容器类型
        container_context = {
            'layout_mode': layout_mode,
            'layout_wrap': layout_wrap,
            'has_fill_child': has_fill_child,
            'visible_children_count': len(visible_children),
            'primary_axis_align': primary_axis_align  # 添加主轴对齐
        }
        container_config = self.rule_engine.select_container(container_context)
        
        # 创建容器节点
        container = self._create_container(
            container_config,
            node,
            layout_sizing_horizontal,
            layout_sizing_vertical,
            layout_align,
            counter_axis_align,
            primary_axis_align
        )
        
        # 处理子元素
        use_grid = container_config.get('use_grid', False)
        use_grid_layout = container_config.get('use_grid_layout', False)
        
        if use_grid_layout:
            # Figma Grid 布局: 处理行列定义
            grid_row_sizes = node.get('gridRowSizes', [])
            grid_column_sizes = node.get('gridColumnSizes', [])
            
            # 转换行定义
            row_definitions = []
            for row_size in grid_row_sizes:
                if row_size.get('type') == 'FLEX':
                    value = row_size.get('value', 1)
                    # 如果是1,简化为 "*"
                    row_definitions.append('*' if value == 1 else f"{value}*")
                elif row_size.get('type') == 'FIXED':
                    row_definitions.append(str(row_size.get('value', 'Auto')))
                else:
                    row_definitions.append('Auto')
            
            # 转换列定义
            column_definitions = []
            for col_size in grid_column_sizes:
                if col_size.get('type') == 'FLEX':
                    value = col_size.get('value', 1)
                    # 如果是1,简化为 "*"
                    column_definitions.append('*' if value == 1 else f"{value}*")
                elif col_size.get('type') == 'FIXED':
                    column_definitions.append(str(col_size.get('value', 'Auto')))
                else:
                    column_definitions.append('Auto')
            
            if row_definitions:
                container.set_attribute('_row_definitions', row_definitions)
            if column_definitions:
                container.set_attribute('_column_definitions', column_definitions)
        
        elif use_grid:
            # Grid: 需要设置列定义(如果还没有设置)
            if '_column_definitions' not in container.attributes:
                column_definitions = []
                for i, child in enumerate(visible_children):
                    is_last_in_root = (is_root and i == len(visible_children) - 1)
                    is_fill = (child.get('layoutSizingHorizontal') == 'FILL')
                    
                    if is_fill or is_last_in_root:
                        column_definitions.append('*')
                    else:
                        column_definitions.append('Auto')
                
                container.set_attribute('_column_definitions', column_definitions)
        
        # 转换子元素
        current_layout = self._get_current_layout(layout_mode, layout_wrap)
        visible_child_index = 0
        
        for child in children:
            if not child.get('visible', True):
                continue
            
            is_first = (visible_child_index == 0)
            is_in_fill_column = False
            
            if use_grid:
                is_last_in_root = (is_root and visible_child_index == len(visible_children) - 1)
                is_fill = (child.get('layoutSizingHorizontal') == 'FILL')
                is_in_fill_column = is_fill or is_last_in_root
            
            # 设置上下文信息
            child['_parent_spacing'] = item_spacing
            child['_parent_layout'] = current_layout
            child['_is_first_child'] = is_first
            child['_in_fill_column'] = is_in_fill_column
            
            # 构建子节点
            child_ast = self.build(child, is_root=False)
            
            # Figma Grid 布局: 设置 Grid.Row 和 Grid.Column
            if use_grid_layout:
                # 获取子元素在 Grid 中的位置
                grid_row = child.get('gridRowAnchorIndex', -1)
                grid_col = child.get('gridColumnAnchorIndex', -1)
                
                # 获取 Grid 的行列数
                grid_column_count = len(container.attributes.get('_column_definitions', []))
                grid_row_count = len(container.attributes.get('_row_definitions', []))
                
                # 如果没有明确指定位置,按顺序自动分配
                if grid_row == -1 or grid_col == -1:
                    if grid_column_count > 0:
                        grid_row = visible_child_index // grid_column_count
                        grid_col = visible_child_index % grid_column_count
                    else:
                        grid_row = 0
                        grid_col = visible_child_index
                
                child_ast.set_attribute('Grid.Row', str(grid_row))
                child_ast.set_attribute('Grid.Column', str(grid_col))
                
                # 设置行列跨度
                grid_row_span = child.get('gridRowSpan', 1)
                grid_col_span = child.get('gridColumnSpan', 1)
                if grid_row_span > 1:
                    child_ast.set_attribute('Grid.RowSpan', str(grid_row_span))
                if grid_col_span > 1:
                    child_ast.set_attribute('Grid.ColumnSpan', str(grid_col_span))
                
                # 设置 Grid 间距 (通过 Margin 实现)
                # gridRowGap: 行间距, gridColumnGap: 列间距
                row_spacing = node.get('gridRowGap', 0)  # 行间距
                col_spacing = node.get('gridColumnGap', 0)  # 列间距
                
                # 计算 Margin: 左,上,右,下
                margin_left = col_spacing / 2 if grid_col > 0 else 0
                margin_top = row_spacing / 2 if grid_row > 0 else 0
                margin_right = col_spacing / 2
                margin_bottom = row_spacing / 2
                
                # 为最后一列和最后一行移除右边和下边的间距
                if grid_col == grid_column_count - 1:
                    margin_right = 0
                if grid_row == grid_row_count - 1:
                    margin_bottom = 0
                
                if margin_left > 0 or margin_top > 0 or margin_right > 0 or margin_bottom > 0:
                    # 转换为整数（如果是整数值）
                    margin_left = int(margin_left) if margin_left == int(margin_left) else margin_left
                    margin_top = int(margin_top) if margin_top == int(margin_top) else margin_top
                    margin_right = int(margin_right) if margin_right == int(margin_right) else margin_right
                    margin_bottom = int(margin_bottom) if margin_bottom == int(margin_bottom) else margin_bottom
                    margin_str = f"{margin_left},{margin_top},{margin_right},{margin_bottom}"
                    child_ast.set_attribute('Margin', margin_str)
            
            # 水平布局 Grid: 设置 Grid.Column
            elif use_grid:
                # 检查是否是 SPACE_BETWEEN 布局
                if container_config.get('space_between'):
                    # 两端对齐: 第一个在列0,最后一个在列2,中间的在列1
                    if visible_child_index == 0:
                        col_index = 0  # 第一个元素
                    elif visible_child_index == len(visible_children) - 1:
                        col_index = 2  # 最后一个元素
                    else:
                        col_index = 1  # 中间元素
                    child_ast.set_attribute('Grid.Column', str(col_index))
                else:
                    # 普通 Grid: 按顺序排列
                    child_ast.set_attribute('Grid.Column', str(visible_child_index))
            
            container.add_child(child_ast)
            visible_child_index += 1
        
        # 检查是否需要 Border 包装
        # 如果没有边框、圆角、背景、Padding 等 Border 特有属性，直接返回容器
        corner_radius = node.get('cornerRadius', 0)
        border_brush = self._get_border_color(node)
        background = self._get_background_color(node)
        padding_str = self._get_padding_string(node)
        
        needs_border = (
            border_brush is not None or  # 有边框
            corner_radius > 0 or  # 有圆角
            background is not None or  # 有背景色
            padding_str  # 有 Padding
        )
        
        if not needs_border and is_root:
            # 根节点且不需要 Border，直接返回容器
            return container
        elif needs_border:
            # 需要 Border 包装
            border.add_child(container)
            return border
        else:
            # 非根节点也不需要 Border，直接返回容器
            # 但保留注释
            container.comment = f"{node.get('name', 'Frame')} 容器"
            return container
    
    def _create_border_for_frame(
        self,
        node: Dict[str, Any],
        is_root: bool,
        sizing_horizontal: str,
        sizing_vertical: str,
        layout_align: str
    ) -> WpfNode:
        """为 Frame 创建 Border 节点"""
        name = node.get('name', 'Frame')
        border = create_border(comment=f"{name} 容器")
        
        # 构建属性上下文
        width = node.get('width')
        height = node.get('height')
        background = self._get_background_color(node)
        corner_radius = node.get('cornerRadius', 0)
        border_brush = self._get_border_color(node)
        padding_str = self._get_padding_string(node)
        
        # 是否在填充列
        is_in_fill_column = node.get('_in_fill_column', False)
        
        # 判断是否设置宽高
        if is_root:
            should_set_width = False
            should_set_height = False
        elif sizing_horizontal == 'FILL' or layout_align == 'STRETCH' or is_in_fill_column:
            should_set_width = False
        else:
            should_set_width = self.rule_engine.should_set_dimension(sizing_horizontal)
        
        if is_root:
            should_set_height = False
        elif sizing_vertical == 'FILL':
            should_set_height = False
        else:
            should_set_height = self.rule_engine.should_set_dimension(sizing_vertical)
        
        # 设置属性
        border.set_attribute('CornerRadius', str(corner_radius))
        
        # 只在有边框时设置边框属性
        if border_brush:
            border.set_attribute('BorderBrush', border_brush)
            border.set_attribute('BorderThickness', '1')
        
        if should_set_width and width:
            border.set_attribute('Width', str(width))
        
        if should_set_height and height:
            border.set_attribute('Height', str(height))
        
        # HorizontalAlignment
        if sizing_horizontal == 'FILL' or layout_align == 'STRETCH':
            border.set_attribute('HorizontalAlignment', 'Stretch')
        
        # Background
        if background:
            border.set_attribute('Background', background)
        
        # Padding
        if padding_str:
            border.set_attribute('Padding', padding_str)
        else:
            border.set_attribute('Padding', '0')
        
        return border
    
    def _create_container(
        self,
        container_config: Dict[str, Any],
        node: Dict[str, Any],
        sizing_horizontal: str,
        sizing_vertical: str,
        layout_align: str,
        counter_axis_align: str,
        primary_axis_align: str
    ) -> WpfNode:
        """创建布局容器节点"""
        container_type = container_config['container_type']
        orientation = container_config.get('orientation', 'Vertical')
        
        if container_type == 'StackPanel':
            container = create_stackpanel(orientation=orientation)
            
            # 设置对齐
            is_container_fill_horizontal = (sizing_horizontal == 'FILL' or layout_align == 'STRETCH')
            is_container_fill_vertical = (sizing_vertical == 'FILL' or layout_align == 'STRETCH')
            
            if orientation == 'Vertical' and not is_container_fill_horizontal:
                # 垂直布局,设置水平对齐
                h_align = self.rule_engine.get_alignment('counter_axis', counter_axis_align, 'horizontal')
                container.set_attribute('HorizontalAlignment', h_align)
            
            if orientation == 'Horizontal' and not is_container_fill_vertical:
                # 水平布局,设置垂直对齐
                v_align = self.rule_engine.get_alignment('counter_axis', counter_axis_align, 'vertical')
                container.set_attribute('VerticalAlignment', v_align)
        
        elif container_type == 'WrapPanel':
            container = create_wrappanel(orientation=orientation)
            
            # 设置对齐
            h_align = self.rule_engine.get_alignment('primary_axis', primary_axis_align, 'horizontal')
            v_align = self.rule_engine.get_alignment('counter_axis', counter_axis_align, 'vertical')
            
            container.set_attribute('HorizontalAlignment', h_align)
            container.set_attribute('VerticalAlignment', v_align)
        
        elif container_type == 'Grid':
            container = create_grid()
            
            # 检查是否是 SPACE_BETWEEN 布局
            if container_config.get('space_between'):
                # 为两端对齐创建列定义: Auto - * - Auto
                orientation = container_config.get('orientation', 'Horizontal')
                if orientation == 'Horizontal':
                    # 水平两端对齐: Auto - * - Auto
                    container.attributes['_column_definitions'] = ['Auto', '*', 'Auto']
                else:
                    # 垂直两端对齐: Auto - * - Auto (行)
                    container.attributes['_row_definitions'] = ['Auto', '*', 'Auto']
        
        else:
            # 默认 StackPanel
            container = create_stackpanel()
        
        return container
    
    def _build_rectangle(self, node: Dict[str, Any]) -> WpfNode:
        """构建 Rectangle 节点 → Border"""
        name = node.get('name', 'Rectangle')
        width = node.get('width', 0)
        height = node.get('height', 0)
        
        # 获取布局信息
        sizing_horizontal = node.get('layoutSizingHorizontal', 'FIXED')
        sizing_vertical = node.get('layoutSizingVertical', 'FIXED')
        layout_align = node.get('layoutAlign', 'INHERIT')
        is_in_fill_column = node.get('_in_fill_column', False)
        
        # 判断是否设置宽高
        if sizing_horizontal == 'FILL' or layout_align == 'STRETCH' or is_in_fill_column:
            should_set_width = False
        else:
            should_set_width = self.rule_engine.should_set_dimension(sizing_horizontal)
        
        if sizing_vertical == 'FILL':
            should_set_height = False
        else:
            should_set_height = self.rule_engine.should_set_dimension(sizing_vertical)
        
        # 创建 Border
        border = create_border(comment=name)
        
        # 设置宽高
        if should_set_width and width:
            border.set_attribute('Width', str(width))
        if should_set_height and height:
            border.set_attribute('Height', str(height))
        
        # HorizontalAlignment
        if sizing_horizontal == 'FILL' or layout_align == 'STRETCH':
            border.set_attribute('HorizontalAlignment', 'Stretch')
        
        # VerticalAlignment  
        if sizing_vertical == 'FILL':
            border.set_attribute('VerticalAlignment', 'Stretch')
        
        # 背景色
        background = self._get_background_color(node)
        if background:
            border.set_attribute('Background', background)
        
        # 圆角
        corner_radius_str = self._get_corner_radius_string(node)
        if corner_radius_str:
            border.set_attribute('CornerRadius', corner_radius_str)
        
        # Margin
        margin = self._calculate_margin(node)
        if margin:
            border.set_attribute('Margin', margin)
        
        return border
    
    def _build_text(self, node: Dict[str, Any]) -> WpfNode:
        """构建 Text 节点 → TextBlock"""
        name = node.get('name', 'Text')
        text = node.get('characters', name)
        
        # 创建 TextBlock
        textblock = create_textblock(text=text, comment=name)
        
        # 字体属性
        font_name = node.get('fontName', {})
        font_family = font_name.get('family', 'Segoe UI')
        font_weight = node.get('fontWeight', 400)
        font_size = node.get('fontSize', 12)
        
        # 颜色
        foreground = self._get_text_color(node)
        
        # 尺寸
        sizing_horizontal = node.get('layoutSizingHorizontal', 'FIXED')
        sizing_vertical = node.get('layoutSizingVertical', 'FIXED')
        width = node.get('width')
        height = node.get('height')
        
        # 设置属性
        if font_family and font_family not in ['Segoe UI', 'Roboto']:
            textblock.set_attribute('FontFamily', font_family)
        
        if font_size and font_size != 12:
            textblock.set_attribute('FontSize', str(font_size))
        
        if font_weight and font_weight >= 700:
            textblock.set_attribute('FontWeight', 'Bold')
        
        if foreground:
            textblock.set_attribute('Foreground', foreground)
        
        if sizing_horizontal != 'HUG' and width:
            textblock.set_attribute('Width', str(width))
        
        if sizing_vertical != 'HUG' and height:
            textblock.set_attribute('Height', str(height))
        
        # Margin
        margin = self._calculate_margin(node)
        if margin:
            textblock.set_attribute('Margin', margin)
        
        return textblock
    
    # ========== 辅助方法 ==========
    
    def _get_current_layout(self, layout_mode: str, layout_wrap: str) -> str:
        """获取当前布局类型"""
        if layout_mode == 'HORIZONTAL' and layout_wrap == 'WRAP':
            return 'WRAP'
        elif layout_mode == 'VERTICAL':
            return 'VERTICAL'
        elif layout_mode == 'HORIZONTAL':
            return 'HORIZONTAL'
        else:
            return 'NONE'
    
    def _calculate_margin(self, node: Dict[str, Any]) -> Optional[str]:
        """计算 Margin"""
        parent_spacing = node.get('_parent_spacing', 0)
        parent_layout = node.get('_parent_layout', 'NONE')
        is_first_child = node.get('_is_first_child', False)
        
        if parent_spacing > 0 and not is_first_child:
            if parent_layout == 'WRAP':
                half_spacing = parent_spacing / 2
                if half_spacing == int(half_spacing):
                    return str(int(half_spacing))
                else:
                    return str(half_spacing)
            elif parent_layout == 'VERTICAL':
                return f"0,{int(parent_spacing)},0,0"
            elif parent_layout == 'HORIZONTAL':
                return f"{int(parent_spacing)},0,0,0"
        
        return None
    
    def _get_background_color(self, node: Dict[str, Any]) -> Optional[str]:
        """获取背景颜色"""
        opacity = node.get('opacity', 1.0)
        fills = node.get('fills', [])
        
        if fills and len(fills) > 0:
            fill = fills[0]
            color = fill.get('color', '#FFFFFF')
            fill_opacity = fill.get('opacity', 1.0)
            final_opacity = opacity * fill_opacity
            return self._hex_to_wpf_color(color, final_opacity)
        
        return None
    
    def _get_border_color(self, node: Dict[str, Any]) -> Optional[str]:
        """获取边框颜色"""
        opacity = node.get('opacity', 1.0)
        strokes = node.get('strokes', [])
        
        if strokes and len(strokes) > 0:
            stroke = strokes[0]
            color = stroke.get('color', '#000000')
            stroke_opacity = stroke.get('opacity', 1.0)
            final_opacity = opacity * stroke_opacity
            return self._hex_to_wpf_color(color, final_opacity)
        
        return None  # 没有边框时返回 None
    
    def _get_text_color(self, node: Dict[str, Any]) -> Optional[str]:
        """获取文本颜色"""
        opacity = node.get('opacity', 1.0)
        fills = node.get('fills', [])
        
        if fills and len(fills) > 0:
            fill = fills[0]
            color = fill.get('color', '#000000')
            fill_opacity = fill.get('opacity', 1.0)
            final_opacity = opacity * fill_opacity
            
            # 黑色且完全不透明是默认值
            if color.upper() != '#000000' or final_opacity < 1.0:
                return self._hex_to_wpf_color(color, final_opacity)
        
        return None
    
    def _get_padding_string(self, node: Dict[str, Any]) -> Optional[str]:
        """获取 Padding 字符串"""
        padding_left = node.get('paddingLeft', 0)
        padding_right = node.get('paddingRight', 0)
        padding_top = node.get('paddingTop', 0)
        padding_bottom = node.get('paddingBottom', 0)
        
        if padding_left or padding_right or padding_top or padding_bottom:
            if padding_left == padding_right == padding_top == padding_bottom:
                return str(int(padding_left))
            else:
                return f"{int(padding_left)},{int(padding_top)},{int(padding_right)},{int(padding_bottom)}"
        
        return None
    
    def _get_corner_radius_string(self, node: Dict[str, Any]) -> Optional[str]:
        """获取圆角字符串"""
        corner_radius = node.get('cornerRadius', 0)
        
        if corner_radius == 'Mixed':
            tl = node.get('topLeftRadius', 0)
            tr = node.get('topRightRadius', 0)
            br = node.get('bottomRightRadius', 0)
            bl = node.get('bottomLeftRadius', 0)
            
            if tl or tr or br or bl:
                return f"{int(tl)},{int(tr)},{int(br)},{int(bl)}"
        elif corner_radius and corner_radius != 0:
            return str(int(corner_radius))
        
        return None
    
    def _hex_to_wpf_color(self, hex_color: str, opacity: float = 1.0) -> str:
        """转换颜色格式"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        if opacity >= 1.0:
            return f"#{hex_color.upper()}"
        
        alpha = int(opacity * 255)
        alpha_hex = f"{alpha:02X}"
        
        return f"#{alpha_hex}{hex_color.upper()}"
