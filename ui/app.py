import chainlit as cl
import requests
import json

# Backend URL
API_URL = "http://localhost:8000/chat"

@cl.on_chat_start
async def start():
    await cl.Message(
        content="👋 **Enterprise API Assistant** is ready!\n\nI can help you:\n1. Find API documentation locally.\n2. Create an implementation plan.\n3. Generate Python/Node.js code."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # Call the Backend API
    try:
        payload = {"query": message.content}
        
        # Stream "Thinking" status
        msg = cl.Message(content="")
        await msg.send()
        
        # Send Request
        response = requests.post(API_URL, json=payload, stream=False)
        
        if response.status_code == 200:
            data = response.json()
            
            plan = data.get("plan", "No plan generated.")
            code = data.get("response", "# No code generated.")
            context = data.get("context", [])
            
            # 1. Show the Plan (Reasoning)
            async with cl.Step(name="Architect Plan", type="run") as step:
                step.output = plan
            
            # 2. Show the Sources
            if context:
                source_text = "\n".join([f"- {doc[:100]}..." for doc in context[:3]])
                async with cl.Step(name="Retrieved Context", type="tool") as step:
                    step.output = source_text
            
            # 3. Final Code Output
            msg.content = f"""
### 🏗️ Implementation Plan
{plan}

### 💻 Generated Code
```python
{code}
```
"""
            await msg.update()
            
        else:
            await cl.Message(content=f"❌ Error: Backend returned {response.status_code}").send()
            
    except Exception as e:
        await cl.Message(content=f"❌ Connection Error: Is the backend running on port 8000? \nDetails: {str(e)}").send()
