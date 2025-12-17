"""
WPF AST (抽象语法树) 模型
作用: 表示 WPF XAML 的对象树结构
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class WpfNode:
    """WPF AST 节点基类
    
    表示一个 XAML 元素,如 Border, StackPanel, TextBlock 等
    """
    # 节点类型 (Border, StackPanel, Grid, WrapPanel, TextBlock)
    type: str
    
    # 属性字典 {属性名: 属性值}
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # 子节点列表
    children: List['WpfNode'] = field(default_factory=list)
    
    # 注释 (会生成 <!-- 注释 -->)
    comment: str = ''
    
    # 优化等级 (0=不优化, 1=基础优化, 2=激进优化)
    _optimization_level: int = 0
    
    def add_child(self, child: 'WpfNode') -> None:
        """添加子节点"""
        self.children.append(child)
    
    def set_attribute(self, name: str, value: Any, condition: bool = True) -> None:
        """条件设置属性
        
        Args:
            name: 属性名
            value: 属性值
            condition: 条件,为 True 时才设置
        """
        if condition and value is not None:
            self.attributes[name] = value
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """获取属性值"""
        return self.attributes.get(name, default)
    
    def remove_attribute(self, name: str) -> None:
        """移除属性"""
        if name in self.attributes:
            del self.attributes[name]
    
    def optimize(self) -> 'WpfNode':
        """优化 AST 节点
        
        根据 optimization_level 进行不同程度的优化
        Returns:
            优化后的节点 (可能是自己,也可能被替换)
        """
        if self._optimization_level == 0:
            # 不优化,直接返回
            # 但仍需递归优化子节点
            for i, child in enumerate(self.children):
                self.children[i] = child.optimize()
            return self
        
        # 未来可以添加优化逻辑
        # 例如:
        # - Level 1: 去除默认值属性
        # - Level 2: 合并嵌套容器 (需要谨慎)
        
        # 递归优化子节点
        for i, child in enumerate(self.children):
            self.children[i] = child.optimize()
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 (用于 JSON 序列化或模板渲染)
        
        Returns:
            字典格式:
            {
                'type': 'Border',
                'attributes': {'Width': '100', 'Height': '50'},
                'children': [...],
                'comment': 'Frame 1'
            }
        """
        return {
            'type': self.type,
            'attributes': self.attributes,
            'children': [child.to_dict() for child in self.children],
            'comment': self.comment
        }
    
    def __repr__(self) -> str:
        """字符串表示 (用于调试)"""
        attrs_str = ', '.join(f'{k}={v}' for k, v in self.attributes.items())
        children_count = len(self.children)
        return f"<{self.type} {attrs_str} ({children_count} children)>"


class ASTOptimizer:
    """AST 优化器
    
    对 WPF AST 进行优化,提升生成的 XAML 质量
    """
    
    def __init__(self, optimization_level: int = 0):
        """初始化优化器
        
        Args:
            optimization_level: 优化等级
                0 = 不优化 (第一版使用)
                1 = 基础优化 (去除默认值)
                2 = 激进优化 (合并容器,需谨慎)
        """
        self.level = optimization_level
    
    def optimize(self, root: WpfNode) -> WpfNode:
        """优化整个 AST 树
        
        Args:
            root: AST 根节点
        
        Returns:
            优化后的根节点
        """
        # 设置优化等级
        self._set_optimization_level(root, self.level)
        
        # 执行优化
        return root.optimize()
    
    def _set_optimization_level(self, node: WpfNode, level: int) -> None:
        """递归设置优化等级"""
        node._optimization_level = level
        for child in node.children:
            self._set_optimization_level(child, level)


# 便捷构造函数

def create_border(
    comment: str = '',
    **attributes
) -> WpfNode:
    """创建 Border 节点"""
    return WpfNode(type='Border', comment=comment, attributes=attributes)


def create_stackpanel(
    orientation: str = 'Vertical',
    comment: str = '',
    **attributes
) -> WpfNode:
    """创建 StackPanel 节点"""
    attrs = {'Orientation': orientation, **attributes}
    return WpfNode(type='StackPanel', comment=comment, attributes=attrs)


def create_grid(
    comment: str = '',
    **attributes
) -> WpfNode:
    """创建 Grid 节点"""
    return WpfNode(type='Grid', comment=comment, attributes=attributes)


def create_wrappanel(
    orientation: str = 'Horizontal',
    comment: str = '',
    **attributes
) -> WpfNode:
    """创建 WrapPanel 节点"""
    attrs = {'Orientation': orientation, **attributes}
    return WpfNode(type='WrapPanel', comment=comment, attributes=attrs)


def create_textblock(
    text: str,
    comment: str = '',
    **attributes
) -> WpfNode:
    """创建 TextBlock 节点"""
    attrs = {'Text': text, **attributes}
    return WpfNode(type='TextBlock', comment=comment, attributes=attrs)


# 测试代码
if __name__ == '__main__':
    # 测试 AST 构建
    root = create_border(
        comment='Main Container',
        Width='200',
        Height='100'
    )
    
    stack = create_stackpanel(
        orientation='Vertical',
        HorizontalAlignment='Left'
    )
    root.add_child(stack)
    
    text = create_textblock(
        text='Hello World',
        FontSize='16',
        FontWeight='Bold'
    )
    stack.add_child(text)
    
    # 打印 AST
    print(root)
    print("\nAST 字典:")
    import json
    print(json.dumps(root.to_dict(), indent=2, ensure_ascii=False))
    
    # 测试优化
    optimizer = ASTOptimizer(optimization_level=0)
    optimized = optimizer.optimize(root)
    print("\n优化后:")
    print(optimized)
