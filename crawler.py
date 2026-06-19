import requests
import pandas as pd
import os
from datetime import datetime

def crawl_bilibili():
    """抓取B站AI玄幻/仙侠动画排行榜"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }
    
    search_url = "https://api.bilibili.com/x/web-interface/search/type"
    keywords = ["AI动画 玄幻", "AI动画 仙侠", "AI漫剧 修仙"]
    
    all_results = []
    rank_counter = 1
    
    for kw in keywords:
        params = {
            "keyword": kw,
            "search_type": "video",
            "order": "click",  # 按播放量排序
            "page": 1
        }
        try:
            resp = requests.get(search_url, headers=headers, params=params, timeout=10)
            data = resp.json()
            if data.get("data") and data["data"].get("result"):
                for item in data["data"]["result"][:15]:
                    title = item.get("title", "").replace('<em class="keyword">', '').replace('</em>', '')
                    all_results.append({
                        "排名": rank_counter,
                        "标题": title,
                        "作者": item.get("author", ""),
                        "播放量": item.get("play", 0),
                        "点赞": item.get("like", 0),
                        "弹幕": item.get("video_review", 0),
                        "链接": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                        "搜索词": kw
                    })
                    rank_counter += 1
        except Exception as e:
            print(f"抓取 {kw} 失败: {e}")
            
    # 按播放量重新排序并赋予最终排名
    df = pd.DataFrame(all_results)
    if not df.empty:
        df = df.sort_values(by="播放量", ascending=False).reset_index(drop=True)
        df["排名"] = df.index + 1
    
    return df

def save_data(df):
    """保存数据为CSV并更新网页"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 保存按日期归档的CSV
    os.makedirs("data", exist_ok=True)
    df.to_csv(f"data/rank_{today}.csv", index=False, encoding="utf-8-sig")
    
    # 2. 生成 index.html 网页用于展示
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI漫剧每日排行榜 (更新于 {today})</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; color: #333; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            h1 {{ text-align: center; color: #4a00e0; border-bottom: 2px solid #eee; padding-bottom: 15px;}}
            .date {{ text-align: center; color: #777; margin-bottom: 20px; font-size: 1.1em; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px 15px; border-bottom: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #4a00e0; color: white; }}
            tr:hover {{ background-color: #f1f1f1; }}
            .rank-1 {{ font-weight: bold; color: #FFD700; font-size: 1.2em; }}
            .rank-2 {{ font-weight: bold; color: #C0C0C0; font-size: 1.1em; }}
            .rank-3 {{ font-weight: bold; color: #CD7F32; font-size: 1.1em; }}
            a {{ color: #007bff; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .tag {{ background: #eef; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; color: #555; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 AI玄幻/仙侠漫剧排行榜</h1>
            <div class="date">数据来源：Bilibili | 更新日期：{today}</div>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>标题</th>
                        <th>作者</th>
                        <th>播放量</th>
                        <th>点赞</th>
                        <th>来源</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for _, row in df.iterrows():
        rank_class = f"rank-{row['排名']}" if row['排名'] <= 3 else ""
        # 格式化播放量数字
        play_str = f"{int(row['播放量']/10000)}万" if row['播放量'] >= 10000 else str(row['播放量'])
        
        html += f"""
                    <tr>
                        <td class="{rank_class}">#{row['排名']}</td>
                        <td><a href="{row['链接']}" target="_blank">{row['标题']}</a></td>
                        <td>{row['作者']}</td>
                        <td>▶ {play_str}</td>
                        <td>👍 {row['点赞']}</td>
                        <td><span class="tag">{row['搜索词']}</span></td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    print("开始采集B站AI漫剧数据...")
    df = crawl_bilibili()
    if not df.empty:
        save_data(df)
        print(f"✅ 采集完成！共获取 {len(df)} 条数据。")
    else:
        print("❌ 采集失败，未获取到数据。")
