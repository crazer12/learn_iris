# -*- coding: utf-8 -*-
"""iriska_v2.0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/159HIgJZYbaFONXNJlk5bHDxLFj3DhbQ1
"""

!pip install transformers datasets

from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch

from google.colab import drive
drive.mount('/content/gdrive')

# Загрузка предобученной модели и токенизатора
model_name = "gpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Проверка параметров токенизатора
tokenizer.pad_token = tokenizer.eos_token

dataset = load_dataset('json', data_files='/content/gdrive/MyDrive/iris/model_train/dialogues.json', )

def preprocess_function(examples):
    questions = examples['question']
    answers = examples['answer']
    model_inputs = tokenizer(questions, padding="max_length", truncation=True, max_length=128)
    print(model_inputs)

    # Добавление ответов в качестве целевых значений
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(answers, padding="max_length", truncation=True, max_length=128)

    model_inputs['labels'] = labels['input_ids']
    return model_inputs

# Применение токенизации к датасету
tokenized_dataset = dataset.map(preprocess_function, batched=True)

training_args = TrainingArguments(
    output_dir='/content/gdrive/MyDrive/iris/model_train/results',
    overwrite_output_dir=True,
    num_train_epochs=500,
    per_device_train_batch_size=8,
    save_total_limit=2,
    save_steps=5_000,
    logging_dir='/content/gdrive/MyDrive/iris/model_train/logs',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    tokenizer=tokenizer,
)

trainer.train(resume_from_checkpoint=True)

trainer.save_model("/content/gdrive/MyDrive/iris/model_train/iris_model")
tokenizer.save_pretrained("/content/gdrive/MyDrive/iris/model_train/iris_model")

# Загрузка обученной модели
model = AutoModelForCausalLM.from_pretrained("/content/gdrive/MyDrive/iris/model_train/iris_model")
tokenizer = AutoTokenizer.from_pretrained("/content/gdrive/MyDrive/iris/model_train/iris_model")

# Тестовый запрос
input_text = "Привет"

# Токенизация входного текста
inputs = tokenizer(input_text, return_tensors="pt")

# Генерация ответа
output = model.generate(inputs['input_ids'], max_length=100, pad_token_id=tokenizer.eos_token_id)

# Декодирование ответа
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

print(generated_text)