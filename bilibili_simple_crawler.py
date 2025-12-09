#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频爬虫程序（简化版）
使用requests直接爬取B站API，不依赖bilibili-api库

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


class BilibiliSimpleCrawler:
    """B站视频爬虫类（简化版）"""

    def __init__(self):
        """初始化爬虫配置"""
        self.max_retries = 8  # 最大重试次数（进一步增加）
        self.retry_delay = 10  # 重试延迟（秒，进一步增加）
        self.request_delay = 5  # 基础请求间隔（秒，进一步增加）
        self.videos_per_page = 10  # 每页视频数量（进一步减少）
        self.output_dir = "./output"  # 输出目录

        # 多个User-Agent轮换
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        # 获取随机User-Agent
        import random
        user_agent = random.choice(self.user_agents)

        self.headers = {
            'User-Agent': user_agent,
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Origin': 'https://www.bilibili.com'
        }

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    def get_user_info(self, uid: int) -> Optional[Dict]:
        """
        获取用户信息

        Args:
            uid: 用户UID

        Returns:
            用户信息字典，失败返回None
        """
        url = f"https://api.bilibili.com/x/space/arc/search"
        params = {
            'mid': uid,
            'ps': 1,
            'pn': 1
        }

        for attempt in range(self.max_retries):
            try:
                # 添加随机延迟和User-Agent轮换
                if attempt > 0:
                    # 频率限制时使用更长的延迟
                    if attempt > 2:
                        delay = 30 + random.uniform(10, 20)  # 30-50秒
                        print(f"🔄 检测到多次失败，等待 {delay:.1f} 秒...")
                    else:
                        delay = self.retry_delay + random.uniform(5, 10)  # 15-20秒
                        print(f"等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)

                    # 轮换User-Agent
                    user_agent = random.choice(self.user_agents)
                    self.headers['User-Agent'] = user_agent

                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=15,
                    verify=False  # 禁用SSL验证（仅用于解决兼容性问题）
                )
                response.raise_for_status()
                data = response.json()

                if data.get('code') == 0:
                    return data.get('data', {}).get('list', {}).get('vlist', [])
                else:
                    error_msg = data.get('message', '未知错误')
                    if '频繁' in error_msg or '频率' in error_msg:
                        print(f"请求过于频繁，等待更长时间...")
                        time.sleep(30)  # 频率限制时等待更长时间
                        continue
                    print(f"获取用户信息失败：{error_msg}")
                    return None

            except requests.exceptions.Timeout:
                print(f"请求超时（尝试 {attempt + 1}/{self.max_retries}）")
            except requests.exceptions.ConnectionError:
                print(f"网络连接错误（尝试 {attempt + 1}/{self.max_retries}）")
            except Exception as e:
                print(f"获取用户信息时发生错误（尝试 {attempt + 1}/{self.max_retries}）：{e}")

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
            else:
                print("已达到最大重试次数")
                return None

    def get_user_videos(self, uid: int, page: int = 1) -> Optional[Dict]:
        """
        获取用户视频列表（分页）

        Args:
            uid: 用户UID
            page: 页码，从1开始

        Returns:
            视频列表数据，失败返回None
        """
        url = "https://api.bilibili.com/x/space/arc/search"
        params = {
            'mid': uid,
            'ps': self.videos_per_page,
            'pn': page,
            'order': 'pubdate'  # 按发布时间排序
        }

        for attempt in range(self.max_retries):
            try:
                # 添加随机延迟和User-Agent轮换
                if attempt > 0:
                    # 频率限制时使用更长的延迟
                    if attempt > 2:
                        delay = 30 + random.uniform(10, 20)  # 30-50秒
                        print(f"🔄 检测到多次失败，等待 {delay:.1f} 秒...")
                    else:
                        delay = self.retry_delay + random.uniform(5, 10)  # 15-20秒
                        print(f"等待 {delay:.1f} 秒后重试第 {page} 页...")
                    time.sleep(delay)

                    # 轮换User-Agent
                    user_agent = random.choice(self.user_agents)
                    self.headers['User-Agent'] = user_agent

                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=20,
                    verify=False  # 禁用SSL验证（仅用于解决兼容性问题）
                )
                response.raise_for_status()
                data = response.json()

                if data.get('code') == 0:
                    return data.get('data', {})
                else:
                    error_msg = data.get('message', '未知错误')
                    if '频繁' in error_msg or '频率' in error_msg:
                        print(f"请求过于频繁，等待更长时间（{page}页）...")
                        time.sleep(30)  # 频率限制时等待更长时间
                        continue
                    elif '不存在' in error_msg or '找不到' in error_msg:
                        print(f"用户不存在或没有公开视频（{page}页）")
                        return None
                    else:
                        print(f"获取视频列表失败（页码：{page}）：{error_msg}")
                        return None

            except requests.exceptions.Timeout:
                print(f"请求超时（页码：{page}，尝试 {attempt + 1}/{self.max_retries}）")
            except requests.exceptions.ConnectionError:
                print(f"网络连接错误（页码：{page}，尝试 {attempt + 1}/{self.max_retries}）")
            except Exception as e:
                print(f"获取视频列表时发生错误（页码：{page}，尝试 {attempt + 1}/{self.max_retries}）：{e}")

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
            else:
                print(f"第 {page} 页已达到最大重试次数")
                return None

    def fetch_all_videos_with_incremental_save(self, uid: int) -> int:
        """
        获取用户的所有视频并增量保存

        Args:
            uid: 用户UID

        Returns:
            获取到的视频总数
        """
        # 初始化保存文件
        save_filepath = self.init_save_file(uid)
        if not save_filepath:
            return 0

        total_videos = 0
        page = 1

        print("开始爬取视频列表...")

        while True:
            # 添加智能请求延迟
            if page > 1:
                # 基础延迟 + 随机延迟
                base_delay = self.request_delay + (page - 1) * 0.5  # 逐页增加延迟
                random_delay = random.uniform(2, 5)
                total_delay = base_delay + random_delay
                print(f"等待 {total_delay:.1f} 秒后获取下一页...")
                time.sleep(total_delay)

            # 获取当前页视频
            print(f"正在获取第 {page} 页...")
            data = self.get_user_videos(uid, page)

            if not data:
                print(f"第 {page} 页获取失败，停止爬取")
                break

            # 提取视频列表
            videos = data.get('list', {}).get('vlist', [])

            if not videos:
                print(f"第 {page} 页没有视频，爬取完成")
                break

            # 处理每个视频信息
            page_videos = []
            for video_info in videos:
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

            # 立即保存到文件
            if self.append_videos_to_file(save_filepath, page_videos):
                total_videos += len(page_videos)
                print(f"✅ 第 {page} 页完成：{len(page_videos)} 个视频，总计 {total_videos} 个")
            else:
                print(f"❌ 第 {page} 页保存失败")
                break

            # 检查是否还有更多页面
            page_info = data.get('page', {})
            count = page_info.get('count', 0)
            if count > 0 and total_videos >= count:
                print(f"✅ 已获取所有 {count} 个视频")
                break

            # 如果当前页的视频数少于期望，说明没有更多页面了
            if len(videos) < self.videos_per_page:
                print(f"✅ 当前页视频数不足，说明已到最后一页")
                break

            page += 1

        # 完成保存
        self.finalize_save_file(save_filepath)

        return total_videos

    def fetch_all_videos(self, uid: int) -> List[Dict]:
        """
        获取用户的所有视频（原版本，保留兼容性）

        Args:
            uid: 用户UID

        Returns:
            所有视频的列表
        """
        all_videos = []
        page = 1

        print("开始爬取视频列表...")

        while True:
            # 添加智能请求延迟
            if page > 1:
                # 基础延迟 + 随机延迟
                base_delay = self.request_delay + (page - 1) * 0.5  # 逐页增加延迟
                random_delay = random.uniform(2, 5)
                total_delay = base_delay + random_delay
                print(f"等待 {total_delay:.1f} 秒后获取下一页...")
                time.sleep(total_delay)

            # 获取当前页视频
            print(f"正在获取第 {page} 页...")
            data = self.get_user_videos(uid, page)

            if not data:
                break

            # 提取视频列表
            videos = data.get('list', {}).get('vlist', [])

            if not videos:
                print(f"第 {page} 页没有视频，爬取完成")
                break

            # 处理每个视频信息
            for video_info in videos:
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

            print(f"已获取第 {page} 页，本页 {len(videos)} 个视频，总计 {len(all_videos)} 个视频")

            # 检查是否还有更多页面
            page_info = data.get('page', {})
            count = page_info.get('count', 0)
            if count > 0 and len(all_videos) >= count:
                print(f"已获取所有 {count} 个视频")
                break

            # 如果当前页的视频数少于期望，说明没有更多页面了
            if len(videos) < self.videos_per_page:
                break

            page += 1

        return all_videos

    def init_save_file(self, uid: int) -> str:
        """
        初始化保存文件

        Args:
            uid: 用户UID

        Returns:
            文件路径
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"videos_{uid}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        # 初始化文件结构
        init_data = {
            "user_info": {
                "uid": uid,
                "total_videos": 0,
                "start_time": current_time,
                "status": "crawling"
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
        """
        增量添加视频到文件

        Args:
            filepath: 文件路径
            new_videos: 新获取的视频列表

        Returns:
            是否成功
        """
        if not new_videos:
            return True

        try:
            # 读取现有数据
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 追加新视频
            data['videos'].extend(new_videos)
            data['user_info']['total_videos'] = len(data['videos'])
            data['user_info']['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 写回文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ 已追加 {len(new_videos)} 个视频，总计 {data['user_info']['total_videos']} 个")
            return True

        except Exception as e:
            print(f"❌ 追加视频失败：{e}")
            return False

    def finalize_save_file(self, filepath: str) -> str:
        """
        完成文件保存

        Args:
            filepath: 文件路径

        Returns:
            最终文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 更新最终状态
            data['user_info']['status'] = 'completed'
            data['user_info']['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 重命名文件，加上最终标记
            dir_path = os.path.dirname(filepath)
            base_name = os.path.basename(filepath)
            final_name = base_name.replace('.json', '_final.json')
            final_path = os.path.join(dir_path, final_name)

            with open(final_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 删除临时文件
            os.remove(filepath)

            print(f"\n🎉 最终文件已保存：{final_path}")
            print(f"📊 总计爬取 {data['user_info']['total_videos']} 个视频")

            return final_path

        except Exception as e:
            print(f"❌ 完成保存失败：{e}")
            return filepath

    def save_to_json(self, uid: int, videos: List[Dict]) -> str:
        """
        保存数据到JSON文件（兼容旧版本）

        Args:
            uid: 用户UID
            videos: 视频列表

        Returns:
            保存的文件路径
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        data = {
            "user_info": {
                "uid": uid,
                "total_videos": len(videos),
                "crawl_time": current_time
            },
            "videos": videos
        }

        filename = f"videos_{uid}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"\n数据已保存到：{filepath}")
            return filepath

        except Exception as e:
            print(f"保存文件失败：{e}")
            return ""

    def run(self, uid: Optional[int] = None) -> bool:
        """
        运行爬虫主程序（使用增量保存）

        Args:
            uid: 用户UID，如果为None则从命令行获取

        Returns:
            是否成功完成
        """
        # 获取UID
        if uid is None:
            try:
                uid_input = input("请输入B站用户UID：").strip()
                if not uid_input:
                    print("错误：UID不能为空")
                    return False

                uid = int(uid_input)

            except ValueError:
                print("错误：请输入有效的数字UID")
                return False
            except KeyboardInterrupt:
                print("\n\n程序已取消")
                return False

        print(f"\n开始爬取用户 {uid} 的视频列表...")
        print("=" * 50)
        print("💾 使用增量保存模式，数据会实时保存到文件")

        # 获取用户信息（测试连接）
        test_data = self.get_user_info(uid)
        if not test_data:
            print("\n获取用户信息失败，请检查UID是否正确")
            return False

        print(f"✅ 连接成功！")
        print("\n📝 注意：数据会实时保存，即使程序中断也不会丢失已爬取的数据\n")

        # 使用增量保存模式爬取视频
        total_videos = self.fetch_all_videos_with_incremental_save(uid)

        if total_videos == 0:
            print("\n❌ 没有找到任何视频")
            return False

        print(f"\n✅ 爬取完成！共获取到 {total_videos} 个视频")

        # 显示最终统计信息
        print("\n📊 最终统计：")
        print(f"- 总视频数：{total_videos}")
        print("- 数据已保存到 output/ 文件夹")
        print("- 文件名格式：videos_{uid}_时间戳_final.json")

        print("\n💡 提示：")
        print("- 即使程序中途失败，已爬取的数据也已保存")
        print("- 可以检查 output/ 文件夹中的临时文件")

        return True


def main():
    """主函数"""
    print("=" * 50)
    print("B站视频爬虫程序（简化版）")
    print("=" * 50)
    print()

    # 检查是否提供了命令行参数
    uid = None
    if len(sys.argv) > 1:
        try:
            uid = int(sys.argv[1])
        except ValueError:
            print("错误：命令行参数必须是数字UID")
            return

    # 创建爬虫实例并运行
    crawler = BilibiliSimpleCrawler()
    success = crawler.run(uid)

    if success:
        print("\n程序执行完成！")
    else:
        print("\n程序执行失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()