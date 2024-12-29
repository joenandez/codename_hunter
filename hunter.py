import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.markdown import Markdown
import pyperclip
import re
import os
from typing import Optional

def clean_text(text):
    """Clean text while preserving important formatting"""
    text = re.sub(r'_\d+', '', text)
    text = re.sub(r'#$', '', text.strip())
    # Preserve important whitespace but remove extra
    text = re.sub(r'\s+', ' ', text)
    # Ensure proper spacing around inline code
    text = re.sub(r'`(\S)', '` \\1', text)  # Add space after backtick if missing
    text = re.sub(r'(\S)`', '\\1 `', text)  # Add space before backtick if missing
    return text.strip()

def clean_code(text):
    """Clean code while preserving structure"""
    lines = text.splitlines()
    cleaned_lines = [re.sub(r'_\d+', '', line.rstrip()) for line in lines]
    # Remove empty lines at start and end while preserving internal empty lines
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    return '\n'.join(cleaned_lines)

def detect_language(element):
    """Detect code language from element attributes"""
    if not element:
        return ''
        
    # Check class names
    classes = element.get('class', [])
    for cls in classes:
        if cls.startswith(('language-', 'lang-')):
            return cls.replace('language-', '').replace('lang-', '')
            
    # Check data attributes
    for attr in element.attrs:
        if attr.startswith('data-lang'):
            return element[attr]
            
    # Detect from content
    code_text = element.get_text()
    language_hints = {
        'import': 'typescript',
        'function': 'typescript',
        'const': 'typescript',
        'export': 'typescript',
        'interface': 'typescript',
        'type': 'typescript',
        'npm': 'bash',
        'yarn': 'bash',
        'apt-get': 'bash',
        '<template>': 'vue',
        'useState': 'jsx',
        'NextResponse': 'typescript',
        'supabase.auth': 'typescript'
    }
    
    for hint, lang in language_hints.items():
        if hint in code_text:
            return lang
            
    return ''

def is_code_block(text, element=None):
    """Enhanced code block detection"""
    # Always treat pre tags as blocks
    if element and element.parent and element.parent.name == 'pre':
        return True
        
    # Check for code block indicators
    if element and element.get('class'):
        classes = element.get('class')
        if any(c in str(classes) for c in ['block', 'language-', 'hljs', 'syntax', 'code-block']):
            return True
    
    # Content-based detection
    has_newlines = '\n' in text.strip()
    word_count = len(text.split())
    
    code_patterns = [
        'function',
        'import',
        'class',
        'const',
        'return',
        'async',
        'await',
        '{',
        '};',
        '=>',
        'interface',
        'type',
        'export'
    ]
    
    return (has_newlines or 
            word_count > 10 or 
            any(pattern in text for pattern in code_patterns))

def format_code_block(code, language=''):
    """Enhanced code block formatting"""
    code = clean_code(code)
    if not code.strip():
        return ''
    
    language_map = {
        'js': 'javascript',
        'ts': 'typescript',
        'jsx': 'javascript',
        'tsx': 'typescript',
        'shell': 'bash',
        'sh': 'bash',
        'json': 'json',
        'py': 'python',
    }
    
    lang_spec = language_map.get(language, language) if language else ''
    
    # Format with proper spacing and ensure empty lines before and after
    return f"\n```{lang_spec}\n{code.strip()}\n```\n"

def format_link(element):
    """Format links with proper spacing"""
    href = element.get('href', '')
    text = clean_text(element.get_text(strip=True))
    # Ensure proper spacing around links
    return f" [{text}]({href}) " if href and text else text

def format_image(element):
    """Format images with proper attributes and spacing"""
    src = element.get('src', '')
    alt = clean_text(element.get('alt', ''))
    title = clean_text(element.get('title', ''))
    if title:
        return f"\n![{alt}]({src} \"{title}\")\n"
    return f"\n![{alt}]({src})\n" if src else ''

def get_list_depth(element):
    """Calculate list nesting depth"""
    depth = 0
    parent = element.parent
    while parent:
        if parent.name in ['ul', 'ol']:
            depth += 1
        parent = parent.parent
    return depth

