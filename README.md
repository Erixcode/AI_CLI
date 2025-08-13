# AI_CLI
Use AI in your Terminal Localy

This is modification from my ChatGPT_Linux_Terminal but with modification to use any LLM localy, since you may face internet issue like no
coverage or like me 12day war ending up have no internet, you can have your AI assistance with you all the time privately, or maybe you are
in Environment where you cannot have internet access for your workspace or you have privacy concerns, this approach is a nice solution.
in this model I used deepseek 1.5b which is compatible with my laptop, if you have better hardware, you can go with different model.

✅ Benefits of This Approach

    No API calls → Fully offline.

    No FastAPI server overhead → Runs in-process.

    Privacy → everything stays on your hardware.

    GPU-accelerated if available → Falls back to CPU.

🚀 How to Use

    Place your model in ../models/deepseek-coder-1.3b-base (or update MODEL_PATH).

    Run your CLI as usual:
    
  <code> python ai.py </code>

    The first query will load the model (may take ~10-30s).

    Subsequent queries will be fast.

🔧 Requirements:<br>

  <code>  pip install torch transformers </code>
