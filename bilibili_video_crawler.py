#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频爬虫程序
用于爬取指定B站用户的所有视频标题和链接

作者：Kirk
日期：2025-12-08
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    from bilibili_api import user, video
    from bilibili_api.exceptions import ResponseCodeException
except ImportError:
    print("错误：未找到 bilibili-api 库")
    print("请运行：pip install bilibili-api")
    sys.exit(1)


class BilibiliCrawler:
    """B站视频爬虫类"""

    def __init__(self):
        """初始化爬虫配置"""
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试延迟（秒）
        self.request_delay = 1  # 请求间隔（秒）
        self.videos_per_page = 30  # 每页视频数量
        self.output_dir = "./output"  # 输出目录

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    async def get_user_info(self, uid: int) -> Optional[Dict]:
        """
        获取用户信息

        Args:
            uid: 用户UID

        Returns:
            用户信息字典，失败返回None
        """
        try:
            user_obj = user.User(uid=uid)
            info = await user_obj.get_info()
            return info
        except ResponseCodeException as e:
            print(f"获取用户信息失败：{e}")
            return None
        except Exception as e:
            print(f"获取用户信息时发生错误：{e}")
            return None

    async def get_user_videos(self, uid: int, page: int = 1) -> Optional[Dict]:
        """
        获取用户视频列表（分页）

        Args:
            uid: 用户UID
            page: 页码，从1开始

        Returns:
            视频列表数据，失败返回None
        """
        try:
            user_obj = user.User(uid=uid)

            # 获取视频列表
            videos_data = await user_obj.get_videos(
                pn=page,
                ps=self.videos_per_page
            )

            return videos_data

        except ResponseCodeException as e:
            if e.code in [-400, -404]:
                print(f"错误：用户 {uid} 不存在或没有公开视频")
            else:
                print(f"获取视频列表失败（页码：{page}）：{e}")
            return None
        except Exception as e:
            print(f"获取视频列表时发生错误（页码：{page}）：{e}")
            return None

    async def fetch_all_videos(self, uid: int) -> List[Dict]:
        """
        获取用户的所有视频

        Args:
            uid: 用户UID

        Returns:
            所有视频的列表
        """
        all_videos = []
        page = 1

        print("开始爬取视频列表...")

        while True:
            # 添加请求延迟
            if page > 1:
                time.sleep(self.request_delay)

            # 获取当前页视频
            videos_data = await self.get_user_videos(uid, page)

            if not videos_data:
                break

            # 提取视频列表
            videos = videos_data.get('list', {}).get('vlist', [])

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
                    'reply': video_info.get('comment')
                }
                all_videos.append(video_data)

            print(f"已获取第 {page} 页，本页 {len(videos)} 个视频，总计 {len(all_videos)} 个视频")

            # 检查是否还有更多页面
            page_info = videos_data.get('list', {}).get('page', {})
            if page_info.get('count', 0) <= len(all_videos):
                break

            page += 1

        return all_videos

    def save_to_json(self, uid: int, videos: List[Dict]) -> str:
        """
        保存数据到JSON文件

        Args:
            uid: 用户UID
            videos: 视频列表

        Returns:
            保存的文件路径
        """
        # 准备数据
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

        # 生成文件名
        filename = f"videos_{uid}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        # 保存文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"\n数据已保存到：{filepath}")
            return filepath

        except Exception as e:
            print(f"保存文件失败：{e}")
            return ""

    async def run(self, uid: Optional[int] = None) -> bool:
        """
        运行爬虫主程序

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

        # 获取用户信息（可选）
        user_info = await self.get_user_info(uid)
        if user_info:
            print(f"用户名：{user_info.get('name', '未知')}")
            print(f"用户签名：{user_info.get('sign', '无')}")
            print("-" * 50)

        # 获取所有视频
        videos = await self.fetch_all_videos(uid)

        if not videos:
            print("\n没有找到任何视频")
            return False

        print(f"\n爬取完成！共获取到 {len(videos)} 个视频")

        # 保存数据
        filepath = self.save_to_json(uid, videos)

        if filepath:
            # 显示统计信息
            print("\n统计信息：")
            print(f"- 总视频数：{len(videos)}")

            # 计算总播放量
            total_views = sum(v.get('view', 0) for v in videos if v.get('view'))
            if total_views > 0:
                print(f"- 总播放量：{total_views:,}")

            # 显示前5个视频作为示例
            print("\n前5个视频：")
            for i, video in enumerate(videos[:5], 1):
                print(f"{i}. {video['title']}")
                print(f"   {video['url']}")

            if len(videos) > 5:
                print(f"... 还有 {len(videos) - 5} 个视频")

            return True
        else:
            return False


async def main():
    """主函数"""
    print("=" * 50)
    print("B站视频爬虫程序")
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
    crawler = BilibiliCrawler()
    success = await crawler.run(uid)

    if success:
        print("\n程序执行完成！")
    else:
        print("\n程序执行失败！")
        sys.exit(1)


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())