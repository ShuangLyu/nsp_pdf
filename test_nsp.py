from transformers import BertForNextSentencePrediction, BertTokenizer
import torch


# 加载字典和分词工具，即tokenizer
tokenizer = BertTokenizer.from_pretrained(r'E:\LLM的模型\bert-base-chinese')
# 加载预训练模型
model = BertForNextSentencePrediction.from_pretrained(r'E:\LLM的模型\bert-base-chinese')



MERGE_RATIO = 0.9   # 阈值分数（自定义）
TEMPERATURE = 3  # 温度函数 自定义

def is_nextsent(sent, next_sent):
    encoding = tokenizer(sent, next_sent, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**encoding, labels=torch.LongTensor([1]))
        logits = outputs.logits
        probs = torch.softmax(logits / TEMPERATURE, dim=1)
        next_sentence_prob = probs[:, 0].item()  # 类别 0 是 "IsNext" 类别
    # print(next_sentence_prob)
    if next_sentence_prob >= MERGE_RATIO:
        return True
    else:
        return False

# # # 示例用法
# sent1 = "合计人民币总金额（大写）："
# sent2 = "贰万壹仟柒佰陆拾捌元整"
#
# result = is_nextsent(sent1, sent2)
# print(result)