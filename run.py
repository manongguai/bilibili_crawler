#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频爬虫 - 一键运行脚本

使用方法：
python run.py

或者直接指定UID：
python run.py UID

使用智能版本：
python run.py smart UID

示例：
python run.py 435776729
python run.py smart 435776729
"""

import sys
import os

def main():
    print("🎬 B站视频爬虫程序")
    print("=" * 40)
    print("📋 版本选择：")
    print("   1. 标准版本 - 速度较快，可能遇到频率限制")
    print("   2. 智能版本 - 速度较慢，成功率更高")
    print("   3. 快速版本 - 10秒获取结果，仅第一页数据")
    print()

    # 解析命令行参数
    use_smart = False
    use_fast = False
    uid = None

    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'smart':
            use_smart = True
            if len(sys.argv) > 2:
                try:
                    uid = int(sys.argv[2])
                    print(f"📍 目标UID: {uid}")
                except ValueError:
                    print("❌ 错误：UID必须是数字")
                    return
        elif sys.argv[1].lower() == 'fast':
            use_fast = True
            if len(sys.argv) > 2:
                try:
                    uid = int(sys.argv[2])
                    print(f"📍 目标UID: {uid}")
                except ValueError:
                    print("❌ 错误：UID必须是数字")
                    return
        else:
            try:
                uid = int(sys.argv[1])
                print(f"📍 目标UID: {uid}")
            except ValueError:
                print("❌ 错误：UID必须是数字")
                return

    # 如果没有指定版本，让用户选择
    if not use_smart and not use_fast and len(sys.argv) <= 1:
        try:
            choice = input("请选择版本 (1/2/3) [默认:1]: ").strip()
            if choice == '2':
                use_smart = True
            elif choice == '3':
                use_fast = True
        except KeyboardInterrupt:
            print("\n👋 程序已取消")
            return

    # 选择爬虫版本
    if use_fast:
        print("\n🚀 使用快速版本（10秒获取结果）")
        try:
            from bilibili_fast_crawler import BilibiliFastCrawler
            crawler = BilibiliFastCrawler()
        except ImportError:
            print("❌ 无法导入快速版本，使用标准版本")
            from bilibili_simple_crawler import BilibiliSimpleCrawler
            crawler = BilibiliSimpleCrawler()
    elif use_smart:
        print("\n🤖 使用智能版本（成功率更高）")
        try:
            from bilibili_smart_crawler import BilibiliSmartCrawler
            crawler = BilibiliSmartCrawler()
        except ImportError:
            print("❌ 无法导入智能版本，使用标准版本")
            from bilibili_simple_crawler import BilibiliSimpleCrawler
            crawler = BilibiliSimpleCrawler()
    else:
        print("\n⚡ 使用标准版本（速度较快）")
        from bilibili_simple_crawler import BilibiliSimpleCrawler
        crawler = BilibiliSimpleCrawler()

    print("\n🚀 开始爬取...")
    success = crawler.run(uid)

    if success:
        print("\n✅ 爬取成功！")
    else:
        print("\n❌ 爬取失败，请检查UID或稍后重试")
        print("💡 建议尝试：")
        print("   1. 使用智能版本：python run.py smart")
        print("   2. 使用快速版本：python run.py fast")
        print("   3. 运行诊断工具：python diagnose.py")

    # 询问是否继续
    try:
        answer = input("\n🔄 是否继续爬取其他用户？(y/n): ").strip().lower()
        if answer == 'y' or answer == 'yes':
            # 递归调用，继续爬取
            main()
    except KeyboardInterrupt:
        print("\n👋 再见！")

if __name__ == "__main__":
    main()