# 使用 Toggl 与日历集成脚本的分步指南

[English](README.md)

本指南为设置和使用脚本以与 Toggl 和日历数据交互提供了清晰、顺序的说明。

## 前置条件
- 确保你的**Mac电脑**已安装 **Python 3**。
- 拥有一个 **Toggl 账号**，并获取你的 API token 和工作区 ID。
- 拥有一个 **日历应用**（Apple Calendar），可在其中创建日历。

## 分步设置

### 1. 克隆仓库
将仓库下载或克隆到本地计算机, 进入项目目录：
```bash
cd toggl-to-calendar
```

### 2. 安装依赖
检查项目目录下是否有 `requirements.txt` 文件。如果有，安装所需的 Python 包：
```bash
pip install -r requirements.txt
```
如果没有 `requirements.txt`，请根据脚本注释或文档手动安装所需的包。

### 3. 配置文件设置
脚本需要一个包含 Toggl 凭据和项目映射的 `config.json` 文件。

#### a. 创建 `config.json`
如果项目目录下没有 `config.json`，请手动创建。

#### b. 添加配置信息
将以下模板复制到 `config.json` 并填写你的凭据：
```json
{
  "TOGGL_API_TOKEN": "YOUR_TOGGL_API_TOKEN_HERE",
  "TOGGL_WORKSPACE_ID": "YOUR_WORKSPACE_ID_HERE",
  "id_to_name": {
    "000000001": "Work",
    "000000002": "Personal",
    "000000003": "Growth",
    "000000004": "Relationships",
    "000000005": "Hobbies"
  }
}
```
- **TOGGL_API_TOKEN**：登录 Toggl，进入 **Profile > Profile Settings > API Token**，点击“Reveal”复制你的 token。
- **TOGGL_WORKSPACE_ID**：在 Toggl 中，进入你的项目。工作区 ID 是 URL 中的一串数字。
- **id_to_name**：将 Toggl 项目 ID 映射为名称（如“Work”、“Personal”）。如何查找项目 ID，请见第 4 步。

**安全提示**：请妥善保管 `config.json`，不要公开分享。

### 4. 获取 Toggl 项目 ID
为填充 `config.json` 的 `id_to_name` 部分，运行以下命令以获取你的 Toggl 项目 ID 和名称：
```bash
python get_projects.py
```
根据脚本显示的项目 ID 和名称，更新 `config.json` 中的 `id_to_name` 部分。

### 5. 在日历应用中创建日历
在运行 `test.py` 之前，请在你的日历应用（如 Google 日历、Outlook）中创建与 `config.json` 的 `id_to_name` 部分中项目名称**完全一致**的日历。例如，如果 `id_to_name` 包含 `"Work"` 和 `"Personal"`，请分别创建名为“Work”和“Personal”的日历。

### 6. 运行脚本
- 获取 Toggl 项目数据：
  ```bash
  python get_projects.py
  ```
- 运行测试或执行主要功能（如同步 Toggl 数据到日历）：
  ```bash
  python test.py
  ```

## 重要说明
- 确保你拥有 Toggl 和日历服务商的必要权限和有效 API token。
- 请确保你的日历名称与 `id_to_name` 条目完全一致，脚本依赖这些名称进行匹配。
- 有关更多细节或故障排查，请参考脚本（`get_projects.py`、`test.py`）中的注释。
- 如遇问题，请仔细检查 `config.json` 的准确性，并确保所有依赖已安装。

按照以上步骤操作，你应该能够顺利完成脚本的设置与使用。
