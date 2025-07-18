# swarmToolbox

**蜂群（Neurosama 粉丝群体）信息中心软件**

`swarmToolbox` 是一个专为 Neurosama 粉丝（蜂群）设计的桌面应用程序，旨在提供一个集成的中心，方便您获取最新资讯、追踪直播动态以及启动社区相关工具。本软件采用 WinUI 3 风格界面，力求简洁、现代且易于使用。

## ✨ 主要功能

* **一键启动中心**:
  * 快速启动社区项目 `neuroSangSpider`。
  * 支持启动 `Evil vs Zombies` 游戏。

* **直播动态追踪**:
  * 自动获取并展示 Neurosama 的最新直播时间表。
  * 在直播开始时发送桌面通知，确保您不会错过任何精彩瞬间。

* **内容聚合**:
  * 自动爬取并展示 Bilibili 平台最新的 Neurosama 相关切片视频。

* **资讯中心**:
  * 汇聚来自 `neuroSangSpider` 项目的最新资讯与更新。
  * 获取 `Evil vs Zombies` 游戏社区的最新动态。

## 🔧 开发环境配置

* **操作系统**: Windows 10 或更高版本
* **Python**: `3.13` 或更高版本
* **包管理器**: 本项目使用 [**`uv`**](https://github.com/astral-sh/uv) 进行高性能的包管理。
* **IDE 配置**: 项目内已包含 **PyCharm** 和 **VSCode** 的推荐配置文件，帮助您快速搭建开发环境。

## 🚀 开发与构建

如果您希望为本项目贡献代码或自行构建，请遵循以下步骤。

1.  **克隆本仓库**
    ```bash
    git clone https://github.com/qingchenyouforcc/swarmToolbox.git
    cd swarmToolbox
    ```

2.  **安装 `uv`** (如果尚未安装)
    ```bash
    # Windows (PowerShell)
    irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex
    ```
更多安装方式请参考 [uv 官方文档](https://github.com/astral-sh/uv#installation)。

3.  **创建虚拟环境并安装依赖**
    使用 `uv` 可以一键完成虚拟环境创建和依赖安装：
    ```bash
    # 这条命令会自动创建 .venv 虚拟环境并安装所有依赖
    uv sync
    ```

4.  **在开发模式下运行**
    激活虚拟环境后，您可以直接运行主程序进行测试和开发：
    ```bash
    # 激活虚拟环境 (Windows CMD)
    .\.venv\Scripts\activate

    # 运行程序
    python main.py
    ```

5.  **构建 `.exe` 发行版**
    本项目使用 `PyInstaller` 进行打包。
    ```bash
    # 首先，确保已在虚拟环境中安装 PyInstaller
    uv pip install pyinstaller

    # 然后，使用 spec 文件进行构建（推荐）
    pyinstaller your_project_name.spec
    ```
    构建成功后，可执行文件将位于生成的 `dist` 文件夹内。

## 🤝 如何贡献

我们欢迎所有形式的贡献！如果您有任何好的建议、功能需求或发现了 Bug，请随时提交 [Issues](https://github.com/qingchenyouforcc/swarmToolbox/issues)。

如果您希望贡献代码，请遵循以下步骤：

1.  Fork 本仓库
2.  创建您的特性分支
3.  提交您的更改
4.  将更改推送到分支
5.  创建一个 Pull Request到master分支

## 📄 开源协议

该项目采用 [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html) 开源协议。