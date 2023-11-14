from transformers import BertForNextSentencePrediction, BertTokenizer
import torch


# 加载字典和分词工具，即tokenizer
tokenizer = BertTokenizer.from_pretrained(r'E:\LLM的模型\bert-base-chinese')
# 加载预训练模型
model = BertForNextSentencePrediction.from_pretrained(r'E:\LLM的模型\bert-base-chinese')



MERGE_RATIO = 0.9  # 阈值分数（自定义）
TEMPERATURE = 3  # 温度函数 自定义

def is_nextsent(sent, next_sent):
    encoding = tokenizer(sent, next_sent, return_tensors="pt", truncation=True, padding=True,max_length=512)
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
sent1 = "本合同中约定的附件与本合同具有同等法律效力，如有。"
sent2 = "第十一条合同签订及期限"

result = is_nextsent(sent1, sent2)
print(result)