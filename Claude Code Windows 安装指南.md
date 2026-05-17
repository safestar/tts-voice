# Claude Code Windows 安装指南

## 快速开始

> 10 分钟完成安装，让 Claude 在您的 Windows 上运行代码。

---

## 前置检查

| 项目 | 要求 | 检查方法 |
|-----|------|---------|
| 系统 | Windows 10/11 **64位** | `Win + Pause` 查看"系统类型" |
| 权限 | 管理员权限 | 安装时需要 |
| 网络 | 可访问 claude.ai | 浏览器测试 |

---

## 安装步骤

### 1. 安装 Git

**必须先安装 Git，Claude Code 依赖 Git Bash。**

下载地址：https://git-scm.com/downloads/win

安装要点：
- 选择 **64-bit** 版本
- PATH 选项保持默认（"Git from command line..."）
- 其他选项全部默认即可

验证：
```cmd
git --version
```

---

### 2. 安装 Claude Code

以管理员身份打开 PowerShell（搜索 PowerShell → 右键 → 以管理员运行），执行：

```powershell
irm https://claude.ai/install.ps1 | iex
```

等待完成，输出显示安装路径：
```
C:\Users\<用户名>\.local\bin\claude.exe
```

---

### 3. 添加 PATH

**方法一（推荐）：图形界面**

1. `Win + R` → 输入 `sysdm.cpl` → 回车
2. 高级 → 环境变量
3. 用户变量中双击 `Path`
4. 新建 → 输入：
   ```
   C:\Users\<你的用户名>\.local\bin
   ```
5. 确定 → 确定 → 确定

**方法二：命令行**

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\$env:USERNAME\.local\bin", "User")
```

---

### 4. 验证安装

**关闭所有 PowerShell 窗口，重新打开一个。**

```powershell
claude --version
```

成功输出示例：`2.0.34`

---

### 5. 配置认证

**方式 A：Claude Pro/Max 用户（推荐）**

直接运行 `claude`，按提示完成账号登录。

**方式 B：API 用户**

1. 访问 https://console.anthropic.com/settings/keys
2. 创建 API Key
3. 执行：
   ```powershell
   claude config set apiKey
   ```
4. 输入您的 Key

**方式 C：国内 Coding Plan（免国际网络）**

国内各大厂商推出的 AI Coding Plan，兼容 Claude Code：

| 平台 | 套餐类型 | 支持模型 | 适配工具 | 适合人群 |
|-----|---------|---------|---------|---------|
| 方舟（字节） | Lite/Pro，包月/季 | Doubao、GLM、DeepSeek、Kimi、MiniMax | Claude Code、Cursor | 多模型尝试、综合型用户 |
| GLM Coding（智谱） | Lite/Pro/Max，包月/季/年 | GLM 系列 | Claude Code | 智谱生态用户 |
| 百度千帆 | Lite/Pro | GLM-5、MiniMax-M2.5、Kimi-K2.5 | Claude Code | 百度云用户 |
| 腾讯云 | Lite/Pro | Hunyuan、GLM-5、Kimi、MiniMax | Claude Code | 腾讯云生态用户 |
| 阿里云百炼 | Pro 等 | Qwen、GLM、Kimi、MiniMax | Claude Code、Cline、Qoder | 阿里云/通义用户 |
| MiniMax | Starter/Plus/Max/Ultra | MiniMax M2.7 | OpenClaw、MCP | 关注速度额度用户 |
| Kimi（月之暗面） | 四档套餐 | Kimi Code 旗舰模型 | Kimi Code | Kimi 重度用户 |
| 摩尔线程 | Free/Lite/Pro/Max | 国产模型+GLM | Claude Code、Cursor、Cline | 国产模型体验用户 |
| DeepSeek V4 | API 按量计费 | DeepSeek-V4-Flash/Pro | 需自行接入 | 有开发能力用户 |
| Xiaomi MIMO | Lite/Standard/Pro/Max | MiMo-V2.5 多模态 | Claude Code、OpenCode | 多模态需求用户 |

**配置示例（方舟）：**

```powershell
# 设置 API 端点
claude config set apiBaseUrl https://ark.cn-beijing.volces.com/api/v3

# 设置 API Key
claude config set apiKey
```

> 💡 各平台配置参数不同，购买后查看官方文档获取具体的 `apiBaseUrl` 和 `apiKey`。

---

## 常见问题

### `'claude' 不是内部或外部命令`

- 检查 PATH 是否正确添加
- **必须重启 PowerShell**（关闭后重新打开）
- 用完整路径测试：`C:\Users\<用户名>\.local\bin\claude.exe`

### `requires git-bash`

Git 未安装或未正确配置 PATH。重新安装 Git for Windows。

### `does not support 32-bit`

- 确认系统为 64 位
- 使用 64 位 PowerShell（路径含 `System32`，不是 `SysWOW64`）

### 脚本执行被禁止

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 命令速查

```powershell
claude                  # 启动交互模式
claude --version        # 查看版本
claude --help           # 查看帮助
claude config list      # 查看配置
claude --model opus     # 指定模型
```

---

## 安装验证清单

- [ ] Git 已安装（`git --version` 正常）
- [ ] Claude Code 已安装（`claude --version` 正常）
- [ ] 认证已完成（能正常对话）
- [ ] 测试功能（`claude "创建一个 hello.py 文件"`）

---

## 下一步

安装成功后，进入项目目录运行 `claude`，开始让 AI 协助您编码。

推荐阅读：
- [官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [使用技巧](https://github.com/anthropics/claude-code#usage)

---

**更新日期**：2026-05-17