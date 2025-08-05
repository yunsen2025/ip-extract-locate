## 提取日志/代理池中的 IP，并使用 [ip-api.com](https://ip-api.com/) 批量查询 IP 属地

### 安装依赖

```bash
pip3 install pandas
```

### 路径设置

需更改 `run.py` 中的以下路径为你的绝对路径：

```python
input_file = r"C:\\Users\\Yunsen\\Desktop\\py\\ip.txt"
output_file_excel = r"C:\\Users\\Yunsen\\Desktop\\py\\ips_with_location.xlsx"
output_file_csv = r"C:\\Users\\Yunsen\\Desktop\\py\\ips_with_location.csv"
```

### 特点

- 支持在日志中批量提取
- 支持更换查询 API