#!/usr/bin/env python3
import aws_cdk as cdk
from summarize_csv_service.summarize_csv_service_stack import SummarizeCsvServiceStack

app = cdk.App()
SummarizeCsvServiceStack(app, "SummarizeCsvServiceStack")
app.synth()
