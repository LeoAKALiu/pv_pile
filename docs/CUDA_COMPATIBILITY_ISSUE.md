# CUDA 兼容性问题说明

## 问题描述

RTX 5090 GPU 的 CUDA capability (sm_120) 与当前 PyTorch 2.4.1 版本不完全兼容。

错误信息：
```
CUDA error: no kernel image is available for execution on the device
```

## 解决方案

### 方案一：使用 CPU 训练（临时方案）

虽然速度较慢，但可以正常训练：

```bash
./start_training_screen_cpu.sh
```

**注意**：CPU 训练会非常慢，可能需要数天时间。

### 方案二：升级 PyTorch（推荐）

需要安装支持 sm_120 的 PyTorch 版本。RTX 5090 是较新的 GPU，可能需要：

1. **安装最新的 PyTorch 版本**（支持 CUDA 12.1+ 和 sm_120）

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate /root/miniconda3/envs/yolov11

# 卸载旧版本
pip uninstall torch torchvision -y

# 安装最新版本（从 PyTorch 官网获取最新命令）
# 访问 https://pytorch.org/get-started/locally/ 获取最新安装命令
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

2. **或者使用 nightly 版本**（可能包含对 sm_120 的支持）

```bash
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu121
```

### 方案三：使用 Docker 容器

使用包含最新 PyTorch 的 Docker 容器：

```bash
# 使用 NVIDIA 官方 PyTorch 容器
docker run --gpus all -it --rm \
    -v /root/pv_pile:/workspace \
    pytorch/pytorch:latest \
    bash -c "cd /workspace && python src/models/trainer.py ..."
```

### 方案四：降级或使用其他 GPU

如果有其他兼容的 GPU，可以使用：

```bash
# 查看可用 GPU
nvidia-smi

# 使用其他 GPU（例如 GPU 1）
python src/models/trainer.py --device 1 ...
```

## 当前状态

- ✅ 基本 CUDA 功能可用（`torch.cuda.is_available()` 返回 True）
- ❌ 模型加载到 GPU 时失败（CUDA kernel 不兼容）
- ✅ CPU 模式可用（但速度很慢）

## 建议

1. **短期**：使用 CPU 模式进行小规模测试
2. **长期**：升级 PyTorch 到支持 sm_120 的版本，或联系 PyTorch 社区获取支持

## 检查 PyTorch 版本

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.version.cuda}')"
```

## 相关链接

- [PyTorch 安装指南](https://pytorch.org/get-started/locally/)
- [CUDA Compatibility](https://pytorch.org/get-started/previous-versions/)
- [RTX 5090 支持](https://github.com/pytorch/pytorch/issues)

