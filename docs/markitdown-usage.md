# MarkItDown — ghi chu su dung (tach tu README cua nhanh be-init)

### Converting an Invoice

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("invoice.pdf")

# Output will detect form structure and create tables:
# | Item | Quantity | Price | Total |
# |------|----------|-------|-------|
# | ...  | ...      | ...   | ...   |

print(result.markdown)
```

### Converting a Form

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("application_form.pdf")

# Output preserves field/value structure:
# | Field Name | Value |
# |------------|-------|
# | Name | John Doe |
# | Address | 123 Main St |

print(result.markdown)
```

### Error Handling

```python
from markitdown import MarkItDown
from markitdown._exceptions import MissingDependencyException

md = MarkItDown()

try:
    result = md.convert("document.pdf")
except MissingDependencyException:
    print("Install PDF dependencies: pip install markitdown[pdf]")
except Exception as e:
    print(f"Conversion error: {e}")
```