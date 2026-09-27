# Stkt Universal Syntax Highlighting Suite

This package provides complete, production-ready syntax highlighting definitions for the **Stkt** programming language (`.stkt`) across all major code editors and tools.

---

## Supported Editors & Tools

| Editor / Tool | Technology Used | Location in this Package |
| :--- | :--- | :--- |
| **VS Code / Cursor / Windsurf** | TextMate Grammar (`.tmLanguage.json`) | `vscode/` |
| **Sublime Text / TextMate** | TextMate Grammar | `vscode/syntaxes/stkt.tmLanguage.json` |
| **Vim / Neovim (Classic)** | Vim syntax script (`.vim`) | `vim/` |
| **Neovim (Tree-Sitter) / Helix** | Tree-Sitter & queries (`highlights.scm`) | `zed/` & `helix/` |
| **Zed** | Tree-Sitter / Language settings | `zed/` (or via `settings.json`) |
| **Web Docs (Sphinx, MkDocs, HTML)**| Pygments Python Lexer | `pygments/` |
| **Terminal CLI** | ANSI colorizer tool | `cli/` |

---

## Installation by Editor

### 1. VS Code / Cursor
```bash
cp -r syntax_highlight/vscode ~/.vscode/extensions/stkt-syntax
# Or for Cursor:
cp -r syntax_highlight/vscode ~/.cursor/extensions/stkt-syntax
```

### 2. Sublime Text
Copy the TextMate grammar into your Sublime User packages:
```bash
cp syntax_highlight/vscode/syntaxes/stkt.tmLanguage.json ~/Library/Application\ Support/Sublime\ Text/Packages/User/
```

### 3. Vim / Neovim
```bash
mkdir -p ~/.vim/syntax ~/.vim/ftdetect
cp syntax_highlight/vim/syntax/stkt.vim ~/.vim/syntax/
cp syntax_highlight/vim/ftdetect/stkt.vim ~/.vim/ftdetect/
# (For Neovim: replace ~/.vim with ~/.config/nvim)
```

### 4. Helix
Append `syntax_highlight/helix/languages.toml` to your `~/.config/helix/languages.toml`.

### 5. Zed
Add to `~/.config/zed/settings.json`:
```json
"file_types": {
  "Rust": ["stkt"]
}
```

### 6. Terminal CLI Quick Viewer
```bash
python syntax_highlight/cli/highlight.py path/to/file.stkt
```
