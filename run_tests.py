"""
自动化测试脚本
作用: 批量测试 Figma JSON 转 XAML,对比生成结果与预期结果
"""
import os
import json
from figma_to_xaml_v2 import FigmaToXamlConverter
from test_content_compare import compare_xaml_semantically

# 测试用例目录
TEST_CASES_DIR = "test_cases"
INPUTS_DIR = os.path.join(TEST_CASES_DIR, "inputs")
EXPECTED_DIR = os.path.join(TEST_CASES_DIR, "expected")
OUTPUT_DIR = os.path.join(TEST_CASES_DIR, "outputs")

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def extract_main_content(xaml_with_usercontrol):
    """从完整的 UserControl XAML 中提取主内容"""
    import re
    
    # 尝试提取 UserControl 内部的第一个主要元素
    # 匹配 <Border>, <Grid>, <StackPanel> 等
    pattern = r'<UserControl[^>]*>(.*)</UserControl>'
    match = re.search(pattern, xaml_with_usercontrol, re.DOTALL)
    
    if match:
        content = match.group(1).strip()
        
        # 移除注释
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL).strip()
        
        # 如果有 Border 包装,提取 Border
        if content.startswith('<Border'):
            return content
        
        # 如果直接是 Grid/StackPanel 等,直接返回
        return content
    
    # 如果没有 UserControl,直接返回原内容
    return xaml_with_usercontrol.strip()


def run_all_tests():
    """运行所有测试用例"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}开始运行测试套件{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    # 获取所有测试用例
    test_files = sorted([f for f in os.listdir(INPUTS_DIR) if f.endswith('.json')])
    
    if not test_files:
        print(f"{Colors.YELLOW}❌ 未找到测试用例{Colors.RESET}")
        return
    
    results = []
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_name = os.path.splitext(test_file)[0]
        result = run_single_test(test_name)
        results.append((test_name, result))
        
        if result['passed']:
            passed += 1
        else:
            failed += 1
    
    # 打印汇总
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}测试汇总{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result['passed'] else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{status} - {test_name}")
        if not result['passed']:
            print(f"  {Colors.RED}原因: {result['reason']}{Colors.RESET}")
            
            # 显示更多差异详情
            if result.get('details'):
                details = result['details']
                max_show = 10
                for i, detail in enumerate(details[:max_show], 1):
                    if '标签不同' in detail:
                        print(f"    {Colors.RED}• {detail}{Colors.RESET}")
                    elif '属性' in detail or '@' in detail:
                        print(f"    {Colors.YELLOW}• {detail}{Colors.RESET}")
                    else:
                        print(f"    • {detail}")
                
                if len(details) > max_show:
                    print(f"    {Colors.YELLOW}... 还有 {len(details) - max_show} 个差异{Colors.RESET}")
            
            # 显示文件路径
            if result.get('output_file') and result.get('expected_file'):
                print(f"    {Colors.BLUE}对比: code {result['output_file']} {result['expected_file']}{Colors.RESET}")
    
    # 统计
    total = passed + failed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}总计: {total} | 通过: {Colors.GREEN}{passed}{Colors.RESET}{Colors.BOLD} | 失败: {Colors.RED}{failed}{Colors.RESET}{Colors.BOLD} | 通过率: {pass_rate:.1f}%{Colors.RESET}\n")
    
    return results


def run_single_test(test_name):
    """运行单个测试用例"""
    print(f"\n{Colors.BLUE}▶ 测试: {test_name}{Colors.RESET}")
    
    input_file = os.path.join(INPUTS_DIR, f"{test_name}.json")
    expected_file = os.path.join(EXPECTED_DIR, f"{test_name}.xaml")
    output_file = os.path.join(OUTPUT_DIR, f"{test_name}.xaml")
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        return {'passed': False, 'reason': f'输入文件不存在: {input_file}'}
    
    if not os.path.exists(expected_file):
        return {'passed': False, 'reason': f'预期文件不存在: {expected_file}'}
    
    try:
        # 1. 读取输入 JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            figma_data = json.load(f)
        
        # 2. 转换为 XAML
        converter = FigmaToXamlConverter()
        
        # 获取第一个节点
        nodes = figma_data.get('compressed_data', [])
        if not nodes:
            return {'passed': False, 'reason': '没有找到 compressed_data'}
        
        xaml_output = converter.convert_node(nodes[0], is_root=True)
        
        # 3. 保存生成的 XAML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xaml_output)
        
        # 4. 读取预期的 XAML
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_xaml = f.read()
        
        # 5. 提取生成的 XAML 的主内容 (去掉 UserControl 包装)
        xaml_content = extract_main_content(xaml_output)
        
        # 6. 对比结果
        is_match, differences = compare_xaml_semantically(xaml_content, expected_xaml)
        
        if is_match:
            print(f"  {Colors.GREEN}✅ 测试通过{Colors.RESET}")
            return {'passed': True}
        else:
            print(f"  {Colors.RED}❌ 测试失败{Colors.RESET}")
            print(f"  {Colors.YELLOW}差异数量: {len(differences)}{Colors.RESET}\n")
            
            # 显示所有差异(如果太多则限制)
            max_display = 20
            for i, diff in enumerate(differences[:max_display], 1):
                # 根据差异类型添加颜色
                if '标签不同' in diff:
                    print(f"    {Colors.RED}{i}. {diff}{Colors.RESET}")
                elif '属性' in diff or '@' in diff:
                    print(f"    {Colors.YELLOW}{i}. {diff}{Colors.RESET}")
                elif '子元素' in diff:
                    print(f"    {Colors.BLUE}{i}. {diff}{Colors.RESET}")
                else:
                    print(f"    {i}. {diff}")
            
            if len(differences) > max_display:
                print(f"    {Colors.YELLOW}... 还有 {len(differences) - max_display} 个差异{Colors.RESET}")
            
            # 显示生成和预期的文件路径
            print(f"\n  {Colors.BLUE}📄 生成文件: {output_file}{Colors.RESET}")
            print(f"  {Colors.BLUE}📄 预期文件: {expected_file}{Colors.RESET}")
            
            return {
                'passed': False,
                'reason': f'生成的 XAML 与预期不符 (共 {len(differences)} 处差异)',
                'details': differences,
                'output_file': output_file,
                'expected_file': expected_file
            }
    
    except Exception as e:
        print(f"  {Colors.RED}❌ 测试异常: {str(e)}{Colors.RESET}")
        return {'passed': False, 'reason': f'异常: {str(e)}'}


def run_specific_tests(test_names):
    """运行指定的测试用例"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}运行指定测试: {', '.join(test_names)}{Colors.RESET}\n")
    
    results = []
    for test_name in test_names:
        result = run_single_test(test_name)
        results.append((test_name, result))
    
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 运行指定的测试
        test_names = sys.argv[1:]
        run_specific_tests(test_names)
    else:
        # 运行所有测试
        run_all_tests()
