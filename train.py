import argparse
import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

def get_arg_or_env(arg_name, env_name, default, arg_type=str):
    env_value = os.getenv(env_name)
    if env_value is not None:
        return arg_type(env_value)
    return default

parser = argparse.ArgumentParser(description="Train a HuggingFace model")

parser.add_argument(
    "--model",
    type=str,
    default=get_arg_or_env("model", "MODEL", "bert-base-uncased"),
    help="Name of the model"
)

parser.add_argument(
    "--epochs",
    type=int,
    default=get_arg_or_env("epochs", "EPOCHS", 3, int),
    help="Number of epochs"
)

parser.add_argument(
    "--lr",
    type=float,
    default=get_arg_or_env("lr", "LR", 5e-5, float),
    help="Learning rate"
)

args = parser.parse_args()

# Load dataset
dataset = load_dataset("imdb")
train_data = dataset["train"].shuffle(seed=42).select(range(1000))  # Small subset
test_data = dataset["test"].shuffle(seed=42).select(range(500))  # Small subset

# Load tokenizer and model
# model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(args.model)
model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=2)

# Tokenize data
def preprocess(examples):
    return tokenizer(examples["text"], truncation=True, padding=True, max_length=512)

train_data = train_data.map(preprocess, batched=True)
test_data = test_data.map(preprocess, batched=True)

# Define Trainer
training_args = TrainingArguments(
    output_dir="/mnt/app",
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=1,
    logging_dir="/mnt/app/logs",
    logging_steps=10,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=args.epochs,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data,
    eval_dataset=test_data,
    tokenizer=tokenizer,
)

# Train and evaluate
trainer.train()
eval_results = trainer.evaluate()
print("Evaluation results:", eval_results)

# Save accuracy to file
with open("/mnt/app/test_accuracy.txt", "w") as f:
    f.write(f"Eval results: {eval_results}\n")
