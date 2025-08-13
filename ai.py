#!/usr/bin/env python3
import os
import curses
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# Disable all warnings
logging.disable(logging.WARNING)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

# Configuration
MODEL_PATH = "../deepseek-coder-1.3b-base"
MAX_TOKENS = 15000

# Model Setup
tokenizer = None
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model():
    global tokenizer, model
    if model is None:
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(device)
        except Exception as e:
            raise Exception(f"Failed to load model: {e}")
def get_response(messages):
    load_model()
    
    # Format conversation history clearly
    conversation = []
    for msg in messages:
        if msg['role'] == 'user':
            conversation.append(f"USER: {msg['content']}")
        elif msg['role'] == 'assistant':
            conversation.append(f"ASSISTANT: {msg['content']}")
    
    # Create the prompt with clear boundaries
    prompt = "\n".join(conversation) + "\nASSISTANT:"
    
    with torch.no_grad():
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_TOKENS,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
    
    # Extract and clean the response
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Isolate only the new assistant response
    response = full_response[len(prompt):].split("USER:")[0].strip()
    
    # Additional cleaning to remove any remaining artifacts
    response = response.replace("ASSISTANT:", "").strip()
    response = response.split('\n')[0].strip()
    
    return response if response else "I don't have a response for that."


def safe_addstr(win, y, x, text, attr=0):
    """Safely add string with boundary checking"""
    max_y, max_x = win.getmaxyx()
    if y >= max_y or x >= max_x:
        return
    text = text[:max_x - x - 1]
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass

def main():
    # Initialize chat
    command_mode = False
    history = []
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    # Curses setup
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)
    
    # Color Scheme
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Header
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)     # User
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # AI
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Status
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Prompt
    
    HEADER_COLOR = curses.color_pair(1) | curses.A_BOLD
    USER_COLOR = curses.color_pair(2) | curses.A_BOLD
    AI_COLOR = curses.color_pair(3) | curses.A_BOLD
    STATUS_COLOR = curses.color_pair(4)
    PROMPT_COLOR = curses.color_pair(5)
    
    def draw_interface(prompt, scroll_offset=0):
        rows, cols = stdscr.getmaxyx()
        stdscr.erase()
        
        # Header
        safe_addstr(stdscr, 0, 0, " " * cols, HEADER_COLOR)
        header = " DEEPSEEK CONSOLE "
        safe_addstr(stdscr, 0, (cols - len(header)) // 2, header, HEADER_COLOR)
        
        # Message history
        visible_lines = rows - 4
        start_idx = max(0, len(history) - visible_lines - scroll_offset)
        
        for i, line in enumerate(history[start_idx:start_idx + visible_lines]):
            if i >= visible_lines:
                break
            if line.startswith("You:"):
                safe_addstr(stdscr, i+1, 0, line, USER_COLOR)
            else:
                safe_addstr(stdscr, i+1, 0, line, AI_COLOR)
        
        # Status bar
        mode = "COMMAND" if command_mode else "INSERT"
        status = f" {mode} MODE ".center(cols//2) + "| ↑/↓:Scroll | :h = Help "
        safe_addstr(stdscr, rows-2, 0, "─" * cols, STATUS_COLOR)
        safe_addstr(stdscr, rows-2, 0, status, STATUS_COLOR)
        
        # Prompt area
        prompt_line = "/>" + prompt if command_mode else "You: " + prompt
        safe_addstr(stdscr, rows-1, 0, " " * cols, PROMPT_COLOR)
        safe_addstr(stdscr, rows-1, 0, prompt_line, PROMPT_COLOR)
        
        stdscr.refresh()
    
    # Main interaction loop
    prompt = ""
    scroll_offset = 0
    
    try:
        while True:
            draw_interface(prompt, scroll_offset)
            c = stdscr.getch()
            
            # Navigation
            if c == curses.KEY_UP:
                scroll_offset = min(len(history), scroll_offset + 1)
            elif c == curses.KEY_DOWN:
                scroll_offset = max(0, scroll_offset - 1)
            elif c == curses.KEY_PPAGE:
                scroll_offset = min(len(history), scroll_offset + 10)
            elif c == curses.KEY_NPAGE:
                scroll_offset = max(0, scroll_offset - 10)
            
            # Mode switching
            elif c == 27:  # ESC
                command_mode = not command_mode
                prompt = ""
            
            # Command mode
            elif command_mode:
                if c == ord('\n'):
                    if prompt == ":q" or prompt == ":quit":
                        break
                    elif prompt == ":c" or prompt == ":clear":
                        history = []
                        messages = [{"role": "system", "content": "You are a helpful assistant."}]
                    elif prompt == ":h" or prompt == ":help":
                        history.append(
                            "AI: Vim-style commands available:\n"
                            "  :i /  Esc   - Insert mode\n"
                            "  :q / :quit  - Quit\n"
                            "  :c / :clear - Clear chat\n"
                            "  :h / :help  - This help\n"
                                        )
                    elif prompt == ":i":
                        command_mode = False
                    prompt = ""
                elif c == curses.KEY_BACKSPACE:
                    prompt = prompt[:-1]
                elif 32 <= c <= 126:
                    prompt += chr(c)
            
            # Insert mode
            else:
                if c == ord('\n'):
                    if prompt.strip():
                        messages.append({"role": "user", "content": prompt})
                        history.append(f"You: {prompt}")
                        
                        # Get AI response
                        draw_interface(prompt, scroll_offset)
                        safe_addstr(stdscr, len(history)+1, 0, "AI: thinking...", AI_COLOR)
                        stdscr.refresh()
                        
                        response = get_response(messages)
                        messages.append({"role": "assistant", "content": response})
                        history.append(f"AI: {response}")
                        
                        scroll_offset = 0
                    prompt = ""
                elif c == curses.KEY_BACKSPACE:
                    prompt = prompt[:-1]
                elif 32 <= c <= 126:
                    prompt += chr(c)
    
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == '__main__':
    main()
