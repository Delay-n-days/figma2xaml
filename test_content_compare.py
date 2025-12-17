"""
智能 XAML 对比 - 提取关键信息对比
"""
import re
from collections import Counter


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
