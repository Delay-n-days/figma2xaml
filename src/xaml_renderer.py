"""
XAML 渲染器
作用: 使用 Jinja2 模板将 WPF AST 渲染为 XAML 字符串
"""
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from src.wpf_ast import WpfNode


class XamlRenderer:
    """XAML 渲染器
    
    使用 Jinja2 模板引擎渲染 WPF AST
    """
    
    def __init__(self, template_dir: str = 'templates'):
        """初始化渲染器
        
        Args:
            template_dir: 模板目录路径
        """
        self.template_dir = Path(template_dir)
        
        # 初始化 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,          # 不删除块后的第一个换行符
            lstrip_blocks=False,        # 不删除块前的空白
            keep_trailing_newline=True  # 保留尾部换行符
        )
    
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
        # 加载基础模板
        template = self.env.get_template('base.xaml.j2')
        
        # 渲染
        xaml = template.render(
            root=root,
            class_name=class_name,
            design_width=design_width,
            design_height=design_height
        )
        
        return xaml
    
    def render_node(self, node: WpfNode, indent_level: int = 0) -> str:
        """渲染单个节点 (用于调试)
        
        Args:
            node: WPF AST 节点
            indent_level: 缩进级别
        
        Returns:
            XAML 字符串
        """
        # 加载宏模板
        template = self.env.from_string(
            "{% from 'macros/helpers.j2' import render_control %}"
            "{{ render_control(node, indent_level) }}"
        )
        
        return template.render(node=node, indent_level=indent_level)


# 测试代码
if __name__ == '__main__':
    from src.wpf_ast import create_border, create_stackpanel, create_textblock
    
    # 创建测试 AST
    root = create_border(
        comment='测试容器',
        Width='200',
        Height='100',
        Background='#FFFFFF'
    )
    
    stack = create_stackpanel(orientation='Vertical')
    root.add_child(stack)
    
    text = create_textblock(
        text='Hello World',
        comment='测试文本',
        FontSize='16',
        FontWeight='Bold'
    )
    stack.add_child(text)
    
    # 渲染
    renderer = XamlRenderer('templates')
    xaml = renderer.render_usercontrol(root, class_name='TestControl', design_width=200, design_height=100)
    
    print(xaml)
