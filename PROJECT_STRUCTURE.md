# 项目结构说明

## 📁 目录结构

```
pv_pile/
├── .gitignore              # Git 忽略文件配置
├── .gitattributes          # Git 属性配置
├── README.md               # 项目主文档
├── requirements.txt        # Python 依赖
├── PROJECT_STRUCTURE.md    # 本文件
│
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── data/               # 数据预处理模块
│   │   ├── __init__.py
│   │   ├── preprocess.py   # COCO 转 YOLO + 切片处理
│   │   ├── visualize_dataset.py  # 数据集可视化
│   │   └── README.md
│   ├── models/             # 模型训练模块
│   │   ├── __init__.py
│   │   ├── trainer.py       # 训练脚本
│   │   └── README.md
│   ├── inference/          # 推理模块
│   │   ├── __init__.py
│   │   ├── sahi_inference.py  # SAHI 推理脚本
│   │   └── README.md
│   └── utils/              # 工具函数（如有）
│
├── scripts/                # 训练脚本
│   ├── start_training_screen.sh      # Screen 后台训练
│   ├── start_training_final_v1.sh    # final_v1 实验
│   ├── start_training_opt1.sh        # 优化方案1
│   ├── start_training_opt2.sh        # 优化方案2
│   └── optimize_training.sh          # 优化脚本
│
├── docs/                   # 文档目录
│   ├── README.md           # 文档索引
│   ├── AGENTS.md           # 开发指南
│   ├── QUICKSTART.md       # 快速开始
│   ├── EXPERIMENTS_SUMMARY.md  # 实验总结
│   ├── TRAINING_*.md       # 训练相关文档
│   ├── SAHI_*.md           # SAHI 相关文档
│   └── ...
│
├── tests/                  # 测试目录（如有）
│
├── data/                   # 数据目录（不包含在 git 中）
│   ├── raw/                # 原始数据
│   ├── processed/          # 处理后的数据
│   │   ├── dataset.yaml    # YOLO 数据集配置
│   │   ├── train/          # 训练集
│   │   ├── val/            # 验证集
│   │   └── test/           # 测试集
│   └── visualizations/     # 可视化结果
│
├── runs/                   # 训练结果（不包含在 git 中）
│   └── detect/             # 检测任务结果
│       ├── train4/         # 最佳模型训练结果
│       ├── train_final_v1/ # final_v1 实验
│       └── ...
│
└── ultralytics/            # Ultralytics YOLO 源码（可选，建议作为子模块）
```

## 📝 文件说明

### 核心代码

- `src/data/preprocess.py`: 数据预处理主脚本
  - COCO 格式转 YOLO 格式
  - 大图像切片处理
  - 数据集划分

- `src/models/trainer.py`: 模型训练主脚本
  - 支持丰富的超参数配置
  - 数据增强选项
  - 学习率调度

- `src/inference/sahi_inference.py`: SAHI 推理脚本
  - 切片推理
  - 批量处理
  - 结果保存

### 脚本文件

- `scripts/start_training_*.sh`: 各种训练配置脚本
  - 使用 screen 后台运行
  - 自动日志记录

### 文档文件

- `docs/AGENTS.md`: 项目开发指南
- `docs/QUICKSTART.md`: 快速开始指南
- `docs/EXPERIMENTS_SUMMARY.md`: 实验总结

## 🚫 不包含在 Git 中的文件

以下文件/目录太大或包含敏感信息，不包含在 git 仓库中：

- `data/`: 数据文件（829MB+）
- `runs/`: 训练结果（550MB+）
- `DatasetId_853_1766643148/`: 原始数据集（345MB+）
- `*.pt`: 模型权重文件
- `*.log`: 训练日志
- `ultralytics/`: Ultralytics 源码（建议作为子模块）

## 📦 如何获取完整项目

1. **克隆仓库**:
   ```bash
   git clone <repository-url>
   cd pv_pile
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **下载数据**（需要单独提供）:
   - 将数据放在 `data/` 目录
   - 或使用数据预处理脚本处理原始数据

4. **下载模型权重**（可选）:
   - 最佳模型: `runs/detect/train4/weights/best.pt`
   - 或重新训练模型

## 🔧 开发建议

1. **代码规范**: 参考 `docs/AGENTS.md`
2. **提交前检查**: 确保代码通过 lint 检查
3. **文档更新**: 修改代码时同步更新文档
4. **测试**: 添加必要的单元测试

---

*最后更新: 2025-01-27*


