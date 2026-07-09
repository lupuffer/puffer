import zipfile, sys, re
sys.stdout.reconfigure(encoding='utf-8')
c = zipfile.ZipFile('d:\\3240106033\\3240106033\\简历模板_copy.docx','r').read('word/document.xml').decode('utf-8')

# 查找科技大学在XML中的上下文
idx = c.find('科技大学')
print('=== 科技大学上下文 ===')
print(repr(c[max(0,idx-200):min(len(c),idx+200)]))
print()

# 查找2009.03在XML中的上下文
idx2 = c.find('2009.03')
print('=== 2009.03上下文 ===')
print(repr(c[max(0,idx2-200):min(len(c),idx2+200)]))
print()

# 查找五百丁在XML中的上下文
idx3 = c.find('五百丁')
print('=== 五百丁上下文 ===')
print(repr(c[max(0,idx3-200):min(len(c),idx3+200)]))
print()

# 查找2010.03在XML中的上下文
idx4 = c.find('2010.03')
print('=== 2010.03上下文 ===')
print(repr(c[max(0,idx4-200):min(len(c),idx4+200)]))
