"""
规则引擎 - Rule Engine
作用: 加载 YAML 配置,执行条件表达式求值,返回匹配结果
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class SafeEvaluator:
    """安全的表达式求值器
    
    只支持简单的比较和逻辑运算,防止代码注入
    支持的操作:
    - 比较: ==, !=, >, <, >=, <=
    - 逻辑: and, or, not
    - 成员: in, not in
    - 函数: is None, is not None
    """
    
    def eval(self, expression: str, context: Dict[str, Any]) -> bool:
        """求值表达式
        
        Args:
            expression: 条件表达式字符串,如 "layout_mode == 'HORIZONTAL' and has_fill_child"
            context: 上下文变量,如 {'layout_mode': 'HORIZONTAL', 'has_fill_child': True}
        
        Returns:
            布尔值结果
        """
        # 特殊情况: true/false 字面量
        if expression.strip() == 'true':
            return True
        if expression.strip() == 'false':
            return False
        
        # 构建安全的求值环境
        # 只暴露上下文变量,不暴露任何内置函数
        safe_globals = {
            '__builtins__': {},  # 禁用所有内置函数
        }
        safe_locals = context.copy()
        
        try:
            # 使用 eval 求值 (在受限环境中)
            result = eval(expression, safe_globals, safe_locals)
            return bool(result)
        except Exception as e:
            # 求值失败,返回 False 并打印警告
            print(f"⚠️ 表达式求值失败: {expression}")
            print(f"   错误: {e}")
            print(f"   上下文: {context}")
            return False


class RuleEngine:
    """规则引擎
    
    加载 YAML 配置文件,提供规则匹配和属性计算功能
    """
    
    def __init__(self, config_dir: str = 'config'):
        """初始化规则引擎
        
        Args:
            config_dir: 配置文件目录路径
        """
        self.config_dir = Path(config_dir)
        self.evaluator = SafeEvaluator()
        
        # 加载配置文件
        self.mappings = self._load_yaml('figma_wpf_mapping.yaml')
        self.layout_rules = self._load_yaml('layout_rules.yaml')
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"配置文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def select_container(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """根据规则选择布局容器
        
        Args:
            context: 上下文信息,如:
                {
                    'layout_mode': 'HORIZONTAL',
                    'layout_wrap': 'NO_WRAP',
                    'has_fill_child': True,
                    'visible_children_count': 2
                }
        
        Returns:
            容器配置,如:
                {
                    'container_type': 'Grid',
                    'use_grid': True
                }
        """
        rules = self.layout_rules['container_selection_rules']
        
        for rule in rules:
            condition = rule['condition']
            
            # 求值条件
            if self.evaluator.eval(condition, context):
                return rule['result']
        
        # 默认返回 StackPanel (Vertical)
        return {
            'container_type': 'StackPanel',
            'orientation': 'Vertical',
            'use_grid': False
        }
    
    def calculate_attribute(
        self, 
        control_type: str,
        attr_name: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """根据规则计算属性值
        
        Args:
            control_type: 控件类型,如 'Border', 'StackPanel', 'TextBlock'
            attr_name: 属性名,如 'Width', 'HorizontalAlignment'
            context: 上下文信息,包含所有可能用到的变量
        
        Returns:
            属性值字符串,如果不应设置此属性则返回 None
        """
        # 获取规则
        rules = self.layout_rules['attribute_rules'].get(control_type, {}).get(attr_name, [])
        
        if not rules:
            # 尝试通用规则
            rules = self.layout_rules['attribute_rules'].get('Common', {}).get(attr_name, [])
        
        if not rules:
            return None
        
        # 遍历规则,返回第一个匹配的
        for rule in rules:
            condition = rule['condition']
            
            if self.evaluator.eval(condition, context):
                value_template = rule['value']
                
                # 替换模板变量
                try:
                    # 支持简单的表达式: {parent_spacing / 2}
                    value = self._evaluate_value_template(value_template, context)
                    return value
                except Exception as e:
                    print(f"⚠️ 属性值模板求值失败: {value_template}")
                    print(f"   错误: {e}")
                    return None
        
        return None
    
    def _evaluate_value_template(self, template: str, context: Dict[str, Any]) -> str:
        """求值属性值模板
        
        支持:
        - 简单变量替换: {width} → "100"
        - 表达式计算: {parent_spacing / 2} → "5"
        """
        if not isinstance(template, str):
            return str(template)
        
        # 检查是否包含模板变量
        if '{' not in template:
            return template
        
        # 提取所有 {...} 变量
        import re
        pattern = r'\{([^}]+)\}'
        
        def replace_var(match):
            expr = match.group(1).strip()
            
            # 在安全环境中求值
            safe_globals = {'__builtins__': {}}
            safe_locals = context.copy()
            
            try:
                result = eval(expr, safe_globals, safe_locals)
                
                # 格式化结果
                if isinstance(result, float):
                    # 浮点数转整数(如果是整数值)
                    if result == int(result):
                        return str(int(result))
                    else:
                        return str(result)
                else:
                    return str(result)
            except Exception as e:
                print(f"⚠️ 模板变量求值失败: {expr}")
                return match.group(0)  # 返回原始字符串
        
        return re.sub(pattern, replace_var, template)
    
    def get_alignment(
        self, 
        align_type: str,  # 'counter_axis' or 'primary_axis'
        align_value: str,  # 'MIN', 'CENTER', 'MAX'
        direction: str     # 'horizontal' or 'vertical'
    ) -> str:
        """获取对齐方式映射
        
        Args:
            align_type: 对齐类型 ('counter_axis' 或 'primary_axis')
            align_value: Figma 对齐值 ('MIN', 'CENTER', 'MAX')
            direction: 方向 ('horizontal' 或 'vertical')
        
        Returns:
            WPF 对齐值,如 'Left', 'Center', 'Right', 'Top', 'Bottom'
        """
        mapping = self.mappings['alignment_mapping'][align_type]
        return mapping.get(align_value, {}).get(direction, 'Left' if direction == 'horizontal' else 'Top')
    
    def should_set_dimension(self, sizing_mode: str) -> bool:
        """判断是否应该设置固定尺寸
        
        Args:
            sizing_mode: Figma 尺寸模式 ('FIXED', 'HUG', 'FILL')
        
        Returns:
            True 表示应该设置固定宽高
        """
        config = self.mappings['sizing_mode'].get(sizing_mode, {})
        return config.get('set_dimension', False)
    
    def should_stretch(self, sizing_mode: str) -> bool:
        """判断是否应该拉伸
        
        Args:
            sizing_mode: Figma 尺寸模式 ('FIXED', 'HUG', 'FILL')
        
        Returns:
            True 表示应该设置 Stretch 对齐
        """
        config = self.mappings['sizing_mode'].get(sizing_mode, {})
        return config.get('stretch', False)


# 测试代码
if __name__ == '__main__':
    # 测试规则引擎
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
    
    # 测试属性计算
    context = {
        'sizing_horizontal': 'FIXED',
        'width': 100,
        'height': 50
    }
    width = engine.calculate_attribute('Border', 'Width', context)
    print("Width 属性:", width)
