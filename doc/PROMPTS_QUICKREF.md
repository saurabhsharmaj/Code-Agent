# Quick Reference: Prompt Management

## View All Prompts

```bash
python manage_prompts.py list
```

**Output:**
```
Available Prompt Categories:
- planner (1 prompt)
- reviewer (1 prompt)
- decision (1 prompt)
```

## View Specific Category

```bash
python manage_prompts.py show planner
```

## View Exact Prompt

```bash
python manage_prompts.py get planner strategy
```

## Show Registry Info

```bash
python manage_prompts.py info
```

## Use in Python Code

```python
from src.prompts.registry import PromptRegistry

# Load prompt template
template = PromptRegistry.get("planner", "strategy")

# Format with variables
prompt = template.format(task="Create K8s deployment")

# Use with LLM
response = llm.invoke(prompt)
```

## Update a Prompt

1. Edit the YAML file: `src/prompts/data/planner.yaml`
2. Reload in development: `PromptRegistry.reload()`
3. Changes take effect immediately - no code restart needed

## File Structure

```
src/prompts/
├── registry.py          # Core registry class
├── __init__.py          # Module exports
└── data/
    ├── planner.yaml     # Planner prompts
    ├── reviewer.yaml    # Reviewer prompts
    └── decision.yaml    # Decision prompts
```

## YAML Format

```yaml
category_name:
  prompt_key: |
    Your prompt template here
    Use {variables} for placeholders
    
  another_key: |
    Another prompt template...
```

## Available Prompts

| Category | Key | Variables | Purpose |
|----------|-----|-----------|---------|
| `planner` | `strategy` | `{task}` | Create deployment plan |
| `reviewer` | `review` | `{deployment_yaml}` | Review K8s manifest |
| `decision` | `approval` | `{review}`, `{retries}`, `{max_retries}` | Make approval decision |

## Common Tasks

### Add New Prompt
```yaml
# In src/prompts/data/mycategory.yaml
mycategory:
  my_new_prompt: |
    Your prompt template with {variables}
```

### Use New Prompt
```python
template = PromptRegistry.get("mycategory", "my_new_prompt")
prompt = template.format(variables="value")
```

### Reload During Development
```python
PromptRegistry.reload()  # Force reload from disk
```

### Get All Prompts in Category
```python
all_prompts = PromptRegistry.get_all("planner")
```

### List All Categories
```python
categories = PromptRegistry.list_categories()
```

### List All Prompts in Category
```python
keys = PromptRegistry.list_prompts("planner")
```

## Benefits

✅ No hardcoded prompts in Python  
✅ Easy to update without code changes  
✅ Prompts tracked separately in version control  
✅ Non-developers can edit prompts  
✅ Automatic caching for performance  
✅ Reload on-demand during development  

## Troubleshooting

**Prompt not found?**
```bash
python manage_prompts.py list
python manage_prompts.py show <category>
```

**YAML syntax error?**
- Use online YAML validator
- Check indentation (must be 2 spaces)

**Variables not working?**
- Use exact variable names from YAML
- Example: `{task}` not `{Task}`

---

For detailed documentation, see [PROMPT_MANAGEMENT.md](../docs/PROMPT_MANAGEMENT.md)
