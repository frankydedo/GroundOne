---
type: concept
tags: [framework, agents, ai]
---
# LangChain

**LangChain** is a popular framework for developing applications powered by language models. In the context of decision-making systems like [[Jev]], it offers abstractions such as middleware and agent loops.

## Integration with System One Models
With the introduction of [[System One Models]], LangChain can integrate them to optimize the agent loop, avoiding full LLM calls for simple decisions.
- **TypeSafeClassifier**: The `langchain-typesafe` package allows passing state and questions directly to Jev.
- **Middlewares**: Tools like `ModelRouterMiddleware` (for dynamic model routing) and `AutoModeMiddleware` (for risk-gating tools) use decision models to make the agent loop faster and more robust.
