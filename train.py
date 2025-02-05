import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

# Load dataset
dataset = load_dataset("imdb")
train_data = dataset["train"].shuffle(seed=42).select(range(1000))  # Small subset
test_data = dataset["test"].shuffle(seed=42).select(range(500))  # Small subset

# Load tokenizer and model
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

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
    logging_dir="/mnt/app/logs",
    logging_steps=10,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=1,
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
with open("/mnt/ceph_rbd/test_accuracy.txt", "w") as f:
    f.write(f"Eval results: {eval_results}\n")
