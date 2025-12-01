'''
Initialization the connection to the Gemini API and defines the default model configuration for all agents in this project.

Load API credentials from the environment (e.g. Kaggle Secrets) into a GOOGLE_API_KEY variable.
This keeps the notebook secure: the key is never hard-coded and is not exposed in the output.
Configure the google-genai client using that key, so that subsequent calls to Gemini models are authenticated and routed correctly.
Set default model settings
'''
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from kaggle_secrets import UserSecretsClient
from IPython.display import display, HTML, clear_output

from kaggle_secrets import UserSecretsClient

import warnings
warnings.filterwarnings('ignore')


KAGGLE_SECRET_NAME = "GOOGLE_API_KEY"
# Setup your own key in "Add-ons" -> "Secrets" -> "Add Secret"
user_secrets = UserSecretsClient()
api_key = user_secrets.get_secret(KAGGLE_SECRET_NAME)
if not api_key:
    raise RuntimeError(f"Secret {KAGGLE_SECRET_NAME} is empty or not available right now")
os.environ["GOOGLE_API_KEY"] = api_key
print("GOOGLE_API_KEY set:", bool(os.environ.get("GOOGLE_API_KEY")))

model = "gemini-2.5-flash"
# Also i used a lot of times "gemini-2.0-flash" , "gemini-2.5-pro-preview-06-05" , "gemini-2.5-flash" , "gemini-2.5-flash-lite" 

# # Shows a list of Models available for your tier
# from google import genai
# client = genai.Client(api_key=api_key)
# for m in client.models.list():
#     print(m.name, m.supported_actions)

print("✔️ Libraries installed!")
