# EZ Runner 贡献指南

> **"I'm a huge proponent of designing your code around the data, rather than the other way around."**
> — Linus Torvalds

感谢你对 EZ Runner 的贡献！本文档说明如何参与项目开发。

---

## 开始之前

### 阅读文档

请先阅读以下文档：

1. [DEVELOPMENT.md](DEVELOPMENT.md) - 开发环境搭建
2. [CODE_STYLE.md](CODE_STYLE.md) - 代码规范
3. [TESTING.md](TESTING.md) - 测试策略
4. [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计

### 行为准则

- **技术优先**：批评针对代码，不针对人
- **实用主义**：解决真实问题，不是假想的威胁
- **简洁至上**：优先考虑最简单的解决方案
- **向后兼容**：不破坏现有功能

---

## 贡献方式

### 1. 报告 Bug

**发现 Bug 时，请提供：**

- **复现步骤**（越详细越好）
- **预期行为** vs **实际行为**
- **环境信息**：
  - Python 版本
  - Docker 版本
  - 操作系统
  - 完整的错误日志

**示例：**

```markdown
### Bug 描述
打包 qwen/Qwen-7B 时构建失败

### 复现步骤
1. 运行 `ezrunner pack qwen/Qwen-7B`
2. 等待 5 分钟
3. 报错：`docker.errors.BuildError: ...`

### 预期行为
成功生成 Docker 镜像

### 实际行为
构建失败，错误信息：
\`\`\`
ERROR: failed to solve: process "/bin/sh -c pip install torch" did not complete successfully: exit code: 137
\`\`\`

### 环境
- Python: 3.11.5
- Docker: 24.0.6
- OS: Ubuntu 22.04
- RAM: 8GB
```

### 2. 提出新功能

**在提交 PR 之前，先开 Issue 讨论：**

- **问题陈述**：这个功能解决什么真实问题？
- **解决方案**：你的设计思路
- **替代方案**：为什么不选其他方案？
- **兼容性**：会破坏现有功能吗？

**反例：不要这样提需求**
```
"我觉得应该支持 GGUF 格式"
"能不能加个 Web UI？"
"Ollama 有 XXX 功能，我们也应该有"
```

**正例：好的需求描述**
```markdown
### 问题
目前只支持 safetensors 格式，但部分社区模型只提供 GGUF 格式（如 Llama.cpp 量化模型）。
这导致用户无法打包这些模型。

### 提议方案
在 ModelDiscovery 中检测 GGUF 格式，使用 llama.cpp 作为推理引擎。

### 替代方案
1. 要求用户手动转换 GGUF → safetensors（增加用户负担）
2. 不支持 GGUF（限制模型覆盖）

### 兼容性
- 不影响现有 safetensors 流程
- 新增 `Engine.LLAMA_CPP`
- Dockerfile 模板需要新增 llama.cpp 版本
```

### 3. 改进文档

文档同样重要！贡献方式：

- 修正拼写/语法错误
- 补充缺失的示例
- 更新过时的信息
- 翻译成其他语言

---

## 贡献流程

### Step 1: Fork 仓库

```bash
# 1. Fork 到你的账号
#    点击 GitHub 页面右上角的 "Fork"

# 2. Clone 你的 fork
git clone https://github.com/YOUR_USERNAME/ezrunner.git
cd ezrunner

# 3. 添加上游仓库
git remote add upstream https://github.com/original/ezrunner.git
```

### Step 2: 创建分支

```bash
# 从 main 创建功能分支
git checkout -b feature/model-discovery

# 分支命名规范:
# feature/xxx  - 新功能
# fix/xxx      - Bug 修复
# refactor/xxx - 重构
# docs/xxx     - 文档
```

### Step 3: 开发

```bash
# 1. 搭建开发环境
pip install -e ".[dev]"

# 2. 编写代码
vim src/ezrunner/core/discovery.py

# 3. 编写测试
vim tests/unit/test_discovery.py

# 4. 运行测试
pytest tests/unit/test_discovery.py -v

# 5. 检查代码质量
black src/ tests/
ruff check --fix src/ tests/
mypy src/
```

### Step 4: 提交代码

```bash
# 1. 查看改动
git status
git diff

# 2. 添加改动
git add src/ezrunner/core/discovery.py
git add tests/unit/test_discovery.py

# 3. 提交（遵循 Conventional Commits）
git commit -m "feat: implement ModelDiscovery with ModelScope API"

# Commit 格式:
# feat:     新功能
# fix:      Bug 修复
# refactor: 重构（不改变功能）
# docs:     文档
# test:     测试
# chore:    构建/工具
#
# 示例:
# feat: add GGUF format support
# fix: handle timeout in Docker build
# refactor: simplify engine selection logic
# docs: update README with new examples
```

### Step 5: 同步上游

```bash
# 1. 获取上游更新
git fetch upstream

# 2. 合并到本地 main
git checkout main
git merge upstream/main

# 3. Rebase 你的分支
git checkout feature/model-discovery
git rebase main

# 4. 解决冲突（如果有）
# ... 手动解决冲突 ...
git add .
git rebase --continue
```

### Step 6: 推送到 Fork

```bash
git push origin feature/model-discovery

# 如果 rebase 过，需要强制推送
git push -f origin feature/model-discovery
```

### Step 7: 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "Compare & pull request"
3. 填写 PR 描述（模板如下）

**PR 描述模板：**

```markdown
## 改动说明

简要描述这个 PR 做了什么。

## 相关 Issue

Closes #123

## 改动类型

- [ ] Bug 修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 测试

## 测试

描述你如何测试这些改动：

\`\`\`bash
pytest tests/unit/test_discovery.py -v
\`\`\`

## 检查清单

- [ ] 代码遵循项目规范 (black, ruff, mypy)
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 没有破坏现有功能
```

---

## 代码审查

### 审查标准

你的 PR 会根据以下标准审查：

#### 1. 代码质量

- [ ] **简洁性**：没有超过 3 层缩进
- [ ] **函数长度**：单个函数 ≤ 40 行
- [ ] **命名清晰**：变量/函数名自解释
- [ ] **类型注解**：公共 API 有完整类型

#### 2. 架构设计

- [ ] **数据结构**：设计是否合理？
- [ ] **消除特殊情况**：避免过多的 if/else
- [ ] **单一职责**：每个函数只做一件事
- [ ] **避免过度设计**：最简单的方案

#### 3. 测试

- [ ] **测试覆盖**：核心逻辑有单元测试
- [ ] **测试质量**：测试真实场景，不是实现细节
- [ ] **测试通过**：所有测试（包括现有测试）都通过

#### 4. 兼容性

- [ ] **向后兼容**：不破坏现有 API
- [ ] **无破坏性变更**：除非有充分理由

### 审查流程

1. **自动检查**：CI 运行测试、Linter、类型检查
2. **人工审查**：Maintainer 审查代码设计和质量
3. **讨论**：通过评论讨论改进点
4. **修改**：根据反馈修改代码
5. **批准**：审查通过后合并

### 如何响应审查意见

```markdown
# ✅ 好的回复
> 建议：这个函数有 5 层缩进，太复杂了

已重构，拆分成 3 个子函数。
Commit: abc1234

# ❌ 差的回复
> 建议：这个函数有 5 层缩进，太复杂了

我觉得还好啊，这样更清楚。
```

**记住：审查是为了提高代码质量，不是针对个人。**

---

## Git 工作流

### 分支策略

```
main (保护分支)
  ↓
feature/xxx  (功能分支)
fix/xxx      (修复分支)
```

- **main**: 稳定分支，只接受 PR 合并
- **feature/xxx**: 从 main 拉出，开发完成后合并回 main
- **不使用 develop 分支**：保持简单

### Commit 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>: <subject>

<body> (可选)

<footer> (可选)
```

**Type:**
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构（不改变功能）
- `docs`: 文档
- `test`: 测试
- `chore`: 构建/工具

**示例：**

```bash
# 简单的 commit
git commit -m "feat: add GGUF format support"

# 带详细描述的 commit
git commit -m "fix: handle timeout in Docker build

Docker build sometimes hangs when downloading large models.
Added a 1-hour timeout to prevent infinite waiting.

Closes #123"
```

### Rebase vs Merge

**使用 Rebase 保持历史清晰：**

```bash
# ✅ Rebase 保持线性历史
git checkout feature/xxx
git rebase main
git push -f origin feature/xxx

# ❌ 不要 Merge（产生多余的合并 commit）
git merge main
```

---

## 发布流程

（仅 Maintainer）

### 版本号规范

遵循 [Semantic Versioning](https://semver.org/)：

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1  (Bug 修复)
1.0.1 → 1.1.0  (新功能，向后兼容)
1.1.0 → 2.0.0  (破坏性变更)
```

### 发布步骤

```bash
# 1. 更新版本号
vim pyproject.toml  # version = "1.1.0"

# 2. 更新 CHANGELOG
vim CHANGELOG.md

# 3. 提交
git add .
git commit -m "chore: release v1.1.0"

# 4. 打标签
git tag -a v1.1.0 -m "Release v1.1.0"

# 5. 推送
git push origin main --tags

# 6. 发布到 PyPI
python -m build
twine upload dist/*
```

---

## 常见问题

### Q1: 我的 PR 被拒绝了，怎么办？

**可能原因：**
- 不符合代码规范
- 测试不充分
- 设计有问题
- 功能不必要

**下一步：**
- 阅读审查意见
- 讨论并理解问题
- 修改后重新提交

### Q2: 我的分支落后 main 很多，怎么办？

```bash
git fetch upstream
git rebase upstream/main
# 解决冲突
git push -f origin feature/xxx
```

### Q3: 我不小心改了不相关的文件？

```bash
# 撤销单个文件的改动
git checkout -- path/to/file

# 或者使用 restore
git restore path/to/file
```

### Q4: 我想修改上一个 commit？

```bash
# 修改代码
vim file.py

# 追加到上一个 commit
git add file.py
git commit --amend

# 强制推送
git push -f origin feature/xxx
```

---

## 联系方式

- **Issue Tracker**: https://github.com/yourusername/ezrunner/issues
- **Discussions**: https://github.com/yourusername/ezrunner/discussions

---

**"Don't hurry your code. Make sure it works well and is well designed."**
— Linus Torvalds

感谢你的贡献！每一个 PR 都让 EZ Runner 变得更好。
