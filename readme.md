# 🤖 Multi-Tool Agent with Google ADK 🚀

Welcome to this **multi-agent test project** built using the powerful **Google AI Developer Kit (ADK)**!

## 🔍 Overview

This repo demonstrates a **multi-tool conversational agent** setup leveraging Google ADK’s APIs. It combines multiple AI agents with guardrails, showcasing:

- Stateful session management 🧠  
- Input filtering and safety guardrails 🚦  
- Async conversational flows with custom tools ⚙️  
- Integration with Google’s LLM APIs via ADK client 📡  

It’s a playground to experiment with **advanced AI orchestration** and **safe agent workflows**.

## 🎯 Key Features

- Multi-agent architecture with a root agent coordinating sub-agents 🤝  
- Guardrails to control and filter model inputs 🛡️  
- Stateful sessions to keep context across turns 🔄  
- Built on Google ADK’s Runner and agent APIs 🏃‍♂️  
- Async interface for smooth, real-time interactions ⏳  

## ⚙️ Configuration

The AI model used is defined in `config.py` as:
```MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"```

You can easily swap this out for any other supported AI model to suit your needs! 🔄

## 🚀 How to Run

Make sure you have your Google API credentials set up in your environment variables. Then simply run:


This command launches the main async flow demonstrating multi-agent conversations with stateful sessions and guardrails.
___
This is a **test and demo project** exploring:

- Google ADK capabilities  
- Multi-agent AI systems  
- Conversational AI with guardrails and state  
- Safe and modular AI workflows  