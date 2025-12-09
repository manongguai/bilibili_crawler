#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频爬虫程序 - 智能版本
专门针对B站反爬虫机制的优化版本

作者：Kirk
日期：2025-12-08
"""

import json
import os
import sys
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional
import warnings

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass


class BilibiliSmartCrawler:
    """B站视频爬虫类（智能版本）"""

    def __init__(self):
        """初始化爬虫配置"""
        self.max_retries = 10  # 最大重试次数
        self.base_retry_delay = 15  # 基础重试延迟
        self.base_request_delay = 8  # 基础请求间隔
        self.videos_per_page = 5  # 每页视频数量（非常少）
        self.output_dir = "./output"
        self.consecutive_failures = 0  # 连续失败计数
        self.last_success_time = None  # 上次成功时间

        # 多个User-Agent轮换
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    def get_random_headers(self):
        """获取随机请求头"""
        user_agent = random.choice(self.user_agents)
        return {
            'User-Agent': user_agent,
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': f'zh-CN,zh;q=0.{random.randint(8,9)},en;q=0.{random.randint(6,8)}',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': random.choice(['"macOS"', '"Windows"', '"Linux"']),
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Origin': 'https://www.bilibili.com'
        }

    def smart_delay(self, base_delay, page=1):
        """智能延迟计算"""
        # 基础延迟 + 页数影响 + 随机因素 + 连续失败影响
        page_factor = min(page * 2, 30)  # 页数影响，最多30秒
        failure_factor = min(self.consecutive_failures * 10, 120)  # 失败影响，最多120秒

        total_delay = base_delay + page_factor + failure_factor + random.uniform(5, 15)

        print(f"⏱️  智能延迟 {total_delay:.1f} 秒 (页数:{page}, 失败:{self.consecutive_failures})")
        time.sleep(total_delay)

    def make_request(self, url, params=None, description="请求"):
        """发送HTTP请求"""
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    self.smart_delay(self.base_retry_delay)

                # 每次都使用新的请求头
                headers = self.get_random_headers()

                print(f"🌐 正在{description} (尝试 {attempt + 1}/{self.max_retries})")

                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30,
                    verify=False
                )
                response.raise_for_status()
                data = response.json()

                if data.get('code') == 0:
                    self.consecutive_failures = 0  # 重置失败计数
                    self.last_success_time = time.time()
                    return data.get('data', {})
                else:
                    error_msg = data.get('message', '未知错误')
                    if '频繁' in error_msg or '频率' in error_msg or '上限' in error_msg:
                        self.consecutive_failures += 1
                        wait_time = 60 + self.consecutive_failures * 30  # 递增等待时间
                        print(f"⚠️  触发频率限制，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ {description}失败：{error_msg}")
                        self.consecutive_failures += 1
                        return None

            except requests.exceptions.Timeout:
                print(f"⏰ {description}超时")
                self.consecutive_failures += 1
            except requests.exceptions.ConnectionError:
                print(f"🔌 {description}连接错误")
                self.consecutive_failures += 1
            except Exception as e:
                print(f"❌ {description}异常：{e}")
                self.consecutive_failures += 1

        print(f"💥 {description}失败，已达到最大重试次数")
        return None

    def get_user_info(self, uid: int) -> bool:
        """检查用户是否存在"""
        url = f"https://api.bilibili.com/x/space/arc/search"
        params = {
            'mid': uid,
            'ps': 1,
            'pn': 1
        }

        data = self.make_request(url, params, f"检查用户 {uid}")
        return data is not None

    def init_save_file(self, uid: int) -> str:
        """初始化保存文件"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"videos_{uid}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        init_data = {
            "user_info": {
                "uid": uid,
                "total_videos": 0,
                "start_time": current_time,
                "status": "crawling",
                "crawler_version": "smart_v1.0"
            },
            "videos": []
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(init_data, f, ensure_ascii=False, indent=2)
            print(f"📝 初始化保存文件：{filepath}")
            return filepath
        except Exception as e:
            print(f"❌ 初始化文件失败：{e}")
            return ""

    def append_videos_to_file(self, filepath: str, new_videos: List[Dict]) -> bool:
        """增量添加视频到文件"""
        if not new_videos:
            return True

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data['videos'].extend(new_videos)
            data['user_info']['total_videos'] = len(data['videos'])
            data['user_info']['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ 已追加 {len(new_videos)} 个视频，总计 {data['user_info']['total_videos']} 个")
            return True

        except Exception as e:
            print(f"❌ 追加视频失败：{e}")
            return False

    def finalize_save_file(self, filepath: str) -> str:
        """完成文件保存"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data['user_info']['status'] = 'completed'
            data['user_info']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            dir_path = os.path.dirname(filepath)
            base_name = os.path.basename(filepath)
            final_name = base_name.replace('.json', '_final.json')
            final_path = os.path.join(dir_path, final_name)

            with open(final_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            os.remove(filepath)

            print(f"\n🎉 最终文件已保存：{final_path}")
            print(f"📊 总计爬取 {data['user_info']['total_videos']} 个视频")

            return final_path

        except Exception as e:
            print(f"❌ 完成保存失败：{e}")
            return filepath

    def fetch_all_videos(self, uid: int) -> List[Dict]:
        """获取用户的所有视频（保留兼容性）"""
        all_videos = []
        page = 1

        print(f"\n🎬 开始爬取用户 {uid} 的视频列表")
        print("=" * 60)

        if not self.get_user_info(uid):
            print(f"❌ 用户 {uid} 不存在或没有公开视频")
            return []

        while True:
            if page > 1:
                self.smart_delay(self.base_request_delay, page)

            url = "https://api.bilibili.com/x/space/arc/search"
            params = {
                'mid': uid,
                'ps': self.videos_per_page,
                'pn': page,
                'order': 'pubdate'
            }

            data = self.make_request(url, params, f"获取第 {page} 页")

            if not data:
                print(f"🛑 无法获取第 {page} 页，停止爬取")
                break

            videos = data.get('list', {}).get('vlist', [])

            if not videos:
                print(f"✅ 第 {page} 页没有视频，爬取完成")
                break

            for i, video_info in enumerate(videos):
                video_data = {
                    'aid': video_info.get('aid'),
                    'bvid': video_info.get('bvid'),
                    'title': video_info.get('title'),
                    'url': f"https://www.bilibili.com/video/{video_info.get('bvid')}",
                    'duration': video_info.get('length'),
                    'created': video_info.get('created'),
                    'view': video_info.get('play'),
                    'danmaku': video_info.get('video_review'),
                    'reply': video_info.get('comment'),
                    'pic': video_info.get('pic'),
                    'description': video_info.get('description', '')
                }
                all_videos.append(video_data)

                if i < len(videos) - 1:
                    time.sleep(random.uniform(1, 3))

            print(f"✅ 第 {page} 页完成：{len(videos)} 个视频，总计 {len(all_videos)} 个")

            page_info = data.get('page', {})
            count = page_info.get('count', 0)
            if count > 0 and len(all_videos) >= count:
                print(f"✅ 已获取所有 {count} 个视频")
                break

            if len(videos) < self.videos_per_page:
                print(f"✅ 当前页视频数不足，说明已到最后一页")
                break

            page += 1

            if page % 3 == 1:
                print(f"☕ 已爬取 {page-1} 页，强制休息 60 秒...")
                time.sleep(60)

        return all_videos

    def fetch_all_videos_with_incremental_save(self, uid: int) -> int:
        """获取用户的所有视频并增量保存"""
        save_filepath = self.init_save_file(uid)
        if not save_filepath:
            return 0

        total_videos = 0
        page = 1

        print(f"\n🎬 开始爬取用户 {uid} 的视频列表")
        print("=" * 60)
        print("💾 使用增量保存模式，数据会实时保存到文件")

        if not self.get_user_info(uid):
            print(f"❌ 用户 {uid} 不存在或没有公开视频")
            return 0

        print("\n📝 注意：数据会实时保存，即使程序中断也不会丢失已爬取的数据\n")

        while True:
            if page > 1:
                self.smart_delay(self.base_request_delay, page)

            url = "https://api.bilibili.com/x/space/arc/search"
            params = {
                'mid': uid,
                'ps': self.videos_per_page,
                'pn': page,
                'order': 'pubdate'
            }

            data = self.make_request(url, params, f"获取第 {page} 页")

            if not data:
                print(f"🛑 无法获取第 {page} 页，停止爬取")
                break

            videos = data.get('list', {}).get('vlist', [])

            if not videos:
                print(f"✅ 第 {page} 页没有视频，爬取完成")
                break

            page_videos = []
            for i, video_info in enumerate(videos):
                video_data = {
                    'aid': video_info.get('aid'),
                    'bvid': video_info.get('bvid'),
                    'title': video_info.get('title'),
                    'url': f"https://www.bilibili.com/video/{video_info.get('bvid')}",
                    'duration': video_info.get('length'),
                    'created': video_info.get('created'),
                    'view': video_info.get('play'),
                    'danmaku': video_info.get('video_review'),
                    'reply': video_info.get('comment'),
                    'pic': video_info.get('pic'),
                    'description': video_info.get('description', '')
                }
                page_videos.append(video_data)

                if i < len(videos) - 1:
                    time.sleep(random.uniform(1, 3))

            # 立即保存到文件
            if self.append_videos_to_file(save_filepath, page_videos):
                total_videos += len(page_videos)
                print(f"✅ 第 {page} 页完成：{len(page_videos)} 个视频，总计 {total_videos} 个")
            else:
                print(f"❌ 第 {page} 页保存失败")
                break

            page_info = data.get('page', {})
            count = page_info.get('count', 0)
            if count > 0 and total_videos >= count:
                print(f"✅ 已获取所有 {count} 个视频")
                break

            if len(videos) < self.videos_per_page:
                print(f"✅ 当前页视频数不足，说明已到最后一页")
                break

            page += 1

            if page % 3 == 1:
                print(f"☕ 已爬取 {page-1} 页，强制休息 60 秒...")
                time.sleep(60)

        # 完成保存
        self.finalize_save_file(save_filepath)

        return total_videos

    def save_to_json(self, uid: int, videos: List[Dict]) -> str:
        """保存数据到JSON文件"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        data = {
            "user_info": {
                "uid": uid,
                "total_videos": len(videos),
                "crawl_time": current_time,
                "crawler_version": "smart_v1.0"
            },
            "videos": videos
        }

        filename = f"videos_{uid}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"\n💾 数据已保存到：{filepath}")
            return filepath

        except Exception as e:
            print(f"❌ 保存文件失败：{e}")
            return ""

    def run(self, uid: Optional[int] = None) -> bool:
        """运行爬虫主程序"""
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
                print("\n\n👋 程序已取消")
                return False

        print(f"\n🚀 启动智能爬虫，目标用户：{uid}")
        print("⚠️  注意：此版本包含智能反爬虫策略，可能需要较长时间")
        print("💾 使用增量保存模式，数据会实时保存到文件")

        # 使用增量保存模式爬取视频
        total_videos = self.fetch_all_videos_with_incremental_save(uid)

        if total_videos == 0:
            print("\n❌ 没有找到任何视频")
            return False

        print(f"\n🎉 爬取完成！共获取到 {total_videos} 个视频")

        # 显示最终统计信息
        print(f"\n📊 最终统计：")
        print(f"   总视频数：{total_videos}")
        print(f"   数据已保存到 output/ 文件夹")
        print(f"   文件名格式：videos_{uid}_时间戳_final.json")

        print("\n💡 提示：")
        print(f"   - 即使程序中途失败，已爬取的数据也已保存")
        print(f"   - 可以检查 output/ 文件夹中的临时文件")
        print(f"   - 智能版本提供了最佳的反爬虫策略")

        return True


def main():
    """主函数"""
    print("🤖 B站视频爬虫 - 智能版本")
    print("=" * 50)
    print("🔧 特性：智能反爬虫、自适应延迟、多User-Agent轮换")
    print("⚠️  注意：此版本专为绕过反爬虫机制优化，速度较慢但成功率更高")
    print()

    # 检查命令行参数
    uid = None
    if len(sys.argv) > 1:
        try:
            uid = int(sys.argv[1])
        except ValueError:
            print("❌ 命令行参数必须是数字UID")
            return

    # 运行爬虫
    crawler = BilibiliSmartCrawler()
    success = crawler.run(uid)

    if success:
        print("\n🎊 程序执行完成！")
    else:
        print("\n💔 程序执行失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()