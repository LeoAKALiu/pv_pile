# 后台训练指南

在远程服务器上训练时，可以使用以下方法让训练在后台持续运行，即使断开终端连接也不会中断。

## 方法一：使用 Screen（推荐）

Screen 是一个终端复用器，可以创建持久的会话，即使断开连接也能继续运行。

### 启动训练

```bash
# 使用提供的脚本
./start_training_screen.sh

# 或手动启动
screen -S yolo_training
source /root/miniconda3/etc/profile.d/conda.sh
conda activate /root/miniconda3/envs/yolov11
cd /root/pv_pile
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11s.pt \
    --epochs 200 \
    --batch 32 \
    --imgsz 1280 \
    --device 0 \
    --workers 8 \
    --patience 50 \
    --name pv_pile_yolo11s \
    --cos-lr
# 按 Ctrl+A，然后按 D 来分离会话
```

### Screen 常用命令

```bash
# 列出所有 screen 会话
screen -ls

# 连接到会话
screen -r yolo_training

# 分离会话（在 screen 内按）
Ctrl+A, 然后 D

# 终止会话
screen -S yolo_training -X quit

# 或先连接，然后输入 exit
```

## 方法二：使用 nohup

nohup 可以让命令在后台运行，忽略挂起信号。

### 启动训练

```bash
# 使用提供的脚本
./start_training_nohup.sh

# 或手动启动
cd /root/pv_pile
nohup bash -c "
    source /root/miniconda3/etc/profile.d/conda.sh && \
    conda activate /root/miniconda3/envs/yolov11 && \
    python src/models/trainer.py \
        --data data/processed/dataset.yaml \
        --model yolo11s.pt \
        --epochs 200 \
        --batch 32 \
        --imgsz 1280 \
        --device 0 \
        --workers 8 \
        --patience 50 \
        --name pv_pile_yolo11s \
        --cos-lr
" > training.log 2>&1 &
```

### 管理 nohup 进程

```bash
# 查看训练日志
tail -f training.log

# 查看进程
ps aux | grep trainer.py

# 停止训练（找到 PID 后）
kill <PID>

# 或使用 PID 文件
kill $(cat training.pid)
```

## 方法三：使用 tmux（如果已安装）

tmux 是另一个终端复用器，功能类似 screen。

### 启动训练

```bash
# 创建新会话
tmux new -s yolo_training

# 在 tmux 中运行训练命令
source /root/miniconda3/etc/profile.d/conda.sh
conda activate /root/miniconda3/envs/yolov11
cd /root/pv_pile
python src/models/trainer.py \
    --data data/processed/dataset.yaml \
    --model yolo11s.pt \
    --epochs 200 \
    --batch 32 \
    --imgsz 1280 \
    --device 0 \
    --workers 8 \
    --patience 50 \
    --name pv_pile_yolo11s \
    --cos-lr

# 分离会话：按 Ctrl+B，然后按 D
```

### tmux 常用命令

```bash
# 列出所有会话
tmux ls

# 连接到会话
tmux attach -t yolo_training

# 分离会话（在 tmux 内）
Ctrl+B, 然后 D

# 终止会话
tmux kill-session -t yolo_training
```

## 监控训练

### 查看训练日志

```bash
# 实时查看日志
tail -f training.log

# 查看最后 100 行
tail -100 training.log

# 搜索特定内容
grep "epoch" training.log
grep "mAP" training.log
```

### 查看 GPU 使用情况

```bash
# 实时监控
watch -n 1 nvidia-smi

# 或一次性查看
nvidia-smi
```

### 查看训练进度

```bash
# 查看训练结果目录
ls -lh runs/detect/pv_pile_yolo11s/

# 查看训练曲线（如果已生成）
ls -lh runs/detect/pv_pile_yolo11s/results.png

# 查看 CSV 结果
tail -20 runs/detect/pv_pile_yolo11s/results.csv
```

## 停止训练

### Screen 方法

```bash
# 连接到会话
screen -r yolo_training

# 在会话中按 Ctrl+C 停止训练
# 或直接终止会话
screen -S yolo_training -X quit
```

### nohup 方法

```bash
# 找到进程 ID
ps aux | grep trainer.py

# 停止进程
kill <PID>

# 或使用 PID 文件
kill $(cat training.pid)
```

### tmux 方法

```bash
# 连接到会话
tmux attach -t yolo_training

# 在会话中按 Ctrl+C 停止训练
# 或直接终止会话
tmux kill-session -t yolo_training
```

## 断点续训

如果训练中断，可以从检查点继续：

```bash
python src/models/trainer.py \
    --resume \
    --resume-path runs/detect/pv_pile_yolo11s/weights/last.pt \
    --data data/processed/dataset.yaml \
    --model yolo11s.pt \
    --epochs 200 \
    --batch 32 \
    --imgsz 1280 \
    --device 0
```

## 推荐方案

- **Screen**：适合需要交互式查看训练输出的场景
- **nohup**：适合完全后台运行，不需要交互的场景
- **tmux**：功能更强大，适合需要多个窗口的场景

对于当前场景，推荐使用 **Screen**，因为可以方便地查看训练进度和输出。

