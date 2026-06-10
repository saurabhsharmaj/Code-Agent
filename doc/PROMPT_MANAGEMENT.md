# Prompt Management System

## Overview

All prompts are now externalized from Python code into YAML files located in `src/prompts/data/`. This follows best practices for managing LLM prompts and enables easy maintenance, versioning, and updates without code changes.

## Structure

```
src/prompts/
├── registry.py          # PromptRegistry class for loading prompts
└── data/
    ├── planner.yaml     # Planner agent prompts
    ├── reviewer.yaml    # Reviewer agent prompts
    └── decision.yaml    # Decision agent prompts
```

## Prompt Registry

The `PromptRegistry` class manages all prompt loading and caching:

### Features
- **Lazy Loading**: Prompts are loaded on first access
- **Caching**: Loaded prompts are cached in memory for performance
- **File Validation**: Validates YAML syntax and required fields
- **Directory Management**: Configurable prompt directory

### API

```python
from src.prompts.registry import PromptRegistry

# Load a prompt
prompt_template = PromptRegistry.get("category", "prompt_key")

# Format the prompt with variables
filled_prompt = prompt_template.format(variable1="value1", variable2="value2")

# Get all prompts in a category
all_prompts = PromptRegistry.get_all("category")

# List all categories
categories = PromptRegistry.list_categories()

# List all prompts in a category
prompt_keys = PromptRegistry.list_prompts("category")

# Reload all prompts from disk (useful during development)
PromptRegistry.reload()

# Get the prompts directory
prompts_dir = PromptRegistry.get_prompts_dir()

# Set custom prompts directory
PromptRegistry.set_prompts_dir(Path("custom/path"))
```

## YAML Format

Each YAML file is organized by category, with prompt keys as subkeys:

```yaml
category_name:
  prompt_key_1: |
    Your prompt template here
    with {variable1} and {variable2}
    
  prompt_key_2: |
    Another prompt...
```

### Example: planner.yaml

```yaml
planner:
  strategy: |
    You are a Kubernetes deployment planner...
    User Request: {task}
    ...
```

## Current Prompts

### Planner Agent (`planner.yaml`)
- **Key**: `strategy`
- **Variables**: `{task}`
- **Purpose**: Generate deployment strategy and configuration

### Reviewer Agent (`reviewer.yaml`)
- **Key**: `review`
- **Variables**: `{deployment_yaml}`
- **Purpose**: Validate and review K8s deployment manifests

### Decision Agent (`decision.yaml`)
- **Key**: `approval`
- **Variables**: `{review}`, `{retries}`, `{max_retries}`
- **Purpose**: Make approval/retry decisions based on review scores

## Usage in Agents

### Example: Using PromptRegistry in an Agent

```python
from src.prompts.registry import PromptRegistry

class MyAgent(BaseAgent):
    def execute(self, state):
        # Load prompt from registry
        prompt_template = PromptRegistry.get("my_category", "my_prompt")
        
        # Format with variables
        prompt = prompt_template.format(
            variable1=state["data1"],
            variable2=state["data2"]
        )
        
        # Use with LLM
        response = self.llm.invoke(prompt)
        return {...}
```

## Adding New Prompts

### Step 1: Create YAML File
Add your prompts to an existing file or create a new YAML file in `src/prompts/data/`:

```yaml
my_category:
  my_prompt: |
    Your prompt template with {variables}
    
  another_prompt: |
    Another template...
```

### Step 2: Use in Code
```python
from src.prompts.registry import PromptRegistry

prompt_template = PromptRegistry.get("my_category", "my_prompt")
prompt = prompt_template.format(variables="value")
```

### Step 3: No Code Restart Needed (Development)
To reload prompts without restarting:
```python
PromptRegistry.reload()
```

## Best Practices

1. **Keep Prompts DRY**: Avoid duplicating similar prompts; reuse or create variants
2. **Document Variables**: Use clear variable names like `{deployment_yaml}`, `{task}`
3. **Version Control**: Store YAML files in version control alongside code
4. **Consistent Naming**: Use lowercase, snake_case for category and prompt keys
5. **Clear Structure**: Organize related prompts in the same YAML file
6. **Add Comments**: Use YAML comments to document purpose and usage

## Benefits of This Approach

| Benefit | Description |
|---------|-------------|
| **Maintainability** | Update prompts without touching Python code |
| **Versioning** | Track prompt changes separately in version control |
| **Reusability** | Share prompts across multiple agents |
| **Performance** | Prompts are cached after first load |
| **Flexibility** | Easy to add new prompts or categories |
| **Readability** | YAML is more readable than Python strings |
| **Non-Developer Access** | Non-developers can update prompts |

## Migration from Hardcoded Prompts

Previously, prompts were hardcoded as:

```python
# ❌ OLD WAY (DO NOT USE)
PLANNER_PROMPT = PromptTemplate(
    input_variables=["task"],
    template="""..."""
)
```

Now use:

```python
# ✅ NEW WAY
prompt_template = PromptRegistry.get("planner", "strategy")
```

## Troubleshooting

### Prompt Not Found
```
KeyError: Prompt category 'x' not found. Available: ['planner', 'reviewer', 'decision']
```
**Solution**: Check category and prompt key spelling in YAML file and code

### YAML Parse Error
```
ValueError: Invalid YAML in prompt file...
```
**Solution**: Validate YAML syntax using an online YAML validator

### Variables Not Replaced
```
prompt = prompt_template.format(wrong_var="value")  # ❌
```
**Solution**: Use correct variable names from YAML file (e.g., `task`, `deployment_yaml`)

## See Also

- [Prompt YAML Files](src/prompts/data/)
- [PromptRegistry Class](src/prompts/registry.py)
- [Agent Implementations](src/agents/)
