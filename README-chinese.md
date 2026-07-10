<div align="center">

# 随机学号生成器

一款专为教师设计的桌面应用，用于课堂随机抽选学生，公平高效。

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.11+-41CD52?logo=qt&logoColor=white)](https://www.qt.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/nanocode38/Random-Number-Generator/releases)

[功能](#功能) · [安装](#安装) · [使用方法](#使用方法) · [开发](#开发) · [贡献](#贡献)

</div>

---

> **English version** see [README.md](README.md)

## 项目简介

随机学号生成器是一个跨平台桌面应用，帮助老师在课堂上随机抽选学生。只需加载 CSV 格式的花名册，点击按钮即可随机抽取——支持去重模式，确保每个学生都有机会被抽到。

基于 **PySide6**（Qt for Python）构建，内置流畅的贴边隐藏动画、8 种主题和 5 种语言支持。

## 功能

- **CSV 花名册加载** — 从简单的 CSV 文件加载学生名单。支持单行（仅姓名）和双行（学号 + 姓名）两种格式。
- **智能去重** — 开启去重模式后确保每个学生被公平抽到。全部抽完后自动重置。
- **贴边隐藏模式** — 将窗口拖到屏幕边缘，它会以流畅动画自动缩小为浮动小图标。悬停或点击即可恢复——非常适合演示场景。
- **8 种主题** — Light、Dark、Ocean、Sunset、Forest、Cyber、Lavender、Nord，菜单中一键切换。
- **多语言支持** — English、中文(简体)、中文(繁體)、日本語、 한국어。在语言目录中放入 JSON 文件即可添加更多语言。
- **跨平台** — 得益于 Qt，可运行于 Windows、macOS 和 Linux。
- **设置持久化** — 主题、语言、班级和模式偏好自动保存。

## 安装

### 方式一：下载预构建版本（Windows）

1. 前往 [Releases 页面](https://github.com/nanocode38/Random-Number-Generator/releases)。
2. 下载最新的 Windows 安装包（`.zip`）。
3. 解压后运行 `StudentNumberGenerator.exe`。

### 方式二：从源码运行

**前置要求：** Python 3.10+

```bash
# 克隆仓库
git clone https://github.com/nanocode38/Random-Number-Generator.git
cd Random-Number-Generator

# （可选）创建虚拟环境
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 安装依赖
pip install PySide6

# 运行程序
python enter.py
# 或：python -m src
```

## 使用方法

### 1. 准备花名册

创建一个以班级名命名的 CSV 文件（如 `一年级.csv`），放入 `Classes/` 目录。

**格式 A — 仅姓名（单行）：**

```csv
张三, 李四, 王五, 赵六, 孙七
```

学号将自动编号为 1、2、3、...

**格式 B — 学号 + 姓名（两行）：**

```csv
1, 2, 3, 4, 5
张三, 李四, 王五, 赵六, 孙七
```

> 可参考 `Classes/example.csv` 查看示例。

### 2. 启动程序

运行程序后，在**班级**下拉框中选择你的花名册。

### 3. 随机抽取

点击**生成**按钮，随机抽取一名学生。学号和姓名将显示在界面上。

### 4. 去重模式

勾选**去重**复选框，确保每个学生不会被重复抽到，直到所有人都被抽过一遍。全部抽完后列表自动重置。

### 5. 贴边隐藏模式

勾选**贴边隐藏**复选框，启用窗口置顶和贴边隐藏：

- 窗口将始终置顶于其他窗口之上。
- 将窗口拖近屏幕左边缘或右边缘——短暂延迟后，它会以动画效果缩小为一个小浮动图标。
- 鼠标悬停或点击该图标即可恢复完整窗口。

非常适合演示时让抽号器就近待命但不遮挡内容。

### 6. 主题与语言

- **主题：** 菜单栏 → **主题** → 从 8 种可用主题中选择。
- **语言：** 菜单栏 → **语言** → 选择所需语言。应用将重启以应用更改。

## 项目结构

```
Random student number generator/
├── enter.py                 # 入口脚本
├── src/
│   ├── __init__.py          # 包元数据（版本、作者）
│   ├── __main__.py          # `python -m src` 入口
│   ├── app.py               # 主协调器（Main 类、main()）
│   ├── ui.py                # GUI 组件（MainWindow、FloatingWindow）
│   ├── picker.py            # 随机抽取逻辑（StudentPicker）
│   ├── edge_hider.py        # 贴边隐藏行为（EdgeHider）
│   ├── animation.py         # 窗口显示/隐藏动画（Animation）
│   ├── tools.py             # 工具函数（重启、设置读写、语言加载）
│   └── constant.py          # 路径定义和应用级常量
├── AppData/
│   ├── icon.ico / icon.png  # 应用图标
│   ├── data.json            # 持久化用户设置
│   ├── style/               # 主题 CSS 文件（Light、Dark、Ocean 等）
│   └── language/            # 语言 JSON 文件（English、中文、日本語 等）
├── Classes/                 # CSV 班级花名册
│   └── example.csv
├── Web/                     # 项目官网
├── test/                    # 测试套件（pytest）
├── pyproject.toml           # 项目配置与依赖
├── update.bat               # Nuitka 构建脚本（Windows）
└── update.py                # Web HTML 版本注入脚本
```

## 开发

### 环境配置

```bash
# 安装开发依赖
pip install -e ".[dev]"
# 或手动安装：
pip install PySide6 black isort autoflake pytest pytest-mock pytest-cov
```

### 运行测试

```bash
pytest
```

测试位于 `test/` 目录，覆盖抽取逻辑、工具函数和常量。

### 代码规范

项目使用 [Black](https://github.com/psf/black)（行宽 120）、[isort](https://pyc.github.io/isort/) 和 [autoflake](https://github.com/PyCQA/autoflake) 进行代码格式化：

```bash
black src/ test/
isort src/ test/
autoflake --in-place --remove-unused-imports --remove-unused-variables src/
```

### 从源码构建（Windows）

项目使用 [Nuitka](https://nuitka.net/) 打包：

```bash
# 先安装 Nuitka
pip install nuitka

# 运行构建脚本
update.bat
```

构建产物为 `dist/StudentNumberGenerator.exe` 及所有运行时依赖文件。

## 贡献

欢迎贡献！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

### 添加新语言

1. 复制 `AppData/language/English.json`，重命名为你的语言（如 `Français.json`）。
2. 翻译所有键值。
3. 从应用内的**语言**菜单中选择新语言即可。

### 添加新主题

1. 在 `AppData/style/` 中创建新的 CSS 文件（如 `MyTheme.css`）。
2. 使用 Qt Style Sheets 编写样式，可参考 `Light.css` 或 `Dark.css` 等现有主题。
3. （可选）添加主题预览图 `check_mytheme.png`。
4. 新主题将自动出现在应用内的**主题**菜单中。

## 开源协议

本项目基于 **MIT 协议**开源——详见 [LICENSE](LICENSE)。

## 作者

**nanocode38**

- GitHub: [@nanocode38](https://github.com/nanocode38)
- 邮箱: nanocode38@88.com
- 项目地址: [Random-Number-Generator](https://github.com/nanocode38/Random-Number-Generator)

---

<div align="center">

基于 PySide6 构建 ❤️

</div>
