import re
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class TextFormatter:
    BOLD_COLORS = {
        'user': '#1a1a1a',
        'ai': '#00ffff',
        'ai_alt': '#ff6b6b',
        'ai_accent': '#4ecdc4',
        'ai_warning': '#ffd93d',
    }
    
    @staticmethod
    def format_message_content(content, sender='ai', use_html=True):
        if not content or not isinstance(content, str):
            return content
        
        if not use_html:
            return re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        
        if sender == 'user':
            bold_color = TextFormatter.BOLD_COLORS['user']
            bold_weight = 'bold'
        else:
            bold_color = TextFormatter.BOLD_COLORS['ai']
            bold_weight = 'bold'
        
        def replace_bold(match):
            text = match.group(1)
            return f'<span style="color: {bold_color}; font-weight: {bold_weight};">{text}</span>'
        
        formatted_content = re.sub(r'\*\*(.*?)\*\*', replace_bold, content)
        
        formatted_content = formatted_content.replace('\n', '<br>')
        
        return formatted_content
    
    @staticmethod
    def format_with_multiple_styles(content, sender='ai'):
        if not content or not isinstance(content, str):
            return content
        
        if sender == 'user':
            bold_color = TextFormatter.BOLD_COLORS['user']
            base_color = '#1a1a1a'
        else:
            bold_color = TextFormatter.BOLD_COLORS['ai']
            base_color = '#ffffff'
        
        formatted_content = content
        
        def replace_bold(match):
            text = match.group(1)
            return f'<span style="color: {bold_color}; font-weight: bold; font-size: 110%;">{text}</span>'
        
        formatted_content = re.sub(r'\*\*(.*?)\*\*', replace_bold, formatted_content)
        
        def replace_italic(match):
            text = match.group(1)
            return f'<span style="font-style: italic; color: {base_color}; opacity: 0.9;">{text}</span>'
        
        formatted_content = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', replace_italic, formatted_content)
        
        formatted_content = formatted_content.replace('\n', '<br>')
        
        return formatted_content
    
    @staticmethod
    def format_code_blocks(content):
        if not content or not isinstance(content, str):
            return content
        
        def replace_code_block(match):
            code = match.group(1).strip()
            import hashlib
            code_id = hashlib.md5(code.encode()).hexdigest()[:8]
            
            return f'''<div style="
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
                border: 2px solid rgba(0, 245, 255, 0.4);
                border-radius: 12px; 
                padding: 12px 16px; 
                margin: 8px 0; 
                font-family: 'Consolas', 'Fira Code', 'Monaco', monospace; 
                font-size: 14px;
                color: #e8f4fd;
                white-space: pre-wrap;
                position: relative;
                box-shadow: 0 4px 15px rgba(0, 245, 255, 0.1);
            " data-code-id="{code_id}">
                <div style="
                    position: absolute;
                    top: 8px;
                    right: 12px;
                    background: rgba(0, 245, 255, 0.1);
                    border: 1px solid rgba(0, 245, 255, 0.3);
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-size: 11px;
                    color: #00f5ff;
                    cursor: pointer;
                    user-select: none;
                " onclick="copyCodeBlock('{code_id}')">📋 Copy</div>
                <div style="margin-top: 20px;">{code}</div>
            </div>'''
        
        def replace_inline_code(match):
            code = match.group(1)
            return f'''<code style="
                background: linear-gradient(135deg, #2a2a3e 0%, #1e1e3f 100%); 
                border: 1px solid rgba(0, 245, 255, 0.2);
                padding: 3px 6px; 
                border-radius: 6px; 
                font-family: 'Consolas', 'Fira Code', monospace; 
                font-size: 13px;
                color: #00ff88;
                box-shadow: 0 2px 8px rgba(0, 245, 255, 0.05);
            ">{code}</code>'''
        
        formatted_content = content
        
        formatted_content = re.sub(r'```(?:python|js|javascript|html|css|sql|json|xml|yaml|bash|shell|cmd)?\s*(.*?)```', replace_code_block, formatted_content, flags=re.DOTALL)
        
        formatted_content = re.sub(r'`([^`]+)`', replace_inline_code, formatted_content)
        
        return formatted_content
    
    @staticmethod
    def format_comprehensive(content, sender='ai'):
        if not content or not isinstance(content, str):
            return content
        
        formatted_content = TextFormatter.format_code_blocks(content)
        
        formatted_content = TextFormatter.format_with_multiple_styles(formatted_content, sender)
        
        return formatted_content

    @staticmethod
    def strip_formatting(content):
        if not content or not isinstance(content, str):
            return content
        
        plain_text = content
        plain_text = re.sub(r'\*\*(.*?)\*\*', r'\1', plain_text)
        plain_text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', plain_text)
        plain_text = re.sub(r'```(.*?)```', r'\1', plain_text, flags=re.DOTALL)
        plain_text = re.sub(r'`([^`]+)`', r'\1', plain_text)
        
        return plain_text

if __name__ == "__main__":
    test_content = """
    Hello! Here are some **important points** to consider:
    
    1. **Security**: Always wear gloves when handling sensitive materials
    2. **Privacy**: Use *encrypted* communication channels
    3. **Code Example**: Here's a simple function:
    ```python
    def secure_function():
        return "encrypted_data"
    ```
    
    Remember: **Stay safe** and use `proper protocols` at all times!
    """
    
    print("Original content:")
    print(test_content)
    print("\n" + "="*50 + "\n")
    
    print("Formatted for AI message:")
    formatted = TextFormatter.format_comprehensive(test_content, 'ai')
    print(formatted)
    print("\n" + "="*50 + "\n")
    
    print("Formatted for User message:")
    formatted_user = TextFormatter.format_comprehensive(test_content, 'user')
    print(formatted_user)
    print("\n" + "="*50 + "\n")
    
    print("Plain text (no formatting):")
    plain = TextFormatter.strip_formatting(test_content)
    print(plain)