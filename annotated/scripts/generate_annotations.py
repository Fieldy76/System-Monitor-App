#!/usr/bin/env python3  # #!/usr/bin/env python3
"""Generate annotated copies of source files with inline comments.  # """Generate annotated copies of source files with inline comments.
Supported file types:  # Supported file types:
- .py  -> Python comments using '#'  # - .py  -> Python comments using '#'
- .html, .htm, .j2 -> HTML/Jinja comments using '<!-- ... -->'  # - .html, .htm, .j2 -> HTML/Jinja comments using '<!-- ... -->'
- .js  -> JavaScript comments using '//'  # - .js  -> JavaScript comments using '//'
- .css -> CSS comments using '/* ... */'  # - .css -> CSS comments using '/* ... */'
The script walks the project directory, creates an 'annotated' folder mirroring the structure,  # The script walks the project directory, creates an 'annotated' folder mirroring the structure,
and writes each line followed by a comment that mirrors the original line (as a placeholder).  # and writes each line followed by a comment that mirrors the original line (as a placeholder).
You can later edit the generated comments for more detailed explanations.  # You can later edit the generated comments for more detailed explanations.
"""  # """
import os  # import os
import pathlib  # import pathlib
  # blank line
# Define comment styles per extension  # # Define comment styles per extension
COMMENT_STYLES = {  # COMMENT_STYLES = {
    '.py': lambda line: f"  # {line.strip() or 'blank line'}",  # '.py': lambda line: f"  # {line.strip() or 'blank line'}",
    '.js': lambda line: f"  // {line.strip() or 'blank line'}",  # '.js': lambda line: f"  // {line.strip() or 'blank line'}",
    '.css': lambda line: f"  /* {line.strip() or 'blank line'} */",  # '.css': lambda line: f"  /* {line.strip() or 'blank line'} */",
    '.html': lambda line: f"  <!-- {line.strip() or 'blank line'} -->",  # '.html': lambda line: f"  <!-- {line.strip() or 'blank line'} -->",
    '.htm': lambda line: f"  <!-- {line.strip() or 'blank line'} -->",  # '.htm': lambda line: f"  <!-- {line.strip() or 'blank line'} -->",
    '.j2': lambda line: f"  <!-- {line.strip() or 'blank line'} -->",  # '.j2': lambda line: f"  <!-- {line.strip() or 'blank line'} -->",
}  # }
  # blank line
def annotate_file(src_path: pathlib.Path, dst_path: pathlib.Path):  # def annotate_file(src_path: pathlib.Path, dst_path: pathlib.Path):
    ext = src_path.suffix.lower()  # ext = src_path.suffix.lower()
    comment_func = COMMENT_STYLES.get(ext)  # comment_func = COMMENT_STYLES.get(ext)
    if not comment_func:  # if not comment_func:
        # Copy file unchanged if unsupported  # # Copy file unchanged if unsupported
        dst_path.write_bytes(src_path.read_bytes())  # dst_path.write_bytes(src_path.read_bytes())
        return  # return
    with src_path.open('r', encoding='utf-8') as src, dst_path.open('w', encoding='utf-8') as dst:  # with src_path.open('r', encoding='utf-8') as src, dst_path.open('w', encoding='utf-8') as dst:
        for line in src:  # for line in src:
            stripped = line.rstrip('\n')  # stripped = line.rstrip('\n')
            comment = comment_func(stripped)  # comment = comment_func(stripped)
            dst.write(f"{stripped}{comment}\n")  # dst.write(f"{stripped}{comment}\n")
  # blank line
def main():  # def main():
    project_root = pathlib.Path(os.getcwd())  # project_root = pathlib.Path(os.getcwd())
    annotated_root = project_root / 'annotated'  # annotated_root = project_root / 'annotated'
    for root, dirs, files in os.walk(project_root):  # for root, dirs, files in os.walk(project_root):
        # Skip the annotated directory itself to avoid recursion  # # Skip the annotated directory itself to avoid recursion
        if 'annotated' in dirs:  # if 'annotated' in dirs:
            dirs.remove('annotated')  # dirs.remove('annotated')
        # Skip virtual environment and hidden dirs  # # Skip virtual environment and hidden dirs
        if 'venv' in dirs:  # if 'venv' in dirs:
            dirs.remove('venv')  # dirs.remove('venv')
        if any(part.startswith('.') for part in pathlib.Path(root).parts):  # if any(part.startswith('.') for part in pathlib.Path(root).parts):
            continue  # continue
        for file in files:  # for file in files:
            src_path = pathlib.Path(root) / file  # src_path = pathlib.Path(root) / file
            rel_path = src_path.relative_to(project_root)  # rel_path = src_path.relative_to(project_root)
            dst_path = annotated_root / rel_path  # dst_path = annotated_root / rel_path
            dst_path.parent.mkdir(parents=True, exist_ok=True)  # dst_path.parent.mkdir(parents=True, exist_ok=True)
            annotate_file(src_path, dst_path)  # annotate_file(src_path, dst_path)
  # blank line
if __name__ == '__main__':  # if __name__ == '__main__':
    main()  # main()
