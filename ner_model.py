import os
import pandas as pd
import numpy as np
from tqdm import tqdm

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import Trainer

import json
import re
import emoji
from soynlp.normalizer import repeat_normalize


# 태깅 예측을 위한 기본 데이터
# labels_info = [label.strip() for label in open('/home/sol4/workspace/seokho/ner_label.txt', 'r', encoding='utf-8 ')]
# tag_to_index = {tag: index for index, tag in enumerate(labels_info)}
# index_to_tag = {index: tag for index, tag in enumerate(labels_info)}

with open('/home/sol4/workspace/seokho/final/all_ner_tags_tag2id.json', 'r') as f:
    tag_to_index = json.load(f)
with open('/home/sol4/workspace/seokho/final/all_ner_tags_id2tag.json', 'r') as f:
    index_to_tag = json.load(f)


# 토크나이저, 훈련모델 가져오기
TOKENIZER_PATH = "beomi/KcELECTRA-base-v2022"
BEST_MODEL_PATH = '/home/sol4/workspace/seokho/final/results/checkpoint-8000'
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
model = AutoModelForTokenClassification.from_pretrained(BEST_MODEL_PATH)
device = torch.device('cuda:0')
model.to(device)

# torch모델에 넣기 위한 데이터셋 형태로 변환해주는 클래스
class TokenDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encoding = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key : torch.tensor(val) for key, val in self.encoding[idx].items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)
    
# 손실함수를 따로 정의해줄 필요가 있어서 기본 트레이너에서 손실함수만 수정한 부분
class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")

        loss_fn = torch.nn.CrossEntropyLoss().to(device = device)

        active_loss = torch.reshape(labels, (-1,)) != -100 
        tensor_size = active_loss.size()[0]
        active_logits_loss = active_loss.reshape(tensor_size, 1).expand(tensor_size, logits.size()[2])

        reduced_logits = torch.masked_select(torch.reshape(logits, (-1, logits.size()[2])), active_logits_loss)
        reduced_logits = reduced_logits.reshape(-1, logits.size()[2])
        labels = torch.masked_select(torch.reshape(labels, (-1,)), active_loss)

        loss = loss_fn(reduced_logits, labels)

        return (loss, outputs) if return_outputs else loss
    
# 훈련된 모델 트레이너에 부착
trainer = CustomTrainer(
    model = model
)

# BERT모델에 입력할 수 있게 데이터 형태 변환
def convert_examples_to_features_for_prediction(examples, max_seq_len, tokenizer, pad_token_id_for_segment=0, pad_token_id_for_label=-100):
    
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    pad_token_id = tokenizer.pad_token_id

    tokenizer_data, data_labels = [], []

    print(":::: START DATA CONVERTING::::")
    for example in tqdm(examples):
        tokens = []
        label_mask = []
        for one_word in example:

            subword_tokens = tokenizer.tokenize(one_word)
            tokens.extend(subword_tokens)

            label_mask.extend([0] + [pad_token_id_for_label] * (len(subword_tokens) -1)) 

        special_tokens_count = 2
        if len(tokens) > max_seq_len - special_tokens_count:
            tokens = tokens[:(max_seq_len - special_tokens_count)]
            label_mask = label_mask[:(max_seq_len - special_tokens_count)]

        tokens += [sep_token]
        label_mask += [pad_token_id_for_label]

        tokens = [cls_token] + tokens
        label_mask = [pad_token_id_for_label] + label_mask

        input_id = tokenizer.convert_tokens_to_ids(tokens)

        attention_mask = [1] * len(input_id)

        padding_count = max_seq_len - len(input_id)

        input_id = input_id + ([pad_token_id] * padding_count)
        attention_mask = attention_mask + ([0] * padding_count)

        token_type_id = [pad_token_id_for_segment] * max_seq_len

        label_mask = label_mask + ([pad_token_id_for_label] * padding_count)

        assert len(input_id) == max_seq_len, 'Error with input length {} vs {}'.format(len(input_id), max_seq_len)
        assert len(attention_mask) == max_seq_len, 'Error with input length {} vs {}'.format(len(attention_mask), max_seq_len)
        assert len(token_type_id) == max_seq_len, 'Error with input length {} vs {}'.format(len(token_type_id), max_seq_len)
        assert len(label_mask) == max_seq_len, 'Error with input length {} vs {}'.format(len(label_mask), max_seq_len)

        tokenizer_data.append({
        'input_ids' : input_id,
        'attention_mask' : attention_mask,
        'token_type_ids' : token_type_id
        })
        data_labels.append(label_mask)

    return tokenizer_data, data_labels



# 전처리 
pattern = re.compile(f'[^ ㄱ-ㅣ가-힣]+')

def clean(x): 
    x = pattern.sub(' ', x)
    x = emoji.replace_emoji(x, replace='') #emoji 삭제
    x = x.strip()
    x = repeat_normalize(x, num_repeats=2)
    return x

def preprocessing(txt):
    txt = clean(txt)
    txt = txt.split()
    return txt

def make_datas_to_pred(datas, tokenizer):
    datas = [preprocessing(data) for data in datas]
    input_data, label_data = convert_examples_to_features_for_prediction(datas, max_seq_len=128, tokenizer = tokenizer)
    input_data_set = TokenDataset(input_data, label_data)

    return input_data_set, input_data

def predict_process(datas, trainer, tokenizer):
    input_data_set, token_datas = make_datas_to_pred(datas, tokenizer)
    y_pred = trainer.predict(input_data_set)
    return y_pred, token_datas


def predict_ner(datas ):
    pred_text, pred_tag = [], []

    # 텍스트 단일 데이터면 리스트 형태로 변환
    if str == type(datas):
        datas = [datas]

    y_pred, token_datas = predict_process(datas, trainer, tokenizer)
    preds = np.argmax(y_pred.predictions, axis=-1)
    
    data_idx = 0
    for pred_labels, pred_pred in zip(y_pred.label_ids, preds):
        input_ids = token_datas[data_idx]['input_ids']
        tmp_tag =[]
        for idx in range(128):
            if pred_labels[idx] != -100:
                tmp_tag.append(index_to_tag[str(pred_pred[idx])])
        
            if input_ids[idx] == tokenizer.cls_token_id: start = idx+1
            if input_ids[idx] == tokenizer.sep_token_id: end = idx

        pred_tag.append(tmp_tag)
        pred_text.append(tokenizer.decode(input_ids[start:end]))
        data_idx+=1

        
    return pred_text, pred_tag