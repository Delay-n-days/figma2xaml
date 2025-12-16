"""
Figma JSON 到 WPF XAML 转换器
简单、清晰、易于扩展
"""
import json
from pathlib import Path


class FigmaToXamlConverter:
    """Figma 到 XAML 转换器"""
    
    def __init__(self):
        self.indent = "    "  # 4空格缩进
        
    def hex_to_wpf_color(self, hex_color, opacity=1.0):
        """转换颜色格式 #RRGGBB -> #AARRGGBB（包含透明度）
        
        Args:
            hex_color: 十六进制颜色，如 "#D9D9D9"
            opacity: 透明度 0.0-1.0，默认 1.0（完全不透明）
        
        Returns:
            WPF 颜色格式
            - 完全不透明 (opacity=1.0): "#D9D9D9"
            - 半透明 (opacity<1.0): "#80D9D9D9"
        """
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        # 如果完全不透明，省略 Alpha 通道
        if opacity >= 1.0:
            return f"#{hex_color.upper()}"
        
        # 将 opacity (0.0-1.0) 转换为十六进制 (00-FF)
        alpha = int(opacity * 255)
        alpha_hex = f"{alpha:02X}"
        
        return f"#{alpha_hex}{hex_color.upper()}"
    
    def convert_rectangle(self, node, indent_level=0, parent_spacing=0, parent_layout='NONE', is_first_child=False):
        """转换矩形节点 - 使用 Border
        
        Args:
            parent_spacing: 父容器的 itemSpacing
            parent_layout: 父容器的布局模式 (HORIZONTAL/VERTICAL/WRAP)
            is_first_child: 是否是第一个子元素
        """
        indent = self.indent * indent_level
        
        # 基本属性
        width = node.get('width', 0)
        height = node.get('height', 0)
        name = node.get('name', 'Rectangle')
        
        # 整体透明度
        opacity = node.get('opacity', 1.0)
        
        # 填充颜色
        fill_color = None
        fills = node.get('fills', [])
        if fills and len(fills) > 0:
            fill = fills[0]
            color = fill.get('color', '#D9D9D9')
            # 填充的透明度(如果有)
            fill_opacity = fill.get('opacity', 1.0)
            # 合并整体透明度和填充透明度
            final_opacity = opacity * fill_opacity
            fill_color = self.hex_to_wpf_color(color, final_opacity)
        
        # 是否可见
        visible = node.get('visible', True)
        
        # 圆角
        corner_radius = node.get('cornerRadius', 0)
        corner_radius_str = None
        if corner_radius == 'Mixed':
            # 独立圆角
            tl = node.get('topLeftRadius', 0)
            tr = node.get('topRightRadius', 0)
            br = node.get('bottomRightRadius', 0)
            bl = node.get('bottomLeftRadius', 0)
            # 只有不全为0时才设置
            if tl or tr or br or bl:
                corner_radius_str = f"{tl},{tr},{br},{bl}"
        elif corner_radius and corner_radius != 0:
            # 统一圆角,非0才设置
            corner_radius_str = str(corner_radius)
        
        # 构建 XAML
        xaml = f'{indent}<!-- {name} -->\n'
        xaml += f'{indent}<Border'
        
        # 必需属性
        if width:
            xaml += f' Width="{width}"'
        if height:
            xaml += f' Height="{height}"'
        
        # 可选属性(非默认值才添加)
        if fill_color:
            xaml += f' Background="{fill_color}"'
        if corner_radius_str:
            xaml += f' CornerRadius="{corner_radius_str}"'
        if not visible:
            xaml += ' Visibility="Collapsed"'
        
        # 根据父容器布局模式和间距添加 Margin
        if parent_spacing > 0 and not is_first_child:
            if parent_layout == 'WRAP':
                # WrapPanel: 四边都加间距
                half_spacing = parent_spacing / 2
                xaml += f' Margin="{half_spacing}"'
            elif parent_layout == 'VERTICAL':
                # 垂直布局: 只在上方加间距 (Left,Top,Right,Bottom)
                xaml += f' Margin="0,{parent_spacing},0,0"'
            elif parent_layout == 'HORIZONTAL':
                # 水平布局: 只在左边加间距 (Left,Top,Right,Bottom)
                xaml += f' Margin="{parent_spacing},0,0,0"'
        
        xaml += '/>\n'
        
        return xaml
    
    def convert_frame(self, node, indent_level=0, is_root=False):
        """转换 Frame 节点
        
        Args:
            is_root: 是否是根节点(UserControl 的直接子节点)
        """
        indent = self.indent * indent_level
        
        name = node.get('name', 'Frame')
        
        # 检查布局尺寸模式
        layout_sizing_horizontal = node.get('layoutSizingHorizontal', 'FIXED')
        layout_sizing_vertical = node.get('layoutSizingVertical', 'FIXED')
        layout_align = node.get('layoutAlign', 'INHERIT')
        
        # 判断是否在父容器的填充列中
        is_in_fill_column = node.get('_in_fill_column', False)
        
        # 根据 layoutSizing 决定宽高
        # 根节点特殊处理: 不设置固定宽度,让它自适应
        if is_root or layout_sizing_horizontal == 'FILL' or layout_align == 'STRETCH' or is_in_fill_column:
            # 填充父容器宽度
            width = None  # 不设置固定宽度
        else:
            width = node.get('width', 'Auto')
        
        if is_root or layout_sizing_vertical == 'FILL':
            # 填充父容器高度
            height = None  # 不设置固定高度
        elif layout_sizing_vertical == 'HUG':
            # 根据内容自动调整高度
            height = None
        else:
            height = node.get('height', 'Auto')
        
        # 整体透明度
        opacity = node.get('opacity', 1.0)
        
        # 背景颜色
        background = None
        fills = node.get('fills', [])
        if fills and len(fills) > 0:
            fill = fills[0]
            color = fill.get('color', '#FFFFFF')
            fill_opacity = fill.get('opacity', 1.0)
            final_opacity = opacity * fill_opacity
            background = self.hex_to_wpf_color(color, final_opacity)
        
        # 边框
        strokes = node.get('strokes', [])
        border_brush = "#FF000000"
        if strokes and len(strokes) > 0:
            stroke = strokes[0]
            color = stroke.get('color', '#000000')
            stroke_opacity = stroke.get('opacity', 1.0)
            final_opacity = opacity * stroke_opacity
            border_brush = self.hex_to_wpf_color(color, final_opacity)
        
        # 圆角
        corner_radius = node.get('cornerRadius', 0)
        
        # 内边距 - 获取四个方向的 padding
        padding_left = node.get('paddingLeft', 0)
        padding_right = node.get('paddingRight', 0)
        padding_top = node.get('paddingTop', 0)
        padding_bottom = node.get('paddingBottom', 0)
        
        # 构建 Padding 字符串
        padding_str = None
        if padding_left or padding_right or padding_top or padding_bottom:
            if padding_left == padding_right == padding_top == padding_bottom:
                # 四个方向相同
                padding_str = str(padding_left)
            else:
                # 四个方向不同: Left,Top,Right,Bottom
                padding_str = f"{padding_left},{padding_top},{padding_right},{padding_bottom}"
        
        # 布局模式
        layout_mode = node.get('layoutMode', 'NONE')
        layout_wrap = node.get('layoutWrap', 'NO_WRAP')
        item_spacing = node.get('itemSpacing', 0)
        
        xaml = f'{indent}<!-- {name} 容器 -->\n'
        xaml += f'{indent}<Border CornerRadius="{corner_radius}"\n'
        xaml += f'{indent}        BorderBrush="{border_brush}"\n'
        xaml += f'{indent}        BorderThickness="1"'
        
        # 添加宽度和高度(如果有固定值)
        if width:
            xaml += f'\n{indent}        Width="{width}"'
        if height:
            xaml += f'\n{indent}        Height="{height}"'
        
        # 如果需要水平拉伸,设置 HorizontalAlignment
        if layout_sizing_horizontal == 'FILL' or layout_align == 'STRETCH':
            xaml += f'\n{indent}        HorizontalAlignment="Stretch"'
        
        # 添加背景色
        if background:
            xaml += f'\n{indent}        Background="{background}"'
        
        # 添加 Padding
        if padding_str:
            xaml += f'\n{indent}        Padding="{padding_str}"'
        else:
            xaml += f'\n{indent}        Padding="0"'
        
        xaml += '>\n'
        xaml += f'{indent}    \n'
        
        # 检查子元素数量和布局需求
        children = node.get('children', [])
        visible_children = [c for c in children if c.get('visible', True)]
        
        # 检查是否有子元素需要填充(FILL or STRETCH)
        has_fill_child = any(
            child.get('layoutSizingHorizontal') == 'FILL' or 
            child.get('layoutAlign') == 'STRETCH' 
            for child in visible_children
        )
        
        # 对于根容器的水平布局,如果有多个子元素,使用 Grid 让最后一个元素填充剩余空间
        if is_root and layout_mode == 'HORIZONTAL' and len(visible_children) > 1:
            has_fill_child = True
        
        # 选择布局容器
        use_grid = False
        if layout_mode == 'HORIZONTAL' and layout_wrap == 'WRAP':
            xaml += f'{indent}    <WrapPanel Orientation="Horizontal"\n'
            xaml += f'{indent}               HorizontalAlignment="Center"\n'
            xaml += f'{indent}               VerticalAlignment="Center">\n'
            xaml += f'{indent}        \n'
        elif layout_mode == 'HORIZONTAL' and has_fill_child and len(visible_children) > 1:
            # 水平布局且有填充子元素 -> 使用 Grid
            use_grid = True
            xaml += f'{indent}    <Grid>\n'
            # 定义列
            xaml += f'{indent}        <Grid.ColumnDefinitions>\n'
            for i, child in enumerate(visible_children):
                # 检查是否是最后一个元素(在根容器中)或显式标记为 FILL
                is_last_in_root = (is_root and i == len(visible_children) - 1)
                is_fill = (child.get('layoutSizingHorizontal') == 'FILL' or 
                          child.get('layoutAlign') == 'STRETCH')
                
                if is_fill or is_last_in_root:
                    # 自动填充列
                    xaml += f'{indent}            <ColumnDefinition Width="*"/>\n'
                else:
                    # 自动调整列
                    xaml += f'{indent}            <ColumnDefinition Width="Auto"/>\n'
            xaml += f'{indent}        </Grid.ColumnDefinitions>\n'
            xaml += f'{indent}        \n'
        elif layout_mode == 'VERTICAL':
            # 垂直布局
            xaml += f'{indent}    <StackPanel Orientation="Vertical">\n'
            xaml += f'{indent}        \n'
        elif layout_mode == 'HORIZONTAL':
            # 水平布局
            xaml += f'{indent}    <StackPanel Orientation="Horizontal">\n'
            xaml += f'{indent}        \n'
        else:
            # 默认使用 StackPanel Vertical
            xaml += f'{indent}    <StackPanel Orientation="Vertical">\n'
            xaml += f'{indent}        \n'
        
        # 记录布局信息
        node['_item_spacing'] = item_spacing
        node['_use_grid'] = use_grid
        
        # 处理子元素
        # 确定当前布局类型(用于子元素的 Margin)
        if layout_mode == 'HORIZONTAL' and layout_wrap == 'WRAP':
            current_layout = 'WRAP'
        elif layout_mode == 'VERTICAL':
            current_layout = 'VERTICAL'
        elif layout_mode == 'HORIZONTAL':
            current_layout = 'HORIZONTAL'
        else:
            current_layout = 'NONE'
        
        # 遍历子元素
        visible_child_index = 0  # 可见子元素的索引
        for child in children:
            child_type = child.get('type')
            visible = child.get('visible', True)
            
            if not visible:
                continue  # 跳过不可见元素
            
            is_first = (visible_child_index == 0)
            
            # 判断当前子元素是否在填充列中
            is_in_fill_column_flag = False
            if use_grid:
                is_last_in_root = (is_root and visible_child_index == len(visible_children) - 1)
                is_fill = (child.get('layoutSizingHorizontal') == 'FILL' or 
                          child.get('layoutAlign') == 'STRETCH')
                is_in_fill_column_flag = is_fill or is_last_in_root
            
            # 如果使用 Grid,添加 Grid.Column 属性
            if use_grid:
                # 在子元素开始前保存缩进,后面会用到
                child_xaml_prefix = f'{self.indent * (indent_level + 2)}'
            
            if child_type == 'RECTANGLE':
                child_xaml = self.convert_rectangle(child, indent_level + 2, item_spacing, current_layout, is_first)
            elif child_type == 'FRAME':
                # 传递是否在填充列的信息(通过临时设置标记)
                if is_in_fill_column_flag:
                    child['_in_fill_column'] = True
                child_xaml = self.convert_frame(child, indent_level + 2)
                if is_in_fill_column_flag:
                    child.pop('_in_fill_column', None)
            elif child_type == 'TEXT':
                child_xaml = self.convert_text(child, indent_level + 2, item_spacing, current_layout, is_first)
            else:
                child_xaml = ''
            
            # 如果使用 Grid,在第一个 Border 或 TextBlock 标签后插入 Grid.Column
            if use_grid and child_xaml:
                # 找到第一个 < 之后的位置,插入 Grid.Column
                lines = child_xaml.split('\n')
                for i, line in enumerate(lines):
                    if '<Border' in line or '<TextBlock' in line:
                        # 在这一行后插入 Grid.Column 属性
                        # 检查是否是自闭合标签
                        if '/>' in line:
                            # 自闭合标签,在 /> 前插入
                            lines[i] = line.replace('/>', f' Grid.Column="{visible_child_index}"/>')
                        else:
                            # 非自闭合标签,在下一行添加或在当前行末尾添加
                            lines[i] = line.rstrip()
                            if lines[i].endswith('>'):
                                # 单行标签
                                lines[i] = lines[i][:-1] + f' Grid.Column="{visible_child_index}">'
                            else:
                                # 多行标签,下一行继续
                                if i + 1 < len(lines):
                                    lines.insert(i + 1, f'{child_xaml_prefix}        Grid.Column="{visible_child_index}"')
                        break
                child_xaml = '\n'.join(lines)
            
            xaml += child_xaml
            visible_child_index += 1
        
        # 关闭容器
        if layout_mode == 'HORIZONTAL' and layout_wrap == 'WRAP':
            xaml += f'{indent}    </WrapPanel>\n'
        elif use_grid:
            xaml += f'{indent}    </Grid>\n'
        else:
            xaml += f'{indent}    </StackPanel>\n'
        
        xaml += f'{indent}</Border>\n'
        
        return xaml
    
    def convert_text(self, node, indent_level=0, parent_spacing=0, parent_layout='NONE', is_first_child=False):
        """转换文本节点 - 提取文字、字体、字号等属性
        
        Args:
            parent_spacing: 父容器的 itemSpacing
            parent_layout: 父容器的布局模式 (HORIZONTAL/VERTICAL/WRAP)
            is_first_child: 是否是第一个子元素
        """
        indent = self.indent * indent_level
        
        name = node.get('name', 'Text')
        
        # 提取实际文字内容
        text = node.get('characters', name)
        
        # 提取字体信息
        font_name = node.get('fontName', {})
        font_family = font_name.get('family', 'Segoe UI')
        
        # 提取字号
        font_size = node.get('fontSize', 12)
        
        # 提取颜色
        opacity = node.get('opacity', 1.0)
        fills = node.get('fills', [])
        foreground = None
        if fills and len(fills) > 0:
            fill = fills[0]
            color = fill.get('color', '#000000')
            fill_opacity = fill.get('opacity', 1.0)
            final_opacity = opacity * fill_opacity
            # 黑色且完全不透明是默认值,可省略
            if color.upper() != '#000000' or final_opacity < 1.0:
                foreground = self.hex_to_wpf_color(color, final_opacity)
        
        # 提取宽高(可选)
        width = node.get('width')
        height = node.get('height')
        
        # 构建 XAML
        xaml = f'{indent}<!-- {name} -->\n'
        xaml += f'{indent}<TextBlock'
        
        # 必需属性
        xaml += f' Text="{text}"'
        
        # 可选属性(非默认值才添加)
        # WPF 默认字体是 Segoe UI,字号是系统字号(通常12)
        if font_family and font_family not in ['Segoe UI', 'Roboto']:
            xaml += f' FontFamily="{font_family}"'
        if font_size and font_size != 12:
            xaml += f' FontSize="{font_size}"'
        if foreground:
            xaml += f' Foreground="{foreground}"'
        if width:
            xaml += f' Width="{width}"'
        if height:
            xaml += f' Height="{height}"'
        
        # 根据父容器布局模式和间距添加 Margin
        if parent_spacing > 0 and not is_first_child:
            if parent_layout == 'WRAP':
                # WrapPanel: 四边都加间距
                half_spacing = parent_spacing / 2
                xaml += f' Margin="{half_spacing}"'
            elif parent_layout == 'VERTICAL':
                # 垂直布局: 只在上方加间距 (Left,Top,Right,Bottom)
                xaml += f' Margin="0,{parent_spacing},0,0"'
            elif parent_layout == 'HORIZONTAL':
                # 水平布局: 只在左边加间距 (Left,Top,Right,Bottom)
                xaml += f' Margin="{parent_spacing},0,0,0"'
        
        xaml += '/>\n'
        
        return xaml
    
    def generate_usercontrol(self, root_node, class_name="FigmaControl"):
        """生成完整的 UserControl XAML"""
        
        # 对于根节点,使用设计尺寸,但不限制实际尺寸
        width = root_node.get('width', 200)
        height = root_node.get('height', 200)
        
        xaml = f'<UserControl x:Class="YourNamespace.{class_name}"\n'
        xaml += f'             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n'
        xaml += f'             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n'
        xaml += f'             xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"\n'
        xaml += f'             xmlns:d="http://schemas.microsoft.com/expression/blend/2008"\n'
        xaml += f'             mc:Ignorable="d"\n'
        xaml += f'             d:DesignHeight="{height}" d:DesignWidth="{width}">\n'
        xaml += f'    \n'
        
        # 转换根节点 - 标记为根节点以便特殊处理
        node_type = root_node.get('type')
        if node_type == 'FRAME':
            xaml += self.convert_frame(root_node, indent_level=1, is_root=True)
        elif node_type == 'RECTANGLE':
            xaml += self.convert_rectangle(root_node, indent_level=1)
        
        xaml += '</UserControl>'
        
        return xaml
    
    def convert_file(self, input_json_path, output_xaml_path=None):
        """转换 JSON 文件到 XAML"""
        
        # 读取 JSON
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取压缩数据
        compressed_data = data.get('compressed_data', [])
        
        if not compressed_data:
            print("❌ 没有找到压缩数据！")
            return
        
        # 转换每个根节点
        for i, node in enumerate(compressed_data):
            node_name = node.get('name', f'Control{i}')
            class_name = node_name.replace(' ', '')  # 移除空格作为类名
            
            xaml_content = self.generate_usercontrol(node, class_name)
            
            # 确定输出文件名
            if output_xaml_path:
                output_file = output_xaml_path
            else:
                output_file = f"{class_name}.xaml"
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xaml_content)
            
            print(f"✅ 已生成: {output_file}")
            print(f"   节点名称: {node_name}")
            print(f"   节点类型: {node.get('type')}")
            print(f"   子元素数: {len(node.get('children', []))}")
            print()


def main():
    """主函数 - 支持命令行参数"""
    import sys
    
    # 设置 Windows 控制台 UTF-8 编码
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # 检查命令行参数
    if len(sys.argv) >= 3:
        # 命令行模式：python figma_to_xaml.py input.json output.xaml
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        if not Path(input_file).exists():
            print(f"❌ 找不到文件: {input_file}")
            sys.exit(1)
        
        converter = FigmaToXamlConverter()
        converter.convert_file(input_file, output_file)
        
        print(f"✅ 已生成: {output_file}")
        sys.exit(0)
    else:
        # 默认模式：使用 output_max.json
        print("=" * 60)
        print("Figma JSON → WPF XAML 转换器")
        print("=" * 60)
        print()
        
        converter = FigmaToXamlConverter()
        
        # 转换文件
        input_file = "output_max.json"
        
        if not Path(input_file).exists():
            print(f"❌ 找不到文件: {input_file}")
            return
        
        print(f"📂 输入文件: {input_file}")
        print()
        
        converter.convert_file(input_file)
        
        print("=" * 60)
        print("🎉 转换完成！")
        print("=" * 60)


if __name__ == "__main__":
    main()
