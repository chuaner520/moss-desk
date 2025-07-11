# desk-moss

企业级 Python 桌面应用结构

## 技术栈
- PySide6：桌面 UI 框架
- aiohttp：异步网络请求
- qdarkstyle：美观的蓝色主题

## 目录结构

```
app/
  main.py
  router.py
  network/
    client.py
  views/
    home.py
    about.py
  models/
    user.py
  utils/
    logger.py
dev_run.py
requirements.txt
README.md
```

## 运行方式

```bash
pip install -r requirements.txt
python -m app.main
```

## 开发环境热更新（自动重启）

开发时可用 `dev_run.py` 实现代码变动自动重启，无需手动重启应用：

```bash
pip install watchdog
python dev_run.py
```
- 仅开发环境使用，生产/打包无需此脚本。
- 监控 `app/` 目录下所有 `.py` 文件，保存后自动重启主程序。

## 打包为 macOS 和 Windows 应用

### 1. 安装 PyInstaller
```bash
pip install pyinstaller
```

### 2. macOS 打包命令
```bash
pyinstaller -F -w -n DeskMoss --icon=favicon.icns app/main.py
```
- 生成的可执行文件在 `dist/DeskMoss`

### 3. Windows 打包命令
```bash
pyinstaller -F -w -n DeskMoss --icon=favicon.ico app/main.py
```
- 生成的可执行文件在 `dist/DeskMoss.exe`

### 4. 带图标打包（可选）
```bash
pyinstaller -F -w -n DeskMoss --icon=youricon.ico app/main.py  # Windows
pyinstaller -F -w -n DeskMoss --icon=youricon.icns app/main.py # macOS
```
- macOS 图标用 `.icns`，Windows 用 `.ico`

### 5. 注意事项
- 建议在对应系统下打包（macOS 打包 macOS，Windows 打包 Windows）
- 如有静态资源，需用 `--add-data` 参数
- 打包后请在无 Python 环境的机器上测试

---

## ⚡️ 关于启动速度与 SplashScreen

- **PyInstaller 单文件模式（`-F`）会在启动时先解包所有依赖，导致首次启动有明显空窗期。**
- **SplashScreen 只能在 Python 代码开始执行后显示，无法覆盖 PyInstaller 解包期间的等待。**
- 如果追求“点击即现”的体验，建议用多文件模式打包：
  ```bash
  pyinstaller -w -n DeskMoss app/main.py
  ```
  这样会在 `dist/DeskMoss/` 目录下生成可执行文件和所有依赖，启动速度明显提升，SplashScreen 也能及时显示。
- 单文件模式适合便携分发，多文件模式适合追求极致启动体验。 