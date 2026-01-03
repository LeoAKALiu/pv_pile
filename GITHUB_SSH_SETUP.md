# GitHub SSH 配置指南

## 问题：Permission denied (publickey)

当使用 SSH URL (`git@github.com:...`) 时出现此错误，说明 SSH 密钥未配置或未添加到 GitHub。

## 解决方案

### 方案 1: 使用 HTTPS（最简单，推荐）

如果只是想快速推送代码，使用 HTTPS 是最简单的方案：

```bash
# 更改远程仓库 URL 为 HTTPS
git remote set-url origin https://github.com/LeoAKALiu/pv_pile.git

# 然后推送（会提示输入用户名和密码/Personal Access Token）
git push -u origin main
```

**注意**: GitHub 已不再支持密码认证，需要使用 Personal Access Token (PAT)。

#### 获取 Personal Access Token

1. 登录 GitHub
2. 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 "Generate new token (classic)"
4. 选择权限（至少需要 `repo` 权限）
5. 复制生成的 token（只显示一次）

推送时：
- 用户名：你的 GitHub 用户名
- 密码：使用 Personal Access Token

### 方案 2: 配置 SSH 密钥（推荐用于长期使用）

#### 步骤 1: 检查是否已有 SSH 密钥

```bash
ls -la ~/.ssh/id_*.pub
```

如果有输出，说明已有密钥，跳到步骤 3。

#### 步骤 2: 生成新的 SSH 密钥

```bash
# 生成 SSH 密钥（替换为你的 GitHub 邮箱）
ssh-keygen -t ed25519 -C "leobobsix@outlook.com"

# 如果系统不支持 ed25519，使用 RSA
ssh-keygen -t rsa -b 4096 -C "leobobsix@outlook.com"

# 按提示操作（可以直接回车使用默认路径和空密码）
```

#### 步骤 3: 启动 SSH agent 并添加密钥

```bash
# 启动 SSH agent
eval "$(ssh-agent -s)"

# 添加 SSH 密钥
ssh-add ~/.ssh/id_ed25519
# 或
ssh-add ~/.ssh/id_rsa
```

#### 步骤 4: 复制公钥到剪贴板

```bash
# 显示公钥内容
cat ~/.ssh/id_ed25519.pub
# 或
cat ~/.ssh/id_rsa.pub

# 复制输出的内容（从 ssh-ed25519 或 ssh-rsa 开始到邮箱结束）
```

#### 步骤 5: 将公钥添加到 GitHub

1. 登录 GitHub
2. 进入 Settings → SSH and GPG keys
3. 点击 "New SSH key"
4. Title: 填写一个描述（如 "AutoDL Server"）
5. Key: 粘贴刚才复制的公钥内容
6. 点击 "Add SSH key"

#### 步骤 6: 测试 SSH 连接

```bash
ssh -T git@github.com
```

如果看到类似以下输出，说明配置成功：
```
Hi LeoAKALiu! You've successfully authenticated, but GitHub does not provide shell access.
```

#### 步骤 7: 使用 SSH URL

```bash
# 确保远程仓库使用 SSH URL
git remote set-url origin git@github.com:LeoAKALiu/pv_pile.git

# 验证
git remote -v

# 推送
git push -u origin main
```

## 快速命令总结

### 使用 HTTPS（最简单）

```bash
git remote set-url origin https://github.com/LeoAKALiu/pv_pile.git
git push -u origin main
# 输入用户名和 Personal Access Token
```

### 配置 SSH（一次性设置）

```bash
# 1. 生成密钥
ssh-keygen -t ed25519 -C "leobobsix@outlook.com"

# 2. 启动 agent 并添加密钥
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. 显示公钥（复制到 GitHub）
cat ~/.ssh/id_ed25519.pub

# 4. 测试连接
ssh -T git@github.com

# 5. 使用 SSH URL
git remote set-url origin git@github.com:LeoAKALiu/pv_pile.git
git push -u origin main
```

## 故障排除

### 问题 1: SSH agent 未运行

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### 问题 2: 多个 SSH 密钥

如果有多個密钥，创建 `~/.ssh/config` 文件：

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
```

### 问题 3: 权限问题

确保密钥文件权限正确：

```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

---

*最后更新: 2025-01-27*


