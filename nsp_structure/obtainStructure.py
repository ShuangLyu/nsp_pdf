import copy
from bert_nsp import is_nextsent
import re
from collections import defaultdict

# 句子末尾遇到下述这些字符的时候代表本句子是断掉的，去掉末尾的"\n"
unstop = r"，|：|、|/|¥|（|《|<|\{|\["
##去掉无关字符
space_patt = r"\s+| |_|　|□||＿|"

# 分句子的token
split_token = r"。|；|;|！"

# 下面这些是属于标题的标识符，当前行遇到的下一句头部包含这些标识符，不去掉本句话的“\n"，代表着下一行是可以另起一行的
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


class Contract_Structure():

    def __init__(self):
        self.sentence_set = []
        self.correct_article = ""
        self.native_docs = []
        self.max_len = 0  # 最长的语句的字符长度，不计算数字和英文

    # 判断该句话是否可以用来生成max_len，去除包含字母和数字的文本段，因为数字和字母的文本段会影响max_len
    def check_string(self, s):
        pattern = r'^[^a-zA-Z0-9]*$'
        return bool(re.fullmatch(pattern, s))

    # 去掉无关的字符得到原生的docx，并计算行中字符数量最多的是多大
    def pre_processing(self, datasets):
        '''
        :param datasets: 后端传入的数据
        :return:
        '''
        for i in datasets:
            i = re.sub(space_patt, "", i)
            if len(i) > self.max_len and self.check_string(i):
                self.max_len = copy.deepcopy(len(i))
            if len(i) > 0:
                self.native_docs.append(i)

    def rulesAndBert(self, datasets):
        self.pre_processing(datasets)
        sentence_set = []
        tmp_index = []
        tmp_str = ''
        # 使用规则+bert
        for index, item in enumerate(self.native_docs):
            item = re.sub(space_patt, "", item)
            if index <= len(self.native_docs) - 2 and len(item.replace("\n", "")) >= 1:
                # 默认小于文本段的3/4且不包含unstop字符的，不需要去除文末的“\n”
                if len(item) <= 0.5 * self.max_len and not re.findall(unstop, item[-1]):
                    self.correct_article += item
                    if tmp_index:
                        tmp_str += item.replace("\n", "")
                        tmp_index.append(index)
                        sentence_set.append([tmp_str, tmp_index])
                        tmp_index = []
                        tmp_str = ''
                    else:
                        sentence_set.append([item, [index]])
                else:
                    if (re.findall(unstop, item[-2]) or is_nextsent(item, self.native_docs[index + 1])) and \
                            not bool(re.findall(combined_pattern, self.native_docs[index + 1][:4])):
                        self.correct_article += item.replace("\n", "")

                        tmp_str += item.replace("\n", "")
                        tmp_index.append(index)
                    else:
                        self.correct_article += item
                        if tmp_index:
                            tmp_str += item.replace("\n", "")
                            tmp_index.append(index)
                            sentence_set.append([tmp_str, tmp_index])

                            tmp_index = []
                            tmp_str = ''
                        else:
                            sentence_set.append([item, [index]])
            else:
                self.correct_article += item
                if tmp_index:
                    tmp_str += item.replace("\n", "")
                    tmp_index.append(index)
                    sentence_set.append([tmp_str, tmp_index])
                    tmp_index = []
                    tmp_str = ''
                else:
                    sentence_set.append([item, [index]])

        para_key = defaultdict(list)
        if sentence_set:
            for sentence in sentence_set:
                for item in re.split(split_token, sentence[0].replace("\n", "")):
                    if item:
                        para_key[item].append(sentence[-1])
            return para_key
        else:
            return None

if __name__ == '__main__':

    with open("./../test_nsp.txt", "r", encoding="utf-8") as f:
        datasets = f.readlines()
    cs = Contract_Structure()
    for k,v in cs.rulesAndBert(datasets).items():
        print(k,v)