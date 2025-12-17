"""
XAML 渲染器
作用: 使用 Python 字符串拼接将 WPF AST 渲染为 XAML 字符串
"""
from src.wpf_ast import WpfNode
from typing import List, Dict, Any
import yaml
from pathlib import Path


class XamlRenderer:
    """XAML 渲染器
    
    使用纯 Python 字符串拼接渲染 WPF AST
    """
    
    def __init__(self, config_dir: str = 'config'):
        """初始化渲染器
        
        Args:
            config_dir: 配置文件目录
        """
        self.wpf_defaults = self._load_wpf_defaults(config_dir)
    
    def _load_wpf_defaults(self, config_dir: str) -> Dict[str, Dict[str, Any]]:
        """加载 WPF 默认值配置
        
        Args:
            config_dir: 配置文件目录
        
        Returns:
            WPF 默认值字典
        """
        defaults_file = Path(config_dir) / 'wpf_defaults.yaml'
        if defaults_file.exists():
            with open(defaults_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _is_default_value(self, control_type: str, attr_name: str, attr_value: str) -> bool:
        """判断属性值是否为默认值
        
        Args:
            control_type: 控件类型（如 'Border', 'Grid'）
            attr_name: 属性名
            attr_value: 属性值
        
        Returns:
            True 表示是默认值，应该排除
        """
        if control_type not in self.wpf_defaults:
            return False
        
        defaults = self.wpf_defaults[control_type]
        if attr_name not in defaults:
            return False
        
        default_value = str(defaults[attr_name])
        return str(attr_value) == default_value
    
    def render_usercontrol(
        self,
        root: WpfNode,
        class_name: str = 'FigmaControl',
        design_width: int = 200,
        design_height: int = 200
    ) -> str:
        """渲染 UserControl
        
        Args:
            root: WPF AST 根节点
            class_name: UserControl 类名
            design_width: 设计宽度
            design_height: 设计高度
        
        Returns:
            XAML 字符串
        """
        lines = []
        
        # UserControl 头部
        lines.append(f'<UserControl x:Class="YourNamespace.{class_name}"')
        lines.append('             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"')
        lines.append('             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"')
        lines.append('             xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"')
        lines.append('             xmlns:d="http://schemas.microsoft.com/expression/blend/2008"')
        lines.append('             mc:Ignorable="d"')
        lines.append(f'             d:DesignHeight="{design_height}" d:DesignWidth="{design_width}">')
        lines.append('')
        
        # 渲染根节点
        root_xaml = self.render_node(root, indent_level=1)
        lines.append(root_xaml)
        
        # UserControl 结束
        lines.append('</UserControl>')
        
        return '\n'.join(lines)
    
    def render_node(self, node: WpfNode, indent_level: int = 0) -> str:
        """渲染单个节点
        
        Args:
            node: WPF AST 节点
            indent_level: 缩进级别
        
        Returns:
            XAML 字符串
        """
        if node.type == 'Border':
            return self._render_border(node, indent_level)
        elif node.type == 'Grid':
            return self._render_grid(node, indent_level)
        elif node.type == 'StackPanel':
            return self._render_stackpanel(node, indent_level)
        elif node.type == 'WrapPanel':
            return self._render_wrappanel(node, indent_level)
        elif node.type == 'TextBlock':
            return self._render_textblock(node, indent_level)
        else:
            # 未知类型
            indent = '    ' * indent_level
            return f'{indent}<!-- 未知控件类型: {node.type} -->'
    
    def _get_indent(self, level: int) -> str:
        """获取缩进字符串"""
        return '    ' * level
    
    def _render_attributes(self, attributes: dict, indent_level: int, control_type: str = None) -> List[str]:
        """渲染属性列表
        
        Args:
            attributes: 属性字典
            indent_level: 缩进级别
            control_type: 控件类型（用于过滤默认值）
        
        Returns:
            属性行列表
        """
        lines = []
        indent = self._get_indent(indent_level)
        
        for key, value in attributes.items():
            if value is not None and not key.startswith('_'):
                # 检查是否为默认值
                if control_type and self._is_default_value(control_type, key, value):
                    continue
                lines.append(f'{indent}    {key}="{value}"')
        
        return lines


    def _render_border(self, node: WpfNode, indent_level: int) -> str:
        """渲染 Border 元素"""
        lines = []
        indent = self._get_indent(indent_level)
        
        # 注释
        if node.comment:
            lines.append(f'{indent}<!-- {node.comment} -->')
        
        # 开始标签
        lines.append(f'{indent}<Border')
        
        # 属性
        attr_lines = self._render_attributes(node.attributes, indent_level, 'Border')
        lines.extend(attr_lines)
        
        # 子元素
        if node.children:
            # 最后一个属性后直接跟 >
            if attr_lines:
                lines[-1] = lines[-1] + '>'
            else:
                lines[-1] = lines[-1] + '>'
            
            for child in node.children:
                child_xaml = self.render_node(child, indent_level + 1)
                lines.append(child_xaml)
            
            lines.append(f'{indent}</Border>')
        else:
            # 自闭合 />
            if attr_lines:
                lines[-1] = lines[-1] + '/>'
            else:
                lines[-1] = lines[-1] + '/>'
        
        return '\n'.join(lines)
    
    def _render_grid(self, node: WpfNode, indent_level: int) -> str:
        """渲染 Grid 元素"""
        lines = []
        indent = self._get_indent(indent_level)
        
        # 注释
        if node.comment:
            lines.append(f'{indent}<!-- {node.comment} -->')
        
        # 开始标签
        lines.append(f'{indent}<Grid')
        
        # 其他属性（排除行列定义）
        other_attrs = {k: v for k, v in node.attributes.items() 
                      if k not in ['_row_definitions', '_column_definitions']}
        attr_lines = self._render_attributes(other_attrs, indent_level, 'Grid')
        lines.extend(attr_lines)
        
        # 关闭开始标签
        if attr_lines:
            lines[-1] = lines[-1] + '>'
        else:
            lines[-1] = lines[-1] + '>'
        
        # 行定义
        row_defs = node.attributes.get('_row_definitions', [])
        if row_defs:
            lines.append(f'{indent}    <Grid.RowDefinitions>')
            for row_height in row_defs:
                lines.append(f'{indent}        <RowDefinition Height="{row_height}"/>')
            lines.append(f'{indent}    </Grid.RowDefinitions>')
        
        # 列定义
        col_defs = node.attributes.get('_column_definitions', [])
        if col_defs:
            lines.append(f'{indent}    <Grid.ColumnDefinitions>')
            for col_width in col_defs:
                lines.append(f'{indent}        <ColumnDefinition Width="{col_width}"/>')
            lines.append(f'{indent}    </Grid.ColumnDefinitions>')
        
        # 子元素
        for child in node.children:
            child_xaml = self.render_node(child, indent_level + 1)
            lines.append(child_xaml)
        
        lines.append(f'{indent}</Grid>')
        
        return '\n'.join(lines)
    
    def _render_stackpanel(self, node: WpfNode, indent_level: int) -> str:
        """渲染 StackPanel 元素"""
        lines = []
        indent = self._get_indent(indent_level)
        
        # 注释
        if node.comment:
            lines.append(f'{indent}<!-- {node.comment} -->')
        
        # 开始标签和属性
        lines.append(f'{indent}<StackPanel')
        attr_lines = self._render_attributes(node.attributes, indent_level, 'StackPanel')
        lines.extend(attr_lines)
        
        # 最后一个属性后直接跟 >
        if attr_lines:
            lines[-1] = lines[-1] + '>'
        else:
            lines[-1] = lines[-1] + '>'
        
        # 子元素
        for child in node.children:
            child_xaml = self.render_node(child, indent_level + 1)
            lines.append(child_xaml)
        
        lines.append(f'{indent}</StackPanel>')
        
        return '\n'.join(lines)
    
    def _render_wrappanel(self, node: WpfNode, indent_level: int) -> str:
        """渲染 WrapPanel 元素"""
        lines = []
        indent = self._get_indent(indent_level)
        
        # 注释
        if node.comment:
            lines.append(f'{indent}<!-- {node.comment} -->')
        
        # 开始标签和属性
        lines.append(f'{indent}<WrapPanel')
        attr_lines = self._render_attributes(node.attributes, indent_level, 'WrapPanel')
        lines.extend(attr_lines)
        
        # 最后一个属性后直接跟 >
        if attr_lines:
            lines[-1] = lines[-1] + '>'
        else:
            lines[-1] = lines[-1] + '>'
        
        # 子元素
        for child in node.children:
            child_xaml = self.render_node(child, indent_level + 1)
            lines.append(child_xaml)
        
        lines.append(f'{indent}</WrapPanel>')
        
        return '\n'.join(lines)
    
    def _render_textblock(self, node: WpfNode, indent_level: int) -> str:
        """渲染 TextBlock 元素"""
        lines = []
        indent = self._get_indent(indent_level)
        
        # 注释
        if node.comment:
            lines.append(f'{indent}<!-- {node.comment} -->')
        
        # 自闭合标签和属性
        lines.append(f'{indent}<TextBlock')
        attr_lines = self._render_attributes(node.attributes, indent_level, 'TextBlock')
        lines.extend(attr_lines)
        
        # 最后一个属性后直接跟 />
        if attr_lines:
            lines[-1] = lines[-1] + '/>'
        else:
            lines[-1] = lines[-1] + '/>'
        
        return '\n'.join(lines)


# 测试代码
if __name__ == '__main__':
    from src.wpf_ast import create_border, create_stackpanel, create_textblock, create_grid
    
    # 创建测试 AST
    root = create_border(
        comment='测试容器',
        Width='200',
        Height='100',
        Background='#FFFFFF'
    )
    
    grid = create_grid()
    grid.set_attribute('_row_definitions', ['1*', '1*'])
    grid.set_attribute('_column_definitions', ['Auto', '*'])
    root.add_child(grid)
    
    text1 = create_textblock(
        comment='测试文本1',
        Text='Hello',
        FontSize='16'
    )
    text1.set_attribute('Grid.Row', '0')
    text1.set_attribute('Grid.Column', '0')
    grid.add_child(text1)
    
    text2 = create_textblock(
        comment='测试文本2',
        Text='World',
        FontWeight='Bold'
    )
    text2.set_attribute('Grid.Row', '0')
    text2.set_attribute('Grid.Column', '1')
    grid.add_child(text2)
    
    # 渲染
    renderer = XamlRenderer()
    xaml = renderer.render_usercontrol(root, class_name='TestControl', design_width=200, design_height=100)
    
    print(xaml)
