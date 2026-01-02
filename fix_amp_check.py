#!/usr/bin/env python3
"""
修复 check_amp 函数，使其使用本地已有的 YOLOv11n 权重而不是下载 YOLOv8。

这个脚本会修改 ultralytics/ultralytics/utils/checks.py 文件中的 check_amp 函数。
"""

import re
from pathlib import Path


def fix_amp_check() -> None:
    """修复 check_amp 函数以使用本地 YOLOv11n 权重。"""
    checks_file = Path("ultralytics/ultralytics/utils/checks.py")
    
    if not checks_file.exists():
        print(f"❌ 文件不存在: {checks_file}")
        return
    
    # 读取文件
    content = checks_file.read_text(encoding='utf-8')
    
    # 查找 check_amp 函数中的 YOLO("yolo11n.pt") 调用
    # 将其改为使用绝对路径或本地路径
    pattern = r'(assert amp_allclose\(YOLO\(")yolo11n\.pt("\), im\))'
    
    # 检查本地是否有 yolo11n.pt
    local_weights = Path("/root/pv_pile/yolo11n.pt")
    if local_weights.exists():
        replacement = r'\1' + str(local_weights) + r'\2'
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            checks_file.write_text(new_content, encoding='utf-8')
            print(f"✅ 已修复 check_amp 函数，使用本地权重: {local_weights}")
        else:
            print("⚠️  未找到需要替换的内容，可能已经被修改过")
    else:
        print(f"⚠️  本地权重文件不存在: {local_weights}")
        print("   请确保 yolo11n.pt 文件在 /root/pv_pile/ 目录下")


if __name__ == "__main__":
    fix_amp_check()

