# Git 同步指南

## 📋 准备同步到 GitHub

项目已整理完成，可以同步到 GitHub 仓库。

## 🚀 快速开始

### 1. 初始化 Git 仓库（如果还没有）

```bash
cd /root/pv_pile
git init
```

### 2. 添加远程仓库

```bash
# 替换为你的 GitHub 仓库地址
git remote add origin https://github.com/yourusername/pv_pile.git

# 或使用 SSH
git remote add origin git@github.com:yourusername/pv_pile.git
```

### 3. 检查要提交的文件

```bash
# 查看会被提交的文件
git status

# 查看会被忽略的文件（应该包含 data/, runs/, *.pt 等）
git status --ignored
```

### 4. 添加文件到暂存区

```bash
# 添加所有应该提交的文件
git add .

# 或选择性添加
git add README.md
git add .gitignore
git add requirements.txt
git add src/
git add docs/
git add scripts/
git add PROJECT_STRUCTURE.md
```

### 5. 提交更改

```bash
git commit -m "Initial commit: PV Pile Detection project

- Add core source code (data preprocessing, training, inference)
- Add SAHI inference module
- Add comprehensive documentation
- Add training scripts
- Add project structure and requirements"
```

### 6. 推送到 GitHub

```bash
# 首次推送
git push -u origin main

# 或如果默认分支是 master
git push -u origin master
```

## 📝 提交前检查清单

- [ ] ✅ `.gitignore` 已配置，排除大文件和敏感信息
- [ ] ✅ `README.md` 已创建，包含项目说明
- [ ] ✅ `requirements.txt` 已创建，包含所有依赖
- [ ] ✅ 文档已整理到 `docs/` 目录
- [ ] ✅ 脚本已整理到 `scripts/` 目录
- [ ] ✅ 源代码在 `src/` 目录
- [ ] ✅ 大文件（data/, runs/, *.pt）已被忽略

## 🔍 验证忽略的文件

运行以下命令确认大文件不会被提交：

```bash
# 检查 .gitignore 是否生效
git status --ignored | grep -E "(data/|runs/|\.pt$|\.log$)"
```

应该看到这些文件/目录被忽略。

## 📦 大文件处理建议

### 选项 1: 使用 Git LFS（推荐用于模型权重）

如果需要版本控制模型权重，可以使用 Git LFS：

```bash
# 安装 Git LFS
git lfs install

# 跟踪 .pt 文件
git lfs track "*.pt"

# 添加 .gitattributes
git add .gitattributes
```

### 选项 2: 单独提供下载链接

在 README.md 中提供模型权重和数据集的下载链接。

### 选项 3: 使用 Releases

在 GitHub Releases 中上传大文件（模型权重、数据集等）。

## 🔄 后续更新流程

```bash
# 1. 查看更改
git status

# 2. 添加更改
git add .

# 3. 提交
git commit -m "描述你的更改"

# 4. 推送
git push
```

## 📋 推荐的提交信息格式

```
类型: 简短描述

详细描述（可选）

- 更改1
- 更改2
```

类型包括：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档更新
- `refactor`: 重构
- `test`: 测试
- `chore`: 其他

示例：

```
feat: Add SAHI inference module

- Implement sliced inference for large images
- Add batch processing support
- Add visualization output
```

## ⚠️ 注意事项

1. **不要提交大文件**: 确保 `data/`, `runs/`, `*.pt` 等被忽略
2. **检查敏感信息**: 确保没有提交 API 密钥、密码等
3. **保持提交清晰**: 每次提交应该有明确的目的
4. **定期推送**: 避免本地积累太多未提交的更改

## 🐛 常见问题

### 问题 1: 推送被拒绝（大文件）

如果之前误提交了大文件：

```bash
# 从历史中移除大文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/large/file" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（谨慎使用）
git push origin --force --all
```

### 问题 2: 远程仓库已存在内容

```bash
# 拉取远程更改
git pull origin main --allow-unrelated-histories

# 解决冲突后
git push
```

## 📚 相关资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 文档](https://docs.github.com/)
- [Git LFS 文档](https://git-lfs.github.com/)

---

*最后更新: 2025-01-27*


