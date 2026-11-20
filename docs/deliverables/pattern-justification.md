# Pattern Justification

## Factory Method

An answer can be written by either a user or an AI agent. If `Question` or `Answer` had to know the concrete author type, they would be coupled to every supported type and would need to change whenever a new one was introduced.

To avoid this, `User` and `AIAgent` implement the `Author` interface, and the Factory Method pattern selects the author when an answer is created. `AuthorFactory` is the abstract factory, while `HumanAuthorFactory` and `AIAgentFactory` are the concrete factories. `Question.addAnswer()` receives a factory, asks it for the author, and creates the `Answer` without knowing whether that author is human or AI.

As a result, `Answer` depends only on `Author`, and supporting another author type only requires adding another factory. The factories do not create a new author for every answer: they return the user who is answering or the AI agent that is already registered.

## Strategy

Automatic answers must support different LLM providers, such as OpenAI, Gemini, or a local model, each with its own API. Embedding those provider-specific details in the domain would make changing providers difficult and would force domain changes.

The `LLMStrategy` interface therefore defines `generate(prompt)`, with one implementation per provider. `AutoAnswerService` uses the configured strategy and can replace it through `setStrategy()`. The strategy receives and returns text rather than a `Question`, keeping it independent of the domain. Adding another provider only requires a new strategy implementation without changing the service or the domain model.
