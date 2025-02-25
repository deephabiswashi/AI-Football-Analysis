from transformers import pipeline

# Load a pre-trained text classifier. Here we use a DistilBERT-based classifier.
llm_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def classify_output(text_summary):
    """
    Classify the output summary generated from object detection and tracking data.
    """
    classification = llm_classifier(text_summary)
    return classification
