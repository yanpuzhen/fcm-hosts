# Hosts IP 自动更新工具

这是一个简单的 Python 工具，用于读取 `hosts` 文件中的域名，自动解析其最新的 IP 地址，并生成新的 hosts 列表。项目包含 GitHub Actions 配置，支持每小时自动运行并更新结果。

## 功能特性

- **自动解析**: 从 `hosts` 文件中提取域名，并使用 Google DNS (8.8.8.8) 解析其 A 记录。
- **多路径支持**: 自动在常见位置查找源 `hosts` 文件（如当前目录、上级目录等）。
- **自动化流**: 包含 GitHub Actions 工作流，每小时定时执行，并将更新后的 `hosts.txt` 自动提交到仓库。

## 文件结构

- `fetch_ips.py`: 主程序脚本。
- `requirements.txt`: Python 依赖文件。
- `.github/workflows/schedule.yml`: GitHub Actions 自动化配合文件。
- `hosts.txt`: 脚本生成的包含最新 IP 的结果文件。

## 快速开始

### 本地运行

1.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

2.  **运行脚本**
    ```bash
    python fetch_ips.py
    ```
    脚本运行后会在当前目录下生成 `hosts.txt`。

### GitHub Actions 部署

1.  将本项目推送到 GitHub 仓库。
2.  如果不做任何修改，Actions 会默认每小时运行一次。
3.  你也可以在 "Actions" 标签页手动触发 "Update Hosts" 工作流。
4.  运行完成后，最新的 IP 列表会自动更新到仓库中的 `hosts.txt` 文件。

## 注意事项

- 脚本默认使用 `8.8.8.8` 作为 DNS 服务器。
- 如果本地网络环境存在 DNS 污染或使用了代理（如 fake-ip 模式），本地运行生成的 IP 可能会是虚假 IP（如 `198.18.x.x`）。建议依赖 GitHub Actions 的云端环境进行解析以获取真实的公网 IP。
