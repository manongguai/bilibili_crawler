#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站爬虫诊断工具
帮助诊断爬取失败的原因

作者：Kirk
日期：2025-12-08
"""

import json
import requests
import sys
import time
from datetime import datetime


def test_network_connectivity():
    """测试网络连接性"""
    print("🔍 测试1：网络连接性")
    print("-" * 40)

    test_urls = [
        "https://www.bilibili.com",
        "https://api.bilibili.com/x/web-interface/nav",
        "https://httpbin.org/ip"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for url in test_urls:
        try:
            print(f"🌐 测试: {url}")
            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                verify=False
            )
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   📏 响应大小: {len(response.content)} bytes")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        print()


def test_bilibili_api(uid: int):
    """测试B站API"""
    print("🔍 测试2：B站API访问")
    print("-" * 40)

    # 测试用户信息API
    print("📊 测试用户信息API...")
    url = f"https://api.bilibili.com/x/space/acc/info"
    params = {'mid': uid}

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10,
            verify=False
        )
        data = response.json()
        print(f"   状态码: {response.status_code}")
        print(f"   API响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    print()

    # 测试视频列表API
    print("📼 测试视频列表API...")
    url = "https://api.bilibili.com/x/space/arc/search"
    params = {
        'mid': uid,
        'ps': 1,
        'pn': 1
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10,
            verify=False
        )
        data = response.json()
        print(f"   状态码: {response.status_code}")
        print(f"   API响应: {json.dumps(data, ensure_ascii=False, indent=2)}")

        if data.get('code') == 0:
            videos = data.get('data', {}).get('list', {}).get('vlist', [])
            print(f"   ✅ 找到 {len(videos)} 个视频")
            if videos:
                print(f"   📺 第一个视频: {videos[0].get('title', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    print()


def test_different_uids():
    """测试不同UID"""
    print("🔍 测试3：不同UID访问")
    print("-" * 40)

    test_uids = [
        435776729,  # 何同学（知名UP主）
        269066291,  # 罗翔说刑法
        29002508,   # 老番茄
        123456789   # 不存在的UID
    ]

    for uid in test_uids:
        print(f"👤 测试UID: {uid}")
        url = "https://api.bilibili.com/x/space/arc/search"
        params = {
            'mid': uid,
            'ps': 1,
            'pn': 1
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=5,
                verify=False
            )
            data = response.json()
            print(f"   状态码: {response.status_code}")
            print(f"   响应码: {data.get('code', 'N/A')}")
            print(f"   消息: {data.get('message', 'N/A')}")

            if data.get('code') == 0:
                videos = data.get('data', {}).get('list', {}).get('vlist', [])
                print(f"   ✅ 成功: {len(videos)} 个视频")
            else:
                print(f"   ❌ 失败")
        except Exception as e:
            print(f"   ❌ 异常: {e}")
        print()


def check_environment():
    """检查环境配置"""
    print("🔍 测试4：环境配置")
    print("-" * 40)

    # Python版本
    print(f"🐍 Python版本: {sys.version}")

    # requests版本
    try:
        import requests
        print(f"📦 requests版本: {requests.__version__}")
    except:
        print("❌ requests未安装")

    # 系统时间
    print(f"⏰ 系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查代理
    try:
        import urllib.request
        proxy_handler = urllib.request.getproxies()
        if proxy_handler:
            print(f"🌐 代理设置: {proxy_handler}")
        else:
            print("🌐 代理设置: 无")
    except:
        print("🌐 代理设置: 无法检测")

    print()


def quick_test():
    """快速测试"""
    print("⚡ 快速诊断")
    print("-" * 40)

    # 测试一个简单的请求
    try:
        print("🚀 发送测试请求...")
        start_time = time.time()
        response = requests.get(
            "https://api.bilibili.com/x/web-interface/online",
            timeout=5,
            verify=False
        )
        end_time = time.time()
        print(f"   ✅ 请求成功")
        print(f"   ⏱️  耗时: {end_time - start_time:.2f} 秒")
        print(f"   📊 响应: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")


def main():
    """主函数"""
    print("🔧 B站爬虫诊断工具")
    print("=" * 50)
    print()

    # 获取UID参数
    uid = None
    if len(sys.argv) > 1:
        try:
            uid = int(sys.argv[1])
            print(f"📍 目标UID: {uid}")
            print()
        except ValueError:
            print("❌ UID参数无效")
            return

    # 运行所有测试
    print("🔍 开始全面诊断...")
    print("=" * 50)
    print()

    check_environment()
    test_network_connectivity()

    if uid:
        test_bilibili_api(uid)
    else:
        print("💡 提示：使用 'python diagnose.py UID' 来测试特定用户")

    test_different_uids()
    quick_test()

    print("\n" + "=" * 50)
    print("🎯 诊断建议：")
    print("1. 如果网络测试失败 → 检查网络连接和代理设置")
    print("2. 如果B站API失败 → 可能是IP被限制，稍后重试")
    print("3. 如果所有测试都失败 → 尝试更换网络环境")
    print("4. 如果可以访问网站但API失败 → 可能需要更新User-Agent")


if __name__ == "__main__":
    main()