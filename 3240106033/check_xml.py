import zipfile, sys, re
sys.stdout.reconfigure(encoding='utf-8')
c = zipfile.ZipFile('d:\\3240106033\\3240106033\\简历模板_copy.docx','r').read('word/document.xml').decode('utf-8')

keywords = ['13500', 'service', '海珠', '1996', '177', '党员', '04-至今', '广州信息', '广州', '本科', '2005', '2009', '2010']
for kw in keywords:
    idx = c.find(kw)
    if idx >= 0:
        start = max(0, idx-300)
        end = min(len(c), idx+300)
        snippet = c[start:end]
        print(f'=== 找到 "{kw}" ===')
        print(snippet)
        print()
    else:
        print(f'=== 未找到 "{kw}" ===')
        print()
