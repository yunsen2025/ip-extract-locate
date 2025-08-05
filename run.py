import re
import requests
import pandas as pd
import time

# 输入和输出文件路径
input_file = r"C:\\Users\\Yunsen\\Desktop\\py\\2025060210-imgbed.yunsen2025.top"
output_file_excel = r"C:\\Users\\Yunsen\\Desktop\\py\\ips_with_location.xlsx"
output_file_csv = r"C:\\Users\\Yunsen\\Desktop\\py\\ips_with_location.csv"

# 正则表达式提取 IP
ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

# 批量查询 API
BULK_API_URL = "http://ip-api.com/batch"

# 批量查询函数
def batch_query_ips(ips):
    try:
        # 请求 API，并加入中文语言参数
        response = requests.post(BULK_API_URL, json=ips, params={"lang": "zh-CN"})
        
        if response.status_code == 200:
            data = response.json()
            results = {}
            for entry in data:
                ip = entry.get("query", "未知")
                status = entry.get("status", "fail")
                if status == "success":
                    country = entry.get("country", "未知")
                    region = entry.get("regionName", "未知")
                    city = entry.get("city", "未知")
                    isp = entry.get("isp", "未知")  # 运营商
                    mobile = entry.get("mobile", False)  # 是否为移动网络
                    proxy = entry.get("proxy", False)  # 是否为代理
                    hosting = entry.get("hosting", False)  # 是否为托管服务
                    usage_type = []
                    if mobile:
                        usage_type.append("移动网络")
                    if proxy:
                        usage_type.append("代理")
                    if hosting:
                        usage_type.append("托管服务")
                    usage_type = "，".join(usage_type) if usage_type else "普通网络"
                    
                    # 只保存属地的地址部分
                    location = f"{country} {region} {city}"
                    results[ip] = {
                        "属地": location,
                        "运营商": isp,
                        "使用类型": usage_type,
                    }
                else:
                    results[ip] = {
                        "属地": "查询失败",
                        "运营商": "未知",
                        "使用类型": "未知",
                    }
            return results
        elif response.status_code == 429:
            print("请求过多，等待 2 秒后重试...")
            time.sleep(2)  # 等待2秒后重试
            return batch_query_ips(ips)  # 递归调用，重新发起请求
        elif response.status_code == 502:
            print("服务器不可用，稍后重试...")
            time.sleep(5)  # 等待5秒后重试
            return batch_query_ips(ips)  # 递归调用，重新发起请求
        else:
            print(f"批量查询请求失败：HTTP {response.status_code}")
            return {}
    except Exception as e:
        print(f"批量查询发生错误：{e}")
        return {}

# 处理日志文件
def process_logs_to_files(input_file, output_file_excel, output_file_csv):
    try:
        with open(input_file, 'r') as infile:
            unique_ips = set()
            for line in infile:
                ips = ip_pattern.findall(line)
                unique_ips.update(ips)

        unique_ips = list(unique_ips)
        print(f"找到 {len(unique_ips)} 个唯一 IP 地址，开始查询属地信息...")

        # 分批查询 IP 地址
        batch_size = 100
        ip_locations = {}
        failed_ips = []  # 用来记录查询失败的 IP 地址
        for i in range(0, len(unique_ips), batch_size):
            batch = unique_ips[i:i+batch_size]
            print(f"查询第 {i//batch_size + 1} 批...")
            try:
                results = batch_query_ips(batch)
                ip_locations.update(results)
            except Exception as e:
                failed_ips.extend(batch)  # 记录失败的 IP 地址
                print(f"查询第 {i//batch_size + 1} 批时发生错误: {e}")

        # 将查询结果转换为 DataFrame
        data = [{"IP地址": ip, "属地": ip_locations.get(ip, "查询失败")["属地"],
                 "运营商": ip_locations.get(ip, {}).get("运营商", "未知"),
                 "使用类型": ip_locations.get(ip, {}).get("使用类型", "未知")} for ip in unique_ips]
        df = pd.DataFrame(data)

        # 保存为 Excel 文件
        df.to_excel(output_file_excel, index=False)
        print(f"查询完成，结果已保存到 {output_file_excel}。")

        # 保存为 CSV 文件
        df.to_csv(output_file_csv, index=False)
        print(f"查询完成，结果已保存到 {output_file_csv}。")

        # 记录失败的 IP 地址
        if failed_ips:
            with open("failed_ips.txt", "w") as f:
                for ip in failed_ips:
                    f.write(ip + "\n")
            print("部分 IP 地址查询失败，已记录到 'failed_ips.txt'")

    except FileNotFoundError:
        print(f"文件 {input_file} 未找到，请检查路径！")
    except Exception as e:
        print(f"处理文件时出错：{e}")

# 主函数
if __name__ == "__main__":
    process_logs_to_files(input_file, output_file_excel, output_file_csv)