def format_list_item(marker, content, code_blocks=None):
    """Enhanced list item formatting with proper spacing"""
    indent = '  ' * (len(marker.split('-')[0]) // 2)
    content = content.strip()
    
    # Ensure proper spacing around inline code in list items
    content = re.sub(r'`(\S)', '` \\1', content)
    content = re.sub(r'(\S)`', '\\1 `', content)
    
    lines = [f"{marker} {content}"]
    
    if code_blocks:
        for block in code_blocks:
            if block.strip():
                lines.append('')
                block_lines = block.split('\n')
                if len(indent) > 0:
                    lines.extend([f"{indent}{line}" for line in block_lines])
                else:
                    lines.extend(block_lines)
                lines.append('')
    
    return '\n'.join(lines)

def clean_up_content(content):
    """Final content cleanup and formatting with enhanced spacing rules"""
    lines = content.splitlines()
    processed_lines = []
    in_code_block = False
    last_line_type = None
    
    for i, line in enumerate(lines):
        current_line_type = None
        stripped_line = line.strip()
        
        # Detect line type
        if line.startswith('```'):
            in_code_block = not in_code_block
            current_line_type = 'code_block'
        elif line.startswith('#'):
            current_line_type = 'heading'
        elif line.startswith('-'):
            current_line_type = 'list_item'
        elif stripped_line:
            current_line_type = 'content'
        
        # Enhanced spacing rules
        if not in_code_block and last_line_type and current_line_type:
            # Always add space before headings unless it's after another heading
            if current_line_type == 'heading':
                if last_line_type != 'heading':
                    processed_lines.extend(['', ''])
            # Add space before lists unless they follow a heading
            elif current_line_type == 'list_item':
                if last_line_type not in ['list_item', 'heading']:
                    processed_lines.append('')
            # Add space after lists before regular content
            elif current_line_type == 'content':
                if last_line_type == 'list_item':
                    processed_lines.append('')
            # Add space around code blocks
            elif current_line_type == 'code_block':
                if last_line_type != 'code_block':
                    processed_lines.append('')
        
        processed_lines.append(line)
        if stripped_line or current_line_type == 'code_block':
            last_line_type = current_line_type
    
    content = '\n'.join(processed_lines)
    
    # Clean up spacing with enhanced rules
    content = re.sub(r'\n{5,}', '\n\n\n\n', content)  # Max 3 blank lines anywhere
    content = re.sub(r'```\n\n+```', '```\n```', content)  # No extra lines between empty code blocks
    content = re.sub(r'\s+`', ' `', content)  # Single space before inline code
    content = re.sub(r'`\s+', '` ', content)  # Single space after inline code
    
    # Enhanced list and heading spacing
    content = re.sub(r'(\n- [^\n]+)\n([^-\n])', r'\1\n\n\2', content)  # Double line after list items
    content = re.sub(r'(^|\n)(#+\s[^\n]+)\n([^\n#])', r'\1\2\n\n\3', content)  # Double line after headings unless next is heading
    content = re.sub(r'(\n\n\n)#', r'\n\n#', content)  # Max 2 blank lines before headings
    
    # Code block spacing
    content = re.sub(r'\n{3,}```', '\n\n```', content)  # Max one blank line before code blocks
    content = re.sub(r'```\n{3,}', '```\n\n', content)  # Max one blank line after code blocks
    content = re.sub(r'(```.*\n.*\n```)\n([^\n])', r'\1\n\n\2', content)  # Double line after code blocks
    
    # Clean up any remaining multiple blank lines
    content = re.sub(r'\n{4,}', '\n\n\n', content)  # Max 2 blank lines between other elements
    
    return content.strip()

def add_spacing_around_links(text):
    """Add proper spacing around markdown links while preserving existing formatting"""
    # Add space around links if not already present
    text = re.sub(r'(?<!\s)\[', ' [', text)  # Add space before link if missing
    text = re.sub(r'\](?!\(|\s)', '] ', text)  # Add space after link text if missing
    text = re.sub(r'\)(?!\s|$|\.|,|\?|!|:)', ') ', text)  # Add space after link if missing
    # Clean up any double spaces created
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the main content container more specifically
        main_content = (
            soup.find('article') or 
            soup.find('main') or 
            soup.find('div', class_=['docs-content', 'article-content', 'main-content']) or
            soup.find('div', {'role': 'main'})
        )
        
        if not main_content:
            main_content = soup

        # Build markdown content
        markdown_content = []
        current_list = []
        last_heading = None
        in_list = False
        
        # Elements to skip
        skip_classes = ['sidebar', 'nav', 'menu', 'footer', 'header', 'search']
        skip_ids = ['nav', 'sidebar', 'menu', 'footer', 'header', 'search']
        
        for element in main_content.find_all(recursive=True):
            # Enhanced skip conditions
            if (not element.get_text(strip=True) or 
                (element.parent.name in ['nav', 'header', 'footer'] and 
                 not element.name in ['code', 'pre']) or
                (any(cls in str(element.get('class', [])) for cls in skip_classes) and 
                 not element.name in ['code', 'pre']) or
                (any(id_val in str(element.get('id', '')) for id_val in skip_ids) and 
                 not element.name in ['code', 'pre'])):
                continue

            # Handle different element types
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = clean_text(element.get_text(strip=True))
                if text != last_heading:
                    if current_list:
                        markdown_content.extend(current_list)
                        markdown_content.append('')
                        current_list = []
                    
                    level = int(element.name[1])
                    if level <= 2:
                        markdown_content.append('\n')
                    markdown_content.append(f"{'#' * level} {text}")
                    markdown_content.append('')  # Single line break after heading
                    last_heading = text
                    in_list = False
            
            elif element.name == 'p':
                if current_list:
                    markdown_content.extend(current_list)
                    markdown_content.append('')
                    current_list = []
                
                content = []
                for child in element.children:
                    if child.name == 'code':
                        code_text = clean_code(child.get_text(strip=True))
                        if is_code_block(code_text, child):
                            if content:
                                markdown_content.append(add_spacing_around_links(''.join(content).strip()))
                                content = []
                            markdown_content.append(format_code_block(code_text))
                        else:
                            content.append(f"`{code_text}`")
                    elif child.name == 'a':
                        content.append(' ' + format_link(child) + ' ')
                    elif child.name == 'img':
                        if content:
                            markdown_content.append(add_spacing_around_links(''.join(content).strip()))
                            content = []
                        markdown_content.append(format_image(child))
                    else:
                        text = clean_text(str(child.string or ''))
                        if text.strip():
                            content.append(text)
                
                if content:
                    markdown_content.append(add_spacing_around_links(''.join(content).strip()))
                    markdown_content.append('')  # Single line break after paragraph
                in_list = False
            
            elif element.name == 'li':
                content = []
                code_blocks = []
                depth = get_list_depth(element)
                list_marker = '  ' * (depth - 1) + '-'
                
                for child in element.children:
                    if child.name == 'code':
                        code_text = clean_code(child.get_text(strip=True))
                        if is_code_block(code_text, child):
                            if content:
                                code_blocks.append(format_code_block(code_text))
                            else:
                                code_blocks.append(format_code_block(code_text))
                        else:
                            content.append(f"`{code_text}`")
                    elif child.name == 'a':
                        content.append(' ' + format_link(child) + ' ')
                    elif child.name == 'img':
                        if content:
                            current_list.append(format_list_item(list_marker, ''.join(content).strip()))
                            content = []
                        current_list.append(format_image(child))
                    else:
                        text = clean_text(str(child.string or ''))
                        if text.strip():
                            content.append(text)
                
                if content or code_blocks:
                    current_list.append(format_list_item(list_marker, ''.join(content).strip(), code_blocks))
                in_list = True
            
            elif element.name == 'pre' or (element.name == 'code' and element.parent.name not in ['p', 'li']):
                if current_list:
                    markdown_content.extend(current_list)
                    markdown_content.append('')
                    current_list = []
                
                code_text = element.get_text(strip=False)
                
                # Only format as code block if it's a pre tag or meets block criteria
                if element.name == 'pre' or is_code_block(code_text, element):
                    # Get language if specified
                    classes = element.get('class', [])
                    language = ''
                    for cls in classes:
                        if cls.startswith('language-'):
                            language = cls.replace('language-', '')
                            break
                    
                    markdown_content.append(format_code_block(code_text, language))
                else:
                    # Format as inline code
                    markdown_content.append(f"`{clean_code(code_text)}`")
                
                in_list = False
            
            elif element.name == 'img':
                if current_list:
                    markdown_content.extend(current_list)
                    markdown_content.append('')
                    current_list = []
                markdown_content.append(format_image(element))

        # Add any remaining list items
        if current_list:
            markdown_content.extend(current_list)
            markdown_content.append('')

        # Clean up the final content
        content = '\n'.join(markdown_content)
        # Fix code block spacing
        content = re.sub(r'\n{2,}```', '\n```', content)  # Max one blank line before code block
        content = re.sub(r'```\n{2,}', '```\n', content)  # Max one blank line after code block
        content = re.sub(r'```\n\n+```', '```\n\n```', content)  # Fix spacing between consecutive code blocks
        # Remove excessive blank lines
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        # Clean up extra spaces
        content = re.sub(r'\s+`', ' `', content)
        content = re.sub(r'`\s+', '` ', content)
        # Remove trailing spaces on lines
        content = '\n'.join(line.rstrip() for line in content.splitlines())
        
        return content.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return ""

def calculate_token_cost(text_length: int) -> float:
    """Estimate cost based on text length (rough approximation)"""
    # Together.ai pricing for Mistral-7B is approximately $0.0002 per 1K tokens
    # Rough approximation: 1 token ≈ 4 characters
    estimated_tokens = text_length / 4
    cost_per_1k_tokens = 0.0002
    return (estimated_tokens / 1000) * cost_per_1k_tokens

def enhance_markdown_formatting(content: str, api_key: Optional[str] = None) -> str:
    """Optional enhancement using Mistral 7B for better markdown formatting"""
    if not api_key:
        print("\n[yellow]⚠️  No API key found - skipping AI enhancement[/yellow]")
        return content
        
    try:
        # Calculate approximate cost before making the call
        estimated_cost = calculate_token_cost(len(content))
        print(f"\n[blue]💰 Estimated cost: ${estimated_cost:.4f}[/blue]")
        print("\n[blue]🤖 Using Mistral to enhance formatting...[/blue]")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [{
            "role": "system",
            "content": """You are a markdown formatting expert. Your task is to improve the formatting while preserving all information and links. Focus on:
1. Consistent spacing between sections
2. Beautiful list formatting
3. Proper code block presentation
4. Clear section hierarchy
5. Clean link and inline code formatting

Important!!!: Return ONLY the raw markdown content. Do not add any explanations. The users is saving this output directly to a markdown file."""
        }, {
            "role": "user",
            "content": f"Here is the markdown content to improve. Remember to return only the raw markdown without any wrapper markers:\n\n{content}"
        }]

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json={
                "model": "mistralai/Mistral-7B-Instruct-v0.2",
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.1,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                enhanced_content = result["choices"][0]["message"]["content"].strip()
                
                # Clean up any wrapping code block markers the AI might have added
                # First pass - remove outer code block if present
                if enhanced_content.startswith('```') and enhanced_content.endswith('```'):
                    enhanced_content = enhanced_content[3:-3].strip()
                # Second pass - handle language specifiers
                if enhanced_content.startswith('```markdown') or enhanced_content.startswith('```md'):
                    end_of_first_line = enhanced_content.find('\n')
                    if end_of_first_line != -1 and enhanced_content.endswith('```'):
                        enhanced_content = enhanced_content[end_of_first_line + 1:-3].strip()
                
                # Third pass - clean up any remaining code block markers at start/end
                enhanced_content = re.sub(r'^```\s*\n', '', enhanced_content)
                enhanced_content = re.sub(r'\n\s*```$', '', enhanced_content)
                
                # Fourth pass - deduplicate headers
                lines = enhanced_content.splitlines()
                seen_headers = set()
                cleaned_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                    if line.startswith('#'):
                        header = line.strip()
                        if header not in seen_headers:
                            seen_headers.add(header)
                            cleaned_lines.append(line)
                    else:
                        cleaned_lines.append(line)
                
                # Fifth pass - ensure all code blocks are closed
                enhanced_content = '\n'.join(cleaned_lines)
                if in_code_block:  # If we ended inside a code block, close it
                    enhanced_content += '\n```'
                
                print("[green]✨ AI enhancement complete![/green]")
                return enhanced_content
            else:
                print("[red]❌ Unexpected API response format[/red]")
                return content
        elif response.status_code == 429:  # Rate limit exceeded
            print("[yellow]⚠️  Rate limit exceeded (60 calls/minute). Using original content.[/yellow]")
            return content
        print(f"[red]❌ API call failed with status code: {response.status_code}[/red]")
        if response.text:
            print(f"[red]Error details: {response.text}[/red]")
        return content
    except Exception as e:
        print(f"[red]❌ Enhancement failed: {e}[/red]")
        return content

def main():
    console = Console()
    
    url = "https://react.dev/reference/react/hooks"
    
    content = extract_content(url)
    
    # Debug API key status
    together_api_key = os.getenv("TOGETHER_API_KEY")
    console.print("\n[bold blue]API Status:[/bold blue]")
    if together_api_key:
        console.print(f"[green]✓ Found API key: {together_api_key[:4]}...{together_api_key[-4:]}[/green]")
        content = enhance_markdown_formatting(content, together_api_key)
    else:
        console.print("[yellow]⚠️  No API key found in environment variables[/yellow]")
        console.print("[yellow]Tip: Set it using: export TOGETHER_API_KEY='your_key_here'[/yellow]")
    
    # Copy to clipboard
    pyperclip.copy(content)
    
    # Print using Rich's markdown renderer
    console.print(Markdown(content))
    
    # Notify user about clipboard copy
    console.print("\n[green]✓[/green] Content has been copied to clipboard!")

if __name__ == "__main__":
    main()
