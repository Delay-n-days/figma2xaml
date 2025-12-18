"""
智能 XAML 对比 - 提取关键信息对比
支持语义对比,忽略无关紧要的差异
"""
import re
from collections import Counter
import xml.etree.ElementTree as ET


def extract_elements(xaml):
    """提取所有元素及其属性"""
    # 提取所有元素标签
    elements = re.findall(r'<(\w+)[^/>]*(?:/>|>)', xaml)
    return Counter(elements)


def extract_attributes(xaml):
    """提取所有属性"""
    # 提取所有属性值对
    attrs = re.findall(r'(\w+)="([^"]*)"', xaml)
    return set(attrs)


def compare_xaml_content(file1, file2):
    """对比 XAML 内容 (忽略格式)"""
    with open(file1, 'r', encoding='utf-8') as f:
        content1 = f.read()
    
    with open(file2, 'r', encoding='utf-8') as f:
        content2 = f.read()
    
    # 提取元素
    elements1 = extract_elements(content1)
    elements2 = extract_elements(content2)
    
    print("📦 元素统计:")
    print(f"   V1: {dict(elements1)}")
    print(f"   V2: {dict(elements2)}")
    print()
    
    if elements1 == elements2:
        print("✅ 元素类型和数量完全一致!")
    else:
        print("❌ 元素统计有差异:")
        all_keys = set(elements1.keys()) | set(elements2.keys())
        for key in sorted(all_keys):
            count1 = elements1.get(key, 0)
            count2 = elements2.get(key, 0)
            if count1 != count2:
                print(f"   {key}: V1={count1}, V2={count2}")
    print()
    
    # 提取属性
    attrs1 = extract_attributes(content1)
    attrs2 = extract_attributes(content2)
    
    print(f"🔧 属性统计:")
    print(f"   V1 属性数: {len(attrs1)}")
    print(f"   V2 属性数: {len(attrs2)}")
    print()
    
    # 对比属性
    only_in_v1 = attrs1 - attrs2
    only_in_v2 = attrs2 - attrs1
    common = attrs1 & attrs2
    
    print(f"✅ 共同属性: {len(common)}")
    
    if only_in_v1:
        print(f"\n❌ 仅在 V1 中的属性 ({len(only_in_v1)}):")
        for attr, value in sorted(only_in_v1)[:10]:
            print(f"   {attr}=\"{value}\"")
        if len(only_in_v1) > 10:
            print(f"   ... 还有 {len(only_in_v1) - 10} 个")
    
    if only_in_v2:
        print(f"\n❌ 仅在 V2 中的属性 ({len(only_in_v2)}):")
        for attr, value in sorted(only_in_v2)[:10]:
            print(f"   {attr}=\"{value}\"")
        if len(only_in_v2) > 10:
            print(f"   ... 还有 {len(only_in_v2) - 10} 个")
    
    # 关键属性对比
    key_attrs = ['Width', 'Height', 'Background', 'Foreground', 'Padding', 'Margin']
    print(f"\n🔑 关键属性值对比:")
    for attr_name in key_attrs:
        v1_values = [v for k, v in attrs1 if k == attr_name]
        v2_values = [v for k, v in attrs2 if k == attr_name]
        
        if set(v1_values) == set(v2_values):
            print(f"   ✅ {attr_name}: 一致 ({len(v1_values)} 个)")
        else:
            print(f"   ❌ {attr_name}: 不一致")
            print(f"      V1: {set(v1_values)}")
            print(f"      V2: {set(v2_values)}")
    
    # 总结
    print(f"\n{'='*70}")
    if elements1 == elements2 and attrs1 == attrs2:
        print("🎉 完美! V1 和 V2 输出内容完全一致!")
    elif elements1 == elements2 and len(only_in_v1) == 0 and len(only_in_v2) == 0:
        print("✅ 优秀! 元素和属性完全一致,只有格式差异!")
    else:
        print("⚠️  存在内容差异,需要检查")
    print(f"{'='*70}")


if __name__ == '__main__':
    compare_xaml_content('out.xaml', 'out_v2.xaml')


def normalize_value(value):
    """标准化属性值,忽略微小差异"""
    if not value:
        return value
    
    # 标准化数字(去除多余小数点)
    try:
        num = float(value)
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}"
    except:
        pass
    
    # 标准化空格
    return ' '.join(value.split())


def compare_xaml_semantically(xaml1, xaml2, tolerance=2.0):
    """
    语义化对比两个 XAML 字符串
    
    Args:
        xaml1: 第一个 XAML 字符串
        xaml2: 第二个 XAML 字符串
        tolerance: 数值容差(像素)
    
    Returns:
        (is_match, differences): 是否匹配,差异列表
    """
    differences = []
    
    # 尝试解析为 XML
    try:
        # 包装成完整的 XML
        wrapped1 = f'<Root xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">{xaml1}</Root>'
        wrapped2 = f'<Root xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">{xaml2}</Root>'
        
        root1 = ET.fromstring(wrapped1)
        root2 = ET.fromstring(wrapped2)
        
        # 递归对比元素
        compare_elements(root1, root2, differences, tolerance, path="Root")
        
    except ET.ParseError as e:
        # XML 解析失败,回退到文本对比
        differences.append(f"XML 解析失败: {e}")
        return False, differences
    
    return len(differences) == 0, differences


def compare_elements(elem1, elem2, differences, tolerance, path=""):
    """递归对比两个 XML 元素"""
    # 去除命名空间
    tag1 = elem1.tag.split('}')[-1] if '}' in elem1.tag else elem1.tag
    tag2 = elem2.tag.split('}')[-1] if '}' in elem2.tag else elem2.tag
    
    # 对比标签名
    if tag1 != tag2:
        differences.append(f"{path}: 标签不同 ({tag1} vs {tag2})")
        return
    
    current_path = f"{path}/{tag1}"
    
    # 对比属性
    attrs1 = {k.split('}')[-1]: v for k, v in elem1.attrib.items()}
    attrs2 = {k.split('}')[-1]: v for k, v in elem2.attrib.items()}
    
    # 忽略的属性(不重要)
    ignore_attrs = {'xmlns', 'x:Name'}
    
    all_keys = (set(attrs1.keys()) | set(attrs2.keys())) - ignore_attrs
    
    for key in all_keys:
        val1 = attrs1.get(key, '')
        val2 = attrs2.get(key, '')
        
        if val1 != val2:
            # 检查是否是数值差异
            if is_numeric_diff_acceptable(val1, val2, tolerance):
                continue
            
            differences.append(f"{current_path}[@{key}]: '{val1}' vs '{val2}'")
    
    # 对比文本内容
    text1 = (elem1.text or '').strip()
    text2 = (elem2.text or '').strip()
    if text1 != text2:
        differences.append(f"{current_path}/text(): '{text1}' vs '{text2}'")
    
    # 对比子元素数量
    children1 = list(elem1)
    children2 = list(elem2)
    
    if len(children1) != len(children2):
        differences.append(f"{current_path}: 子元素数量不同 ({len(children1)} vs {len(children2)})")
        return
    
    # 递归对比子元素
    for child1, child2 in zip(children1, children2):
        compare_elements(child1, child2, differences, tolerance, current_path)


def is_numeric_diff_acceptable(val1, val2, tolerance):
    """检查数值差异是否可接受"""
    try:
        num1 = float(val1)
        num2 = float(val2)
        return abs(num1 - num2) <= tolerance
    except:
        return False

