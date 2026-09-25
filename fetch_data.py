# -*- coding: utf-8 -*-
"""
福彩3D 历史数据抓取脚本
直接从中国福彩官网抓取最近N期开奖数据，生成 data.json
HTML 启动时直接加载本地 data.json，无需 CORS 代理。

用法：
  python fetch_data.py          # 抓取近200期
  python fetch_data.py 500      # 抓取近500期
"""
import sys
import json
import urllib.request
import urllib.error

URL = ('https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/'
       'findDrawNotice?name=3d&pageNo=1&pageSize={n}&systemType=PC')

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/120.0.0.0 Safari/537.36'),
    'Referer': 'https://www.cwl.gov.cn/ygkj/fc3d/kjgg/',
    'Accept': 'application/json, text/plain, */*',
}


def fetch(n):
    url = URL.format(n=n)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read().decode('utf-8')
    return json.loads(data)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    print('Fetching {} issues from cwl.gov.cn ...'.format(n))
    try:
        obj = fetch(n)
    except Exception as e:
        print('抓取失败：', e)
        sys.exit(1)
    if not obj or not isinstance(obj.get('result'), list):
        print('返回格式异常：', obj)
        sys.exit(2)
    out = []
    for item in obj['result']:
        period = str(item.get('code', '')).strip()
        red = str(item.get('red', '')).replace(',', '').strip()
        date = str(item.get('date', '')).strip()
        if not period or not red.isdigit() or len(red) != 3:
            continue
        out.append({'period': period, 'num': red, 'date': date})
    # 升序排序
    out.sort(key=lambda x: x['period'])
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    # 同时生成 data.js（HTML 用 <script src> 加载，避免 file:// 下 fetch CORS 限制）
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write('window.LOCAL_DATA=')
        json.dump(out, f, ensure_ascii=False)
        f.write(';')
    print('OK：保存 {} 条到 data.json 和 data.js'.format(len(out)))
    if out:
        print('  最早：{} {} {}'.format(out[0]['period'], out[0]['num'], out[0]['date']))
        print('  最新：{} {} {}'.format(out[-1]['period'], out[-1]['num'], out[-1]['date']))


if __name__ == '__main__':
    main()
