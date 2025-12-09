# 🔧 GitHub SSH配置指南

## ❌ 当前问题
```
git@github.com: Permission denied (publickey).
```

这表示你的SSH密钥没有配置或没有添加到GitHub。

## ✅ 解决方案

### 方法1：使用HTTPS（推荐，最简单）

#### 步骤1：更改远程仓库URL为HTTPS
```bash
# 删除现有的SSH远程仓库
git remote remove origin

# 添加HTTPS远程仓库
git remote add origin https://github.com/manongguai/bilibili_crawler.git

# 推送代码
git push -u origin main
```

#### 步骤2：如果需要认证
推送时会提示输入GitHub用户名和密码（或Personal Access Token）。

### 方法2：配置SSH密钥（推荐长期使用）

#### 步骤1：生成SSH密钥
```bash
# 检查是否已有SSH密钥
ls -la ~/.ssh/id_rsa.pub

# 如果没有，生成新的SSH密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# 按回车使用默认路径，可以设置密码或留空
```

#### 步骤2：复制SSH公钥
```bash
# 显示公钥内容
cat ~/.ssh/id_rsa.pub
```

#### 步骤3：添加到GitHub
1. 访问 https://github.com/settings/keys
2. 点击 "New SSH key"
3. 粘贴公钥内容
4. 保存

#### 步骤4：测试SSH连接
```bash
ssh -T git@github.com
```

#### 步骤5：推送代码
```bash
git push -u origin main
```

### 方法3：使用GitHub CLI（最新方式）

#### 步骤1：安装GitHub CLI
```bash
# macOS
brew install gh

# 或下载：https://cli.github.com/
```

#### 步骤2：登录GitHub
```bash
gh auth login
```

#### 步骤3：创建仓库并推送
```bash
# 如果仓库已存在
gh repo set-default manongguai/bilibili_crawler

# 推送代码
git push -u origin main
```

## 🚀 快速推荐

如果你只是想快速推送代码，使用方法1（HTTPS）：
```bash
git remote remove origin
git remote add origin https://github.com/manongguai/bilibili_crawler.git
git push -u origin main
```

## 💡 注意事项

1. **HTTPS**：每次推送需要认证，但最简单
2. **SSH**：一次性配置，长期使用更方便
3. **GitHub CLI**：官方工具，功能强大
4. **Personal Access Token**：如果使用HTTPS，建议使用token而非密码

## 🔍 验证配置成功

推送成功后会显示类似信息：
```
Enumerating objects: 21, done.
Counting objects: 100% (21/21), done.
Delta compression using up to 8 threads
Compressing objects: 100% (21/21), done.
Writing objects: 100% (21/21), 23.6 KiB | 5.4 MiB/s, done.
Total 21 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/manongguai/bilibili_crawler.git
 * [new branch]      main -> main
```