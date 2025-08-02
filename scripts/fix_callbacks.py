#!/usr/bin/env python3
"""
Script to replace bot.answer_callback_query with safe_answer_callback_query
"""

import re
import os
import glob

def fix_callback_queries(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if safe_answer_callback_query is already imported
    if 'safe_answer_callback_query' not in content:
        # Add import if not present
        if 'from src.utils.helpers import' in content:
            content = re.sub(
                r'(from src\.utils\.helpers import[^)]+)',
                r'\1, safe_answer_callback_query',
                content
            )
        else:
            # Add new import line
            import_line = "from src.utils.helpers import safe_answer_callback_query\n"
            content = import_line + content
    
    # Replace bot.answer_callback_query(call.id, with safe_answer_callback_query(bot, call.id,
    content = re.sub(
        r'bot\.answer_callback_query\(call\.id,',
        'safe_answer_callback_query(bot, call.id,',
        content
    )
    
    # Replace bot.answer_callback_query(call.id) with safe_answer_callback_query(bot, call.id)
    content = re.sub(
        r'bot\.answer_callback_query\(call\.id\)',
        'safe_answer_callback_query(bot, call.id)',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed callback queries in {file_path}")

if __name__ == "__main__":
    # Fix all handler files
    handler_files = glob.glob("src/handlers/*.py")
    for file_path in handler_files:
        if os.path.basename(file_path) != '__init__.py':
            fix_callback_queries(file_path)
