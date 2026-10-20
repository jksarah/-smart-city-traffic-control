# Coding Rules

Basic rules for all code in this project. Read this file at the start of every new session and follow it.

## 1. Comments
- Do not overwrite, delete or rewrite existing explanatory comments. Leave them as they are unless the code they describe changes.
- Do not add excessive comments. Comment only where the reason for the code is not obvious.
- Explain why, not what. Do not repeat what the code already says.

## 2. Python
- Use standard Python and standard pip-installable packages only. Prefer the standard library when it is enough.
- Do not add a dependency for something small that the standard library can do.
- Follow PEP 8: 4-space indentation, `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Keep lines at a reasonable length (about 100 characters at most).
- Keep imports at the top of the file, grouped as standard library, third-party, then local.
- List dependencies in `requirements.txt`.

## 3. JavaScript
- Use standard, plain JavaScript (modern ES6+). No frameworks or build tools unless they are agreed first.
- Use `const` by default and `let` when a value changes. Never use `var`.
- Use `camelCase` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Use 4-space indentation, semicolons and `===` for comparisons.
- Use the browser's built-in APIs (`WebSocket`, `fetch`, Canvas) directly.

## 4. Style
- Follow one standard style across the project. Match the style of the surrounding code.
- Use clear, descriptive names. Avoid abbreviations that are not common.
- Keep functions short and focused on one job.
- Do not leave unused code, unused imports or debugging output in the code.

## 5. Keep It Simple
- Always look for the simplest solution to a problem first.
- Do not over-complicate. Do not add abstractions, layers, settings or features that were not asked for.
- Prefer a few plain functions or one small class over complex patterns.
- Solve the current problem. Do not build for imagined future needs.
- If a solution feels complicated, step back and look for a simpler one.

## 6. Working Habits
- Change only what is needed for the task.
- Keep each file small and focused.
- Run or test the code after changing it, when possible.
- If a rule here conflicts with a request, ask before breaking the rule.
