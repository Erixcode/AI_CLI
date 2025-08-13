# AI_CLI
Use AI in your Terminal Localy

This is modification from my ChatGPT_Linux_Terminal but with modification to use any LLM localy, since you may face internet issue like no
coverage or like me 12days war ended up having no internet, you can have your AI assistance with you all the time privately, or maybe you are
in Environment where you cannot have internet access for your workspace or you have privacy concerns, this approach is a nice solution.
here I used deepseek 1.3b which is compatible with my laptop, if you have better hardware, you can go with different model.

there is lot's of solutions, like Ollama(which is not available for me) or LM Studio, but I leave in Terminal and don't want to use browser :)

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

GPU users: Add --fp16 to halve memory usage (edit load_model()).
When to Use FP16

✅ Recommended if:

    You have a GPU with limited VRAM (e.g., 8GB or less).

    You want faster inference (especially for larger models like 1.5B+).

❌ Avoid if:

    You need maximum accuracy (e.g., for code generation where exact syntax matters).

    You’re already running smoothly in full precision.

🔧 Installation:<br>

  <code>  pip install torch transformers </code>
  edit your LLM path inside the code line 13
