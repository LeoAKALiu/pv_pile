#!/usr/bin/env python3
"""
对比不同训练运行的结果。

分析训练指标，包括：
- mAP50, mAP50-95
- Precision, Recall
- Loss 值
- 训练轮数
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional


def read_results_csv(csv_path: Path) -> List[Dict]:
    """读取 results.csv 文件。

    Args:
        csv_path: CSV 文件路径

    Returns:
        包含所有训练轮次数据的列表
    """
    results = []
    if not csv_path.exists():
        return results

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 去除列名的前导空格
            row = {k.strip(): v for k, v in row.items()}
            # 转换数值字段
            for key in row:
                if key == 'epoch':
                    try:
                        row[key] = int(float(row[key])) if row[key] else 0
                    except (ValueError, TypeError):
                        row[key] = 0
                else:
                    try:
                        row[key] = float(row[key]) if row[key] else 0.0
                    except (ValueError, TypeError):
                        row[key] = 0.0
            results.append(row)

    return results


def get_best_metrics(results: List[Dict]) -> Dict:
    """获取最佳指标。

    Args:
        results: 训练结果列表

    Returns:
        包含最佳指标的字典
    """
    if not results:
        return {}

    # 找到 mAP50-95 最高的轮次
    best_epoch = max(results, key=lambda x: float(x.get('metrics/mAP50-95(B)', 0) or 0))
    
    return {
        'epoch': int(best_epoch.get('epoch', 0) or 0),
        'mAP50': float(best_epoch.get('metrics/mAP50(B)', 0) or 0),
        'mAP50-95': float(best_epoch.get('metrics/mAP50-95(B)', 0) or 0),
        'precision': float(best_epoch.get('metrics/precision(B)', 0) or 0),
        'recall': float(best_epoch.get('metrics/recall(B)', 0) or 0),
        'train_loss': float(best_epoch.get('train/box_loss', 0) or 0) + 
                     float(best_epoch.get('train/cls_loss', 0) or 0) + 
                     float(best_epoch.get('train/dfl_loss', 0) or 0),
        'val_loss': float(best_epoch.get('val/box_loss', 0) or 0) + 
                   float(best_epoch.get('val/cls_loss', 0) or 0) + 
                   float(best_epoch.get('val/dfl_loss', 0) or 0),
    }


def get_final_metrics(results: List[Dict]) -> Dict:
    """获取最终轮次的指标。

    Args:
        results: 训练结果列表

    Returns:
        包含最终指标的字典
    """
    if not results:
        return {}

    final = results[-1]
    
    return {
        'epoch': int(final.get('epoch', 0) or 0),
        'mAP50': float(final.get('metrics/mAP50(B)', 0) or 0),
        'mAP50-95': float(final.get('metrics/mAP50-95(B)', 0) or 0),
        'precision': float(final.get('metrics/precision(B)', 0) or 0),
        'recall': float(final.get('metrics/recall(B)', 0) or 0),
        'train_loss': float(final.get('train/box_loss', 0) or 0) + 
                     float(final.get('train/cls_loss', 0) or 0) + 
                     float(final.get('train/dfl_loss', 0) or 0),
        'val_loss': float(final.get('val/box_loss', 0) or 0) + 
                   float(final.get('val/cls_loss', 0) or 0) + 
                   float(final.get('val/dfl_loss', 0) or 0),
    }


def compare_results(run_dirs: List[Path]) -> None:
    """对比多个训练运行的结果。

    Args:
        run_dirs: 训练运行目录列表
    """
    print("=" * 80)
    print("训练结果对比")
    print("=" * 80)

    all_results = {}
    
    for run_dir in run_dirs:
        csv_path = run_dir / "results.csv"
        if not csv_path.exists():
            print(f"\n⚠️  {run_dir.name}: results.csv 不存在，跳过")
            continue

        results = read_results_csv(csv_path)
        if not results:
            print(f"\n⚠️  {run_dir.name}: 没有训练数据")
            continue

        best = get_best_metrics(results)
        final = get_final_metrics(results)
        
        all_results[run_dir.name] = {
            'best': best,
            'final': final,
            'total_epochs': len(results),
        }

    if not all_results:
        print("\n❌ 没有可对比的训练结果")
        return

    # 打印对比表格
    print("\n【最佳指标对比】")
    print(f"{'训练运行':<20} {'轮次':<8} {'mAP50':<10} {'mAP50-95':<12} {'Precision':<12} {'Recall':<12}")
    print("-" * 80)
    
    for name, data in sorted(all_results.items()):
        best = data['best']
        print(f"{name:<20} {best['epoch']:<8} {best['mAP50']:<10.4f} {best['mAP50-95']:<12.4f} "
              f"{best['precision']:<12.4f} {best['recall']:<12.4f}")

    print("\n【最终指标对比】")
    print(f"{'训练运行':<20} {'轮次':<8} {'mAP50':<10} {'mAP50-95':<12} {'Precision':<12} {'Recall':<12}")
    print("-" * 80)
    
    for name, data in sorted(all_results.items()):
        final = data['final']
        print(f"{name:<20} {final['epoch']:<8} {final['mAP50']:<10.4f} {final['mAP50-95']:<12.4f} "
              f"{final['precision']:<12.4f} {final['recall']:<12.4f}")

    print("\n【训练统计】")
    print(f"{'训练运行':<20} {'总轮次':<10} {'最佳轮次':<10}")
    print("-" * 80)
    
    for name, data in sorted(all_results.items()):
        print(f"{name:<20} {data['total_epochs']:<10} {data['best']['epoch']:<10}")

    # 找出最佳训练
    if len(all_results) > 1:
        best_run = max(all_results.items(), key=lambda x: x[1]['best']['mAP50-95'])
        print(f"\n🏆 最佳训练: {best_run[0]}")
        print(f"   mAP50-95: {best_run[1]['best']['mAP50-95']:.4f}")
        print(f"   mAP50: {best_run[1]['best']['mAP50']:.4f}")
        print(f"   轮次: {best_run[1]['best']['epoch']}")

    print("\n" + "=" * 80)


def main() -> None:
    """主函数。"""
    base_dir = Path("/root/pv_pile/runs/detect")
    
    # 获取所有训练目录
    run_dirs = []
    if len(sys.argv) > 1:
        # 从命令行参数获取
        for arg in sys.argv[1:]:
            run_dir = base_dir / arg
            if run_dir.exists():
                run_dirs.append(run_dir)
    else:
        # 自动查找所有训练目录
        for run_dir in sorted(base_dir.glob("train*")):
            if run_dir.is_dir():
                run_dirs.append(run_dir)
        
        # 也包含其他命名格式的训练
        for run_dir in sorted(base_dir.glob("pv_pile_*")):
            if run_dir.is_dir() and (run_dir / "results.csv").exists():
                run_dirs.append(run_dir)

    if not run_dirs:
        print("❌ 没有找到训练结果目录")
        return

    compare_results(run_dirs)


if __name__ == "__main__":
    main()

