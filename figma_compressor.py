"""
Figma Node Inspector JSON 压缩工具

功能:
1. 基于 Figma 官方文档定义默认值
2. 删除所有等于默认值的属性
3. 删除可计算属性和 parent 引用
4. 递归压缩嵌套对象
5. 输出压缩后的 JSON 和默认值表

使用方法:
    python figma_compressor.py input.json output.json
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


# ==================== Figma 默认值定义 ====================

FIGMA_DEFAULTS = {
    "GLOBAL": {
        # 通用属性默认值
        "visible": True,
        "locked": False,
        "opacity": 1,
        "blendMode": "PASS_THROUGH",
        "isMask": False,
        "maskType": "ALPHA",
        "effects": [],
        "effectStyleId": "",
        "reactions": [],
        "isAsset": False,
        "detachedInfo": None,
        "stuckNodes": [],
        "attachedConnectors": [],
        "componentPropertyReferences": None,
        "variableConsumptionMap": {},
        "boundVariables": {},
        "resolvedVariableModes": {},
        "inferredVariables": {},
        "availableInferredVariables": {},
        "explicitVariableModes": {},
        "constrainProportions": False,
        "layoutGrow": 0,
        "layoutAlign": "INHERIT",
        "layoutPositioning": "AUTO",
        "minWidth": None,
        "minHeight": None,
        "maxWidth": None,
        "maxHeight": None,
        "rotation": 0,
        "exportSettings": [],
        "annotations": [],
        "playbackSettings": {
            "autoplay": True,
            "loop": True,
            "muted": False
        },
    },
    
    "RECTANGLE": {
        # Rectangle 特定默认值
        "fillStyleId": "",
        "fills": [],
        "strokes": [],
        "strokeStyleId": "",
        "strokeWeight": 1,
        "strokeAlign": "INSIDE",
        "strokeJoin": "MITER",
        "strokeCap": "NONE",
        "strokeMiterLimit": 4,
        "dashPattern": [],
        "cornerRadius": 0,
        "cornerSmoothing": 0,
        "topLeftRadius": 0,
        "topRightRadius": 0,
        "bottomLeftRadius": 0,
        "bottomRightRadius": 0,
        "strokeTopWeight": 1,
        "strokeBottomWeight": 1,
        "strokeLeftWeight": 1,
        "strokeRightWeight": 1,
        "fillGeometry": [],
        "strokeGeometry": [],
        "layoutSizingHorizontal": "FIXED",
        "layoutSizingVertical": "FIXED",
        "constraints": {
            "horizontal": "MIN",
            "vertical": "MIN"
        },
        "targetAspectRatio": None,
        "gridRowSpan": 1,
        "gridColumnSpan": 1,
        "gridRowAnchorIndex": -1,
        "gridColumnAnchorIndex": -1,
        "gridChildHorizontalAlign": "AUTO",
        "gridChildVerticalAlign": "AUTO",
    },
    
    "FRAME": {
        # Frame 特定默认值
        "fills": [],
        "fillStyleId": "",
        "strokes": [],
        "strokeStyleId": "",
        "strokeWeight": 1,
        "strokeAlign": "INSIDE",
        "strokeJoin": "MITER",
        "strokeCap": "NONE",
        "strokeMiterLimit": 4,
        "dashPattern": [],
        "cornerRadius": 0,
        "cornerSmoothing": 0,
        "topLeftRadius": 0,
        "topRightRadius": 0,
        "bottomLeftRadius": 0,
        "bottomRightRadius": 0,
        "strokeTopWeight": 1,
        "strokeBottomWeight": 1,
        "strokeLeftWeight": 1,
        "strokeRightWeight": 1,
        "fillGeometry": [],
        "strokeGeometry": [],
        "layoutSizingHorizontal": "FIXED",
        "layoutSizingVertical": "FIXED",
        "clipsContent": True,
        "layoutMode": "NONE",
        "paddingLeft": 0,
        "paddingRight": 0,
        "paddingTop": 0,
        "paddingBottom": 0,
        "itemSpacing": 0,
        "counterAxisSpacing": 0,
        "primaryAxisAlignItems": "MIN",
        "counterAxisAlignItems": "MIN",
        "primaryAxisSizingMode": "FIXED",
        "counterAxisSizingMode": "FIXED",
        "layoutWrap": "NO_WRAP",
        "counterAxisAlignContent": "AUTO",
        "layoutGrids": [],
        "gridStyleId": "",
        "backgrounds": [],
        "backgroundStyleId": "",
        "guides": [],
        "constraints": {
            "horizontal": "MIN",
            "vertical": "MIN"
        },
        "overflowDirection": "NONE",
        "numberOfFixedChildren": 0,
        "overlayPositionType": "CENTER",
        "overlayBackgroundInteraction": "NONE",
        "itemReverseZIndex": False,
        "strokesIncludedInLayout": False,
        "devStatus": None,
    },
    
    "TEXT": {
        # Text 特定默认值
        "fills": [],
        "fillStyleId": "",
        "strokes": [],
        "strokeStyleId": "",
        "strokeWeight": 1,
        "strokeAlign": "OUTSIDE",
        "strokeJoin": "MITER",
        "strokeCap": "NONE",
        "strokeMiterLimit": 4,
        "dashPattern": [],
        "textAlignHorizontal": "LEFT",
        "textAlignVertical": "TOP",
        "textAutoResize": "WIDTH_AND_HEIGHT",
        "paragraphIndent": 0,
        "paragraphSpacing": 0,
        "autoRename": True,
        "textStyleId": "",
        "fontSize": 12,
        "fontName": {
            "family": "Roboto",
            "style": "Regular"
        },
        "textCase": "ORIGINAL",
        "textDecoration": "NONE",
        "letterSpacing": {
            "unit": "PERCENT",
            "value": 0
        },
        "lineHeight": {
            "unit": "AUTO"
        },
        "constraints": {
            "horizontal": "MIN",
            "vertical": "MIN"
        },
    }
}


# 需要删除的可计算属性
COMPUTED_PROPERTIES = {
    "absoluteTransform",
    "absoluteBoundingBox",
    "absoluteRenderBounds",
    "parent",  # 可从树结构推断
    "fillGeometry",  # SVG 路径数据,可从形状属性重建
    "strokeGeometry",  # SVG 描边路径,可从形状属性重建
}

# 需要删除的 UI 状态和辅助属性
UI_STATE_PROPERTIES = {
    "expanded",  # Figma UI 状态
    "inferredAutoLayout",  # Figma 推断的布局,可能不准确
}

# Grid 布局相关属性(如果不使用 Grid 布局则删除)
GRID_PROPERTIES = {
    "gridRowSpan",
    "gridColumnSpan", 
    "gridRowAnchorIndex",
    "gridColumnAnchorIndex",
    "gridRowCount",
    "gridColumnCount",
    "gridRowGap",
    "gridColumnGap",
    "gridRowSizingCSS",
    "gridColumnSizingCSS",
}


# 无论如何都要保留的关键属性
CRITICAL_PROPERTIES = {
    "id",
    "type",
    "name",
    "children",  # 即使为空也保留
    "x",
    "y",
    "width",
    "height",
}


# ==================== 工具函数 ====================

def rgb_to_hex(r: float, g: float, b: float) -> str:
    """将 Figma RGB (0-1) 转换为 HEX 颜色"""
    # Figma 使用 0-1 范围的浮点数
    r_int = int(round(r * 255))
    g_int = int(round(g * 255))
    b_int = int(round(b * 255))
    return f"#{r_int:02X}{g_int:02X}{b_int:02X}"


def convert_color(color: Dict[str, float]) -> str:
    """转换颜色对象为 HEX 字符串"""
    if "r" in color and "g" in color and "b" in color:
        return rgb_to_hex(color["r"], color["g"], color["b"])
    return color


# ==================== 压缩逻辑 ====================

def get_default_value(node_type: str, property_name: str) -> Any:
    """获取指定节点类型的属性默认值"""
    # 先查找类型特定的默认值
    if node_type in FIGMA_DEFAULTS and property_name in FIGMA_DEFAULTS[node_type]:
        return FIGMA_DEFAULTS[node_type][property_name]
    
    # 再查找全局默认值
    if property_name in FIGMA_DEFAULTS["GLOBAL"]:
        return FIGMA_DEFAULTS["GLOBAL"][property_name]
    
    return None


def is_default_value(node_type: str, property_name: str, value: Any) -> bool:
    """判断属性值是否为默认值"""
    default = get_default_value(node_type, property_name)
    return default is not None and value == default


def is_empty_collection(value: Any) -> bool:
    """判断是否为空集合"""
    if isinstance(value, list):
        return len(value) == 0
    if isinstance(value, dict):
        return len(value) == 0
    return False


def compress_fill_or_stroke(item: Dict[str, Any]) -> Dict[str, Any]:
    """压缩 fills/strokes 数组中的单个对象"""
    compressed = {}
    
    # 保留 type (必需)
    if "type" in item:
        compressed["type"] = item["type"]
    
    # 保留非默认值的属性
    for key, value in item.items():
        if key == "type":
            continue
            
        # 跳过 null 值
        if value is None:
            continue
            
        # 检查是否为默认值
        if key == "visible" and value == True:
            continue
        if key == "opacity" and value == 1:
            continue
        if key == "blendMode" and value == "NORMAL":
            continue
        if key == "boundVariables" and is_empty_collection(value):
            continue
        
        # 转换颜色为 HEX
        if key == "color" and isinstance(value, dict):
            compressed[key] = convert_color(value)
        else:
            # 保留其他非默认值
            compressed[key] = value
    
    return compressed


def is_identity_transform(transform: Any) -> bool:
    """判断变换矩阵是否为标准形式 [[1, 0, x], [0, 1, y]]"""
    if not isinstance(transform, list) or len(transform) != 2:
        return False
    
    if not isinstance(transform[0], list) or len(transform[0]) != 3:
        return False
    if not isinstance(transform[1], list) or len(transform[1]) != 3:
        return False
    
    # 检查是否为标准变换 (无旋转、缩放、倾斜)
    # [[1, 0, x], [0, 1, y]]
    return (transform[0][0] == 1 and transform[0][1] == 0 and
            transform[1][0] == 0 and transform[1][1] == 1)


def compress_object(obj: Any, node_type: Optional[str] = None) -> Any:
    """递归压缩对象"""
    if not isinstance(obj, dict):
        return obj
    
    compressed = {}
    
    for key, value in obj.items():
        # 跳过 null 值
        if value is None:
            continue
            
        # 跳过计算属性
        if key in COMPUTED_PROPERTIES:
            continue
        
        # 跳过 UI 状态属性
        if key in UI_STATE_PROPERTIES:
            continue
        
        # 跳过 Grid 相关属性
        if key in GRID_PROPERTIES:
            continue
        
        # 跳过特定的空值对象
        if key == "overlayBackground" and value == {"type": "NONE"}:
            continue
        
        # 智能处理 relativeTransform
        if key == "relativeTransform":
            # 只保留非标准变换 (有旋转/缩放/倾斜)
            if not is_identity_transform(value):
                compressed[key] = value
            continue
        
        # 保留关键属性 (即使是 null 也要检查是否在 children 中)
        if key in CRITICAL_PROPERTIES:
            # children 即使为空也保留
            if key == "children":
                if isinstance(value, list):
                    compressed[key] = [compress_object(item, node_type) for item in value]
                else:
                    compressed[key] = value
            else:
                # 其他关键属性,跳过 null 值
                if value is not None:
                    compressed[key] = value
            continue
        
        # 跳过空集合 (除了 children)
        if is_empty_collection(value):
            continue
        
        # 跳过默认值
        if node_type and is_default_value(node_type, key, value):
            continue
        
        # 递归处理嵌套对象
        if isinstance(value, dict):
            compressed_value = compress_object(value, node_type)
            if compressed_value:  # 只保留非空对象
                compressed[key] = compressed_value
        elif isinstance(value, list):
            # 特殊处理 fills/strokes
            if key in ("fills", "strokes", "effects"):
                compressed_list = [compress_fill_or_stroke(item) if isinstance(item, dict) else item for item in value]
                if compressed_list:  # 只保留非空数组
                    compressed[key] = compressed_list
            else:
                compressed_list = [compress_object(item, node_type) for item in value]
                if compressed_list:
                    compressed[key] = compressed_list
        else:
            compressed[key] = value
    
    return compressed


def compress_node(node: Dict[str, Any]) -> Dict[str, Any]:
    """压缩单个节点"""
    node_type = node.get("type", "")
    
    # 递归压缩节点
    compressed = compress_object(node, node_type)
    
    # 递归处理子节点
    if "children" in compressed:
        compressed["children"] = [compress_node(child) for child in compressed["children"]]
    
    return compressed


def compress_tree(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """压缩节点树"""
    return [compress_node(node) for node in nodes]


# ==================== 主函数 ====================

def main():
    """主函数"""
    # 设置 Windows 控制台 UTF-8 编码
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("使用方法: python figma_compressor.py input.json [output.json]")
        print("如果不指定输出文件,将使用 input_compressed.json")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.parent / f"{input_path.stem}_compressed.json"
    
    # 读取输入文件
    print(f"读取文件: {input_path}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"错误: 无法读取文件 - {e}")
        sys.exit(1)
    
    # 压缩数据
    print("压缩中...")
    compressed_nodes = compress_tree(data)
    
    # 构建输出结构
    output = {
        "compressed_data": compressed_nodes,
        "defaults": FIGMA_DEFAULTS,
        "metadata": {
            "original_nodes": len(data),
            "compressed_nodes": len(compressed_nodes),
            "note": "本文件包含压缩后的 Figma 节点数据和默认值表。已删除所有默认值、可计算属性和空集合。"
        }
    }
    
    # 写入输出文件
    print(f"写入文件: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"错误: 无法写入文件 - {e}")
        sys.exit(1)
    
    # 统计信息
    original_size = input_path.stat().st_size
    compressed_size = output_path.stat().st_size
    reduction = (1 - compressed_size / original_size) * 100
    
    print(f"\n✅ 压缩完成!")
    print(f"原始大小: {original_size:,} bytes")
    print(f"压缩后大小: {compressed_size:,} bytes")
    print(f"压缩率: {reduction:.1f}%")


if __name__ == "__main__":
    main()
