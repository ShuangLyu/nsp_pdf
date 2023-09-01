import copy
from test_nsp import is_nextsent
import re

#句子末尾遇到下述这些字符的时候代表本句子是断掉的，去掉末尾的"\n"
unstop = r"，|：|、|/|¥|（|《|<|\{|\["

#下面这些是属于标题的标识符，当前行遇到的下一句头部包含这些标识符，不去掉本句话的“\n"，代表着下一行是可以另起一行的
combined_pattern = (
    r'^第[一二三四五六七八九十0123456789]+章|'                     
    r'^附件[一二三四五六七八九十0123456789]|合同附件|劳动合同续订书|劳动合同变更书|'  
    r'^第[1234567890一二三四五六七八九十]+条+( |、|\.|\t|\s+|:|：|．|[\u4e00-\u9fa5])|'  
    r'^[一二三四五六七八九十]+( |、|\.|\t|\s+|:|：|．)|'                             
    r'^(\(|（)[一二三四五六七八九十]+(\)|）)|'                                    
    r'^[0-9]+(\t| |、|\s+)|'                                                     
    r'\d+(\.|．|\-)\d+(?=[^(\.|．|\-)+\d]+)|'                                     
    r'\d+(\.|．)+(\t| |、|[\u4e00-\u9fa5]|\s+)|'                                
    r'^(\(|（)[0-9]+(\)|）)|'                                                    
    r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]+'
)

#需要转换的pdf，事先用pdfminer读出来存储了
with open("./test_nsp.txt","r",encoding="utf-8") as f:
    datasets = f.readlines()

#判断该句话是否可以用来生成max_len，去除包含字母和数字的文本段，因为数字和字母的文本段会影响max_len
def check_string(s):
    pattern = r'^[^a-zA-Z0-9]*$'
    return bool(re.fullmatch(pattern, s))

article = ""
docs = []
max_len = 0
for i in datasets:
    if len(i.replace(" ",""))>max_len and check_string(i):
        max_len = copy.deepcopy(len(i))
    if len(i.replace("\n",""))>0:
        docs.append(i.replace(" ", ""))

#使用规则+bert
for index,item in enumerate(docs):
    print(item)
    if index <= len(docs)-2 and len(item.replace("\n",""))>0:
        #默认小于文本段的3/4且不包含unstop字符的，不需要去除文末的“\n”
        if len(item) <= 0.75*max_len and not re.findall(unstop,item[-2]):
            article += item
        else:
            if (re.findall(unstop,item[-2]) or is_nextsent(item,docs[index+1])) and \
                    not bool(re.findall(combined_pattern,docs[index+1][:4])):
                article += item.replace("\n","")
            else:
                article += item
    else:
        article += item
#不使用规则,仅仅使用bert的NSP
# for index,item in enumerate(docs):
#     if index <= len(datasets)-2 and len(item.replace("\n",""))>0:
#         if is_nextsent(item,datasets[index+1]):
#             article += item.replace("\n","")
#         else:
#             article += item

#保存结果
with open("./result.txt","w",encoding="utf-8") as f:
    for j in article:
        f.write(j)


