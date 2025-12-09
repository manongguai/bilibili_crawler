# B站视频爬虫程序

一个用于爬取B站指定用户所有视频标题和链接的Python程序。

## 功能特点

- 🎯 支持通过UID爬取任意B站用户的所有视频
- 📝 获取视频标题、链接、播放量、评论数等详细信息
- 📁 自动保存为JSON格式，便于后续处理
- 🔄 分页爬取，支持大量视频
- ⚡ 带有重试机制和错误处理
- 📊 显示爬取进度和统计信息

## 文件说明

- `bilibili_video_crawler.py` - 使用bilibili-api库的完整版本（推荐）
- `bilibili_simple_crawler.py` - 使用requests的简化版本（备用）
- `requirements.txt` - 项目依赖列表
- `output/` - 输出目录（自动创建）

## 安装方法

### 方法1：使用bilibili-api库（推荐）

```bash
# 安装依赖（可能遇到版本冲突问题）
pip install bilibili-api requests

# 或者使用简化版本（只需要requests）
pip install requests
```

### 方法2：只使用requests库

简化版本只需要requests库：

```bash
pip install requests
```

## 使用方法

### 方法1：命令行使用

```bash
# 直接传入UID参数
python bilibili_simple_crawler.py 435776729

# 或使用完整版本（如果成功安装了bilibili-api）
python bilibili_video_crawler.py 435776729
```

### 方法2：交互式使用

```bash
# 运行程序，然后按提示输入UID
python bilibili_simple_crawler.py
```

程序会提示：
```
请输入B站用户UID：
```

输入目标用户的UID后按回车即可。

## 如何获取UID

1. 打开目标用户的B站主页
2. 查看浏览器地址栏，URL格式为：`https://space.bilibili.com/{UID}`
3. 例如：`https://space.bilibili.com/435776729` 的UID就是 `435776729`

## 输出格式

程序会在 `output/` 目录下生成JSON文件，格式如下：

```json
{
  "user_info": {
    "uid": 435776729,
    "total_videos": 50,
    "crawl_time": "2025-12-08 15:30:45"
  },
  "videos": [
    {
      "aid": 987654321,
      "bvid": "BV1xxxxxx",
      "title": "视频标题",
      "url": "https://www.bilibili.com/video/BV1xxxxxx",
      "duration": "10:30",
      "created": 1703123456,
      "view": 1000000,
      "danmaku": 5000,
      "reply": 2000,
      "pic": "封面图片URL",
      "description": "视频描述"
    }
  ]
}
```

## 注意事项

### ⚠️ 重要提醒

1. **请求频率限制**：B站对API请求有频率限制，请勿过于频繁地运行程序
2. **仅供学习使用**：本程序仅用于学习目的，请遵守B站的使用条款
3. **隐私保护**：只爬取公开数据，不涉及任何私密信息
4. **网络环境**：如果遇到网络问题，请检查网络连接或稍后重试

### 常见问题

1. **"请求过于频繁"错误**
   - 解决方案：等待一段时间再运行程序，或降低爬取频率

2. **"用户不存在"错误**
   - 解决方案：检查输入的UID是否正确，确保用户存在且视频为公开状态

3. **依赖安装问题**
   - 推荐使用简化版本 `bilibili_simple_crawler.py`
   - 只需要安装requests库：`pip install requests`

4. **网络连接问题**
   - 检查网络连接
   - 可能需要设置代理（如有需要）

## 测试用例

可以使用以下UID进行测试：

- 何同学：435776729
- 罗翔说刑法：269066291
- 老番茄：29002508

## 技术说明

### bilibili_video_crawler.py（完整版）
- 使用官方的bilibili-api库
- 功能更全面，支持更多API特性
- 可能存在依赖版本冲突问题

### bilibili_simple_crawler.py（简化版）
- 直接使用requests调用B站API
- 依赖更少，更容易安装
- 基本功能完整，适合一般使用

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和B站的使用条款。

## 联系方式

如有问题或建议，请通过GitHub Issues反馈。