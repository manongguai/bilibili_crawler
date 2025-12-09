#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频爬虫 - 超快速版本
专门优化速度，减少等待时间

作者：Kirk
日期：2025-12-08
"""

import json
import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

# 禁用SSL警告
import warnings
warnings.filterwarnings('ignore')


class BilibiliFastCrawler:
    """B站视频爬虫类（超快速版本）"""

    def __init__(self):
        """初始化爬虫配置"""
        self.max_retries = 3  # 最少重试次数
        self.base_delay = 2  # 最短延迟
        self.videos_per_page = 50  # 每页更多视频
        self.output_dir = "./output"

        # 最简单的请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bilibili.com'
        }

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    def get_user_videos_simple(self, uid: int) -> Optional[List[Dict]]:
        """简化版获取用户视频"""
        url = "https://api.bilibili.com/x/space/arc/search"
        params = {
            'mid': uid,
            'ps': self.videos_per_page,
            'pn': 1,
            'order': 'pubdate'
        }

        try:
            print(f"🚀 快速请求用户 {uid} 的视频...")
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    videos = data.get('data', {}).get('list', {}).get('vlist', [])
                    print(f"✅ 成功获取 {len(videos)} 个视频")
                    return videos
                else:
                    print(f"❌ API错误：{data.get('message', '未知错误')}")
                    return None
            else:
                print(f"❌ HTTP错误：{response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 请求失败：{e}")
            return None

    def save_fast_results(self, uid: int, videos: List[Dict]) -> str:
        """快速保存结果"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        data = {
            "user_info": {
                "uid": uid,
                "total_videos": len(videos),
                "crawl_time": current_time,
                "method": "fast_crawl",
                "note": "仅获取第一页，快速预览"
            },
            "videos": videos
        }

        filename = f"videos_{uid}_fast_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"\n💾 快速结果已保存：{filepath}")
            return filepath

        except Exception as e:
            print(f"❌ 保存失败：{e}")
            return ""

    def run(self, uid: Optional[int] = None) -> bool:
        """运行快速爬虫"""
        # 获取UID
        if uid is None:
            try:
                uid_input = input("请输入B站用户UID：").strip()
                if not uid_input:
                    print("❌ UID不能为空")
                    return False
                uid = int(uid_input)
            except ValueError:
                print("❌ 请输入有效的数字UID")
                return False
            except KeyboardInterrupt:
                print("\n👋 程序已取消")
                return False

        print(f"\n⚡ 启动超快速爬虫")
        print(f"📍 目标UID: {uid}")
        print(f"⚠️  仅获取第一页数据，速度超快！")

        # 快速获取视频
        start_time = time.time()
        videos = self.get_user_videos_simple(uid)
        end_time = time.time()

        if not videos or len(videos) == 0:
            print("\n❌ 没有获取到任何视频")
            print("\n🔍 可能的原因：")
            print("1. UID不正确")
            print("2. 用户没有公开视频")
            print("3. 网络问题")
            print("4. B站API限制")
            return False

        print(f"\n⏱️  耗时：{end_time - start_time:.2f} 秒")
        print(f"📊 获取到 {len(videos)} 个视频")

        # 显示前几个视频预览
        print(f"\n🔝 前5个视频预览：")
        for i, video in enumerate(videos[:5], 1):
            print(f"   {i}. {video['title']}")
            print(f"      📺 {video['url']}")
            print(f"      ⏱️  时长: {video.get('length', 'N/A')}")
            print(f"      👀 播放: {video.get('play', 'N/A'):,}")
            print()

        # 保存结果
        filepath = self.save_fast_results(uid, videos)

        if filepath:
            print(f"\n✅ 快速爬取成功！")
            print(f"💡 提示：这只是第一页数据，如需更多视频请使用标准版本")
            return True
        else:
            return False

    def test_connection(self) -> bool:
        """测试网络连接"""
        print("🔍 测试网络连接...")

        test_url = "https://api.bilibili.com/x/web-interface/nav"
        try:
            response = requests.get(
                test_url,
                headers=self.headers,
                timeout=5,
                verify=False
            )
            if response.status_code == 200:
                print("✅ 网络连接正常")
                return True
            else:
                print(f"❌ 网络异常，状态码：{response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 网络连接失败：{e}")
            return False


def main():
    """主函数"""
    print("⚡ B站视频爬虫 - 超快速版本")
    print("=" * 40)
    print("🚀 特点：速度超快，10秒内获取结果")
    print("📝 限制：仅获取第一页数据")
    print()

    # 先测试网络
    crawler = BilibiliFastCrawler()
    if not crawler.test_connection():
        print("\n❌ 网络连接有问题，请检查：")
        print("1. 是否能访问 bilibili.com")
        print("2. 是否有网络连接")
        print("3. 是否被防火墙阻挡")
        return

    # 检查命令行参数
    uid = None
    if len(sys.argv) > 1:
        try:
            uid = int(sys.argv[1])
        except ValueError:
            print("❌ 命令行参数必须是数字UID")
            return

    # 运行快速爬虫
    success = crawler.run(uid)

    if success:
        print("\n🎉 任务完成！")
        print("\n🔄 如果需要获取完整视频列表，请运行：")
        print("   python run.py smart " + str(uid if uid else "[UID]"))
    else:
        print("\n💔 任务失败！")
        print("\n🔧 故障排除建议：")
        print("1. 检查UID是否正确")
        print("2. 确认用户有公开视频")
        print("3. 尝试使用智能版本")
        print("4. 检查网络代理设置")


if __name__ == "__main__":
    main()