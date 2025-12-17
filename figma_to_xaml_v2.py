"""
Figma 到 WPF XAML 转换器 V2
架构: AST + 规则引擎 + Python 字符串拼接
作者: GitHub Copilot
版本: 2.0
"""
import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ast_builder import FigmaToWpfBuilder
from src.wpf_ast import ASTOptimizer
from src.xaml_renderer import XamlRenderer


class FigmaToXamlConverter:
    """Figma 到 XAML 转换器 (V2 架构)
    
    使用 AST + 规则引擎 + Python 字符串拼接
    """
    
    def __init__(self, config_dir: str = 'config'):
        """初始化转换器
        
        Args:
            config_dir: 配置文件目录
        """
        self.builder = FigmaToWpfBuilder(config_dir)
        self.optimizer = ASTOptimizer(optimization_level=0)  # 第一版: 不优化
        self.renderer = XamlRenderer()
    
    def convert_node(self, figma_node: dict, is_root: bool = False) -> str:
        """转换单个 Figma 节点
        
        Args:
            figma_node: Figma JSON 节点
            is_root: 是否是根节点
        
        Returns:
            XAML 字符串
        """
        # 1. 构建 AST
        ast = self.builder.build(figma_node, is_root=is_root)
        
        # 2. 优化 AST (第一版: 不优化)
        # ast = self.optimizer.optimize(ast)
        
        # 3. 渲染 XAML
        node_name = figma_node.get('name', 'Control')
        class_name = node_name.replace(' ', '')
        
        design_width = figma_node.get('width', 200)
        design_height = figma_node.get('height', 200)
        
        xaml = self.renderer.render_usercontrol(
            ast,
            class_name=class_name,
            design_width=design_width,
            design_height=design_height
        )
        
        return xaml
    
    def convert_file(self, input_path: str, output_path: str = None) -> None:
        """转换 Figma JSON 文件
        
        Args:
            input_path: 输入的 JSON 文件路径
            output_path: 输出的 XAML 文件路径 (可选)
        """
        # 读取 JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取压缩数据
        compressed_data = data.get('compressed_data', [])
        
        if not compressed_data:
            print("❌ 没有找到压缩数据!")
            return
        
        # 转换每个根节点
        for i, node in enumerate(compressed_data):
            node_name = node.get('name', f'Control{i}')
            class_name = node_name.replace(' ', '')
            
            # 转换
            xaml_content = self.convert_node(node, is_root=True)
            
            # 确定输出文件名
            if output_path:
                output_file = output_path
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
    """主函数"""
    # 设置 Windows 控制台 UTF-8 编码
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 70)
    print("Figma JSON → WPF XAML 转换器 V2.0")
    print("架构: AST + 规则引擎 + Python 字符串拼接")
    print("=" * 70)
    print()
    
    # 检查命令行参数
    if len(sys.argv) >= 3:
        # 命令行模式: python figma_to_xaml_v2.py input.json output.xaml
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        if not Path(input_file).exists():
            print(f"❌ 找不到文件: {input_file}")
            sys.exit(1)
        
        converter = FigmaToXamlConverter()
        converter.convert_file(input_file, output_file)
        
        print(f"✅ 转换完成!")
        sys.exit(0)
    
    elif len(sys.argv) == 2:
        # 只有输入文件
        input_file = sys.argv[1]
        
        if not Path(input_file).exists():
            print(f"❌ 找不到文件: {input_file}")
            sys.exit(1)
        
        converter = FigmaToXamlConverter()
        converter.convert_file(input_file)
        
        print("=" * 70)
        print("🎉 转换完成!")
        print("=" * 70)
        sys.exit(0)
    
    else:
        # 默认模式
        print("📖 使用方法:")
        print("  python figma_to_xaml_v2.py <input.json> [output.xaml]")
        print()
        print("📂 默认输入: injson_compressed.json")
        print()
        
        input_file = "injson_compressed.json"
        
        if not Path(input_file).exists():
            print(f"❌ 找不到文件: {input_file}")
            print()
            print("💡 提示: 请在命令行中指定输入文件:")
            print("  python figma_to_xaml_v2.py your_file.json")
            sys.exit(1)
        
        converter = FigmaToXamlConverter()
        converter.convert_file(input_file)
        
        print("=" * 70)
        print("🎉 转换完成!")
        print("=" * 70)


if __name__ == "__main__":
    main()
