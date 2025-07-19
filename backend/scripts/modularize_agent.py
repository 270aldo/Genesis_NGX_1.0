#!/usr/bin/env python3
"""
Agent Modularization Script
===========================

Splits large agent files into modular components following best practices.
Reduces 3000+ line files to manageable 300-500 line modules.
"""

import os
import re
import ast
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import click
import black


class AgentModularizer:
    """Handles splitting monolithic agent files into modules."""
    
    def __init__(self, agent_path: Path, dry_run: bool = True):
        self.agent_path = agent_path
        self.agent_name = agent_path.name
        self.dry_run = dry_run
        self.stats = {
            "original_lines": 0,
            "skills_extracted": 0,
            "config_lines": 0,
            "prompt_lines": 0,
            "model_lines": 0,
            "final_agent_lines": 0
        }
    
    def modularize(self) -> Dict[str, Any]:
        """Main modularization process."""
        agent_file = self.agent_path / "agent.py"
        
        if not agent_file.exists():
            raise FileNotFoundError(f"No agent.py found in {self.agent_path}")
        
        click.echo(f"Modularizing {self.agent_name}...")
        
        # Read original file
        with open(agent_file, 'r') as f:
            content = f.read()
            self.stats["original_lines"] = len(content.splitlines())
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            click.echo(f"Error parsing {agent_file}: {e}", err=True)
            return self.stats
        
        # Extract components
        extracted = {
            "imports": self._extract_imports(tree),
            "config": self._extract_config(tree, content),
            "skills": self._extract_skills(tree, content),
            "prompts": self._extract_prompts(tree, content),
            "models": self._extract_models(tree, content),
            "main_class": self._extract_main_class(tree, content)
        }
        
        if not self.dry_run:
            # Backup original
            shutil.copy(agent_file, agent_file.with_suffix('.py.backup'))
            
            # Create module structure
            self._create_module_structure(extracted)
            
            # Generate new agent.py
            self._generate_main_agent_file(extracted)
        
        # Report results
        self._report_results(extracted)
        
        return self.stats
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                if node.module:
                    imports.append(f"from {node.module} import {', '.join(names)}")
        
        return imports
    
    def _extract_config(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Extract configuration constants and initialization."""
        config_data = {
            "constants": [],
            "init_config": [],
            "lines": []
        }
        
        # Find configuration patterns
        lines = content.splitlines()
        
        # Extract constants (ALL_CAPS variables)
        for i, line in enumerate(lines):
            if re.match(r'^[A-Z_]+\s*=', line.strip()):
                # Find the complete assignment (handle multi-line)
                j = i
                while j < len(lines) and not lines[j].strip().endswith(('"""', "'''", "}", "]", ")")):
                    j += 1
                config_data["constants"].extend(lines[i:j+1])
                config_data["lines"].extend(range(i, j+1))
        
        self.stats["config_lines"] = len(config_data["constants"])
        return config_data
    
    def _extract_skills(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract skill methods from the main class."""
        skills = []
        
        # Find main agent class
        main_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Agent" in node.name:
                main_class = node
                break
        
        if not main_class:
            return skills
        
        # Extract skill-like methods
        skill_patterns = [
            r"analyze", r"generate", r"create", r"process", 
            r"calculate", r"optimize", r"evaluate", r"plan"
        ]
        
        lines = content.splitlines()
        
        for method in main_class.body:
            if isinstance(method, ast.FunctionDef):
                # Check if it's a skill method
                is_skill = any(pattern in method.name.lower() for pattern in skill_patterns)
                
                if is_skill and not method.name.startswith("_"):
                    # Get method source
                    start_line = method.lineno - 1
                    end_line = method.end_lineno
                    
                    method_lines = lines[start_line:end_line]
                    
                    skills.append({
                        "name": method.name,
                        "lines": method_lines,
                        "line_count": len(method_lines),
                        "async": isinstance(method, ast.AsyncFunctionDef)
                    })
        
        self.stats["skills_extracted"] = len(skills)
        return skills
    
    def _extract_prompts(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Extract prompt strings and templates."""
        prompts = {
            "system_prompts": [],
            "examples": [],
            "templates": []
        }
        
        lines = content.splitlines()
        
        # Find large string constants (likely prompts)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        
                        # Check if it's a prompt-related variable
                        if any(word in name.lower() for word in ["prompt", "template", "instruction"]):
                            if isinstance(node.value, ast.Str):
                                # Single string
                                if len(node.value.s) > 100:  # Likely a prompt
                                    prompts["system_prompts"].append({
                                        "name": name,
                                        "content": node.value.s,
                                        "line": node.lineno
                                    })
        
        self.stats["prompt_lines"] = sum(
            len(p["content"].splitlines()) for p in prompts["system_prompts"]
        )
        
        return prompts
    
    def _extract_models(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract data models and type definitions."""
        models = []
        
        # Find TypedDict, NamedTuple, or class definitions that look like models
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a model-like class
                is_model = any(
                    base.id in ["BaseModel", "TypedDict", "NamedTuple"] 
                    for base in node.bases 
                    if isinstance(base, ast.Name)
                )
                
                if is_model or "Model" in node.name or "Schema" in node.name:
                    models.append({
                        "name": node.name,
                        "line": node.lineno,
                        "type": "pydantic" if any(b.id == "BaseModel" for b in node.bases if isinstance(b, ast.Name)) else "dataclass"
                    })
        
        self.stats["model_lines"] = len(models) * 20  # Estimate
        return models
    
    def _extract_main_class(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """Extract the main agent class structure."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Agent" in node.name:
                return {
                    "name": node.name,
                    "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                    "line": node.lineno
                }
        return {}
    
    def _create_module_structure(self, extracted: Dict[str, Any]) -> None:
        """Create the modular directory structure."""
        # Create directories
        for subdir in ["skills", "prompts", "models", "services"]:
            (self.agent_path / subdir).mkdir(exist_ok=True)
            
            # Create __init__.py
            init_file = self.agent_path / subdir / "__init__.py"
            init_file.write_text('"""Auto-generated module."""\n')
        
        # Write config.py
        if extracted["config"]["constants"]:
            self._write_config_module(extracted["config"])
        
        # Write skills
        for skill in extracted["skills"]:
            self._write_skill_module(skill)
        
        # Write prompts
        if extracted["prompts"]["system_prompts"]:
            self._write_prompts_module(extracted["prompts"])
    
    def _write_config_module(self, config: Dict[str, Any]) -> None:
        """Write configuration module."""
        config_file = self.agent_path / "config.py"
        
        content = ['"""Agent configuration."""', "", "from dataclasses import dataclass", "", ""]
        content.extend(config["constants"])
        content.extend(["", "", "@dataclass", f"class {self.agent_name.title()}Config:", "    pass"])
        
        config_file.write_text("\n".join(content))
    
    def _write_skill_module(self, skill: Dict[str, Any]) -> None:
        """Write individual skill module."""
        skill_file = self.agent_path / "skills" / f"{skill['name']}.py"
        
        content = [
            f'"""Skill: {skill["name"]}"""',
            "",
            "from typing import Dict, Any",
            "",
            "",
            f"{'async ' if skill['async'] else ''}def {skill['name']}(self, *args, **kwargs):",
        ]
        content.extend(["    " + line for line in skill["lines"][1:]])  # Skip def line
        
        skill_file.write_text("\n".join(content))
    
    def _write_prompts_module(self, prompts: Dict[str, Any]) -> None:
        """Write prompts module."""
        prompts_file = self.agent_path / "prompts" / "base_prompt.py"
        
        content = ['"""Agent prompts and templates."""', "", ""]
        
        for prompt in prompts["system_prompts"]:
            content.append(f'{prompt["name"]} = """')
            content.append(prompt["content"])
            content.append('"""')
            content.append("")
        
        prompts_file.write_text("\n".join(content))
    
    def _generate_main_agent_file(self, extracted: Dict[str, Any]) -> None:
        """Generate the new modularized agent.py file."""
        agent_file = self.agent_path / "agent.py"
        
        content = [
            '"""',
            f'{self.agent_name} - Modularized Version',
            '=' * 50,
            '',
            'This agent has been modularized for better maintainability.',
            'Original file backed up as agent.py.backup',
            '"""',
            '',
            '# Core imports',
        ]
        
        # Add imports
        content.extend(extracted["imports"][:10])  # First 10 imports
        content.extend([
            '',
            '# Local imports',
            f'from .config import {self.agent_name.title()}Config',
            'from .prompts import base_prompt',
        ])
        
        # Add skill imports
        if extracted["skills"]:
            content.append('from .skills import (')
            for skill in extracted["skills"]:
                content.append(f'    {skill["name"]},')
            content.append(')')
        
        content.extend(['', '', ''])
        
        # Add main class
        main_class = extracted["main_class"]
        content.extend([
            f'class {main_class["name"]}({", ".join(main_class["bases"])}):',
            f'    """Modularized {self.agent_name} agent."""',
            '    ',
            '    def __init__(self, **kwargs):',
            '        super().__init__(**kwargs)',
            f'        self.config = {self.agent_name.title()}Config()',
            '        self._setup_skills()',
            '    ',
            '    def _setup_skills(self):',
            '        """Initialize skills."""',
            '        self.skills = {',
        ])
        
        for skill in extracted["skills"]:
            content.append(f'            "{skill["name"]}": {skill["name"]},')
        
        content.extend([
            '        }',
            '',
            '    # Core agent methods go here',
            '    # Skills are imported from modules',
            ''
        ])
        
        # Format with black
        try:
            formatted = black.format_str("\n".join(content), mode=black.Mode())
            agent_file.write_text(formatted)
        except Exception:
            # Fallback if black fails
            agent_file.write_text("\n".join(content))
        
        self.stats["final_agent_lines"] = len(content)
    
    def _report_results(self, extracted: Dict[str, Any]) -> None:
        """Report modularization results."""
        click.echo("\n" + "=" * 50)
        click.echo("MODULARIZATION COMPLETE")
        click.echo("=" * 50)
        
        click.echo(f"Original file: {self.stats['original_lines']} lines")
        click.echo(f"Final agent.py: ~{self.stats['final_agent_lines']} lines")
        click.echo(f"Reduction: {self.stats['original_lines'] - self.stats['final_agent_lines']} lines")
        click.echo("")
        
        click.echo("Extracted components:")
        click.echo(f"  ✓ {self.stats['skills_extracted']} skills")
        click.echo(f"  ✓ {self.stats['config_lines']} config lines")
        click.echo(f"  ✓ {self.stats['prompt_lines']} prompt lines")
        click.echo(f"  ✓ {self.stats['model_lines']} model lines (estimated)")
        
        if self.dry_run:
            click.echo("\nDRY RUN - No files were modified")
            click.echo("Run with --no-dry-run to apply changes")


@click.command()
@click.argument('agent_path', type=click.Path(exists=True))
@click.option('--dry-run/--no-dry-run', default=True, help='Perform dry run without making changes')
def main(agent_path: str, dry_run: bool):
    """Modularize a monolithic agent file into components."""
    path = Path(agent_path)
    
    if not path.is_dir():
        click.echo("Error: agent_path must be a directory", err=True)
        return
    
    try:
        modularizer = AgentModularizer(path, dry_run=dry_run)
        modularizer.modularize()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise


if __name__ == '__main__':
    main()