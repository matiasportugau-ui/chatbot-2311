# Claude Code overview

> Learn about Claude Code, Anthropic's agentic coding tool that lives in your terminal and helps you turn ideas into code faster than ever before.

## Get started in 30 seconds

Prerequisites:

* A [Claude.ai](https://claude.ai) (recommended) or [Claude Console](https://console.anthropic.com/) account

**Install Claude Code:**

<Tabs>
  <Tab title="macOS/Linux">
    ```bash  theme={null}
    curl -fsSL https://claude.ai/install.sh | bash
    ```
  </Tab>

  <Tab title="Homebrew">
    ```bash  theme={null}
    brew install --cask claude-code
    ```
  </Tab>

  <Tab title="Windows">
    ```powershell  theme={null}
    irm https://claude.ai/install.ps1 | iex
    ```
  </Tab>

  <Tab title="NPM">
    ```bash  theme={null}
    npm install -g @anthropic-ai/claude-code
    ```

    Requires [Node.js 18+](https://nodejs.org/en/download/)
  </Tab>
</Tabs>

**Start using Claude Code:**

```bash  theme={null}
cd your-project
claude
```

You'll be prompted to log in on first use. That's it! [Continue with Quickstart (5 minutes) →](/en/quickstart)

<Tip>
  Claude Code automatically keeps itself up to date. See [advanced setup](/en/setup) for installation options, manual updates, or uninstallation instructions. Visit [troubleshooting](/en/troubleshooting) if you hit issues.
</Tip>

## What Claude Code does for you

* **Build features from descriptions**: Tell Claude what you want to build in plain English. It will make a plan, write the code, and ensure it works.
* **Debug and fix issues**: Describe a bug or paste an error message. Claude Code will analyze your codebase, identify the problem, and implement a fix.
* **Navigate any codebase**: Ask anything about your team's codebase, and get a thoughtful answer back. Claude Code maintains awareness of your entire project structure, can find up-to-date information from the web, and with [MCP](/en/mcp) can pull from external data sources like Google Drive, Figma, and Slack.
* **Automate tedious tasks**: Fix fiddly lint issues, resolve merge conflicts, and write release notes. Do all this in a single command from your developer machines, or automatically in CI.

## Why developers love Claude Code

* **Works in your terminal**: Not another chat window. Not another IDE. Claude Code meets you where you already work, with the tools you already love.
* **Takes action**: Claude Code can directly edit files, run commands, and create commits. Need more? [MCP](/en/mcp) lets Claude read your design docs in Google Drive, update your tickets in Jira, or use *your* custom developer tooling.
* **Unix philosophy**: Claude Code is composable and scriptable. `tail -f app.log | claude -p "Slack me if you see any anomalies appear in this log stream"` *works*. Your CI can run `claude -p "If there are new text strings, translate them into French and raise a PR for @lang-fr-team to review"`.
* **Enterprise-ready**: Use the Claude API, or host on AWS or GCP. Enterprise-grade [security](/en/security), [privacy](/en/data-usage), and [compliance](https://trust.anthropic.com/) is built-in.

## Next steps

<CardGroup>
  <Card title="Quickstart" icon="rocket" href="/en/quickstart">
    See Claude Code in action with practical examples
  </Card>

  <Card title="Common workflows" icon="graduation-cap" href="/en/common-workflows">
    Step-by-step guides for common workflows
  </Card>

  <Card title="Troubleshooting" icon="wrench" href="/en/troubleshooting">
    Solutions for common issues with Claude Code
  </Card>

  <Card title="IDE setup" icon="laptop" href="/en/vs-code">
    Add Claude Code to your IDE
  </Card>
</CardGroup>

## Additional resources

<CardGroup>
  <Card title="Build with the Agent SDK" icon="code-branch" href="https://docs.claude.com/en/docs/agent-sdk/overview">
    Create custom AI agents with the Claude Agent SDK
  </Card>

  <Card title="Host on AWS or GCP" icon="cloud" href="/en/third-party-integrations">
    Configure Claude Code with Amazon Bedrock or Google Vertex AI
  </Card>

  <Card title="Settings" icon="gear" href="/en/settings">
    Customize Claude Code for your workflow
  </Card>

  <Card title="Commands" icon="terminal" href="/en/cli-reference">
    Learn about CLI commands and controls
  </Card>

  <Card title="Reference implementation" icon="code" href="https://github.com/anthropics/claude-code/tree/main/.devcontainer">
    Clone our development container reference implementation
  </Card>

  <Card title="Security" icon="shield" href="/en/security">
    Discover Claude Code's safeguards and best practices for safe usage
  </Card>

  <Card title="Privacy and data usage" icon="lock" href="/en/data-usage">
    Understand how Claude Code handles your data
  </Card>
</CardGroup>

## Documentation Links (Fetched from llms.txt)

- [Claude Code on Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock.md): Learn about configuring Claude Code through Amazon Bedrock, including setup, IAM configuration, and troubleshooting.
- [Analytics](https://code.claude.com/docs/en/analytics.md): View detailed usage insights and productivity metrics for your organization's Claude Code deployment.
- [Checkpointing](https://code.claude.com/docs/en/checkpointing.md): Automatically track and rewind Claude's edits to quickly recover from unwanted changes.
- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web.md): Run Claude Code tasks asynchronously on secure cloud infrastructure
- [CLI reference](https://code.claude.com/docs/en/cli-reference.md): Complete reference for Claude Code command-line interface, including commands and flags.
- [Common workflows](https://code.claude.com/docs/en/common-workflows.md): Learn about common workflows with Claude Code.
- [Manage costs effectively](https://code.claude.com/docs/en/costs.md): Learn how to track and optimize token usage and costs when using Claude Code.
- [Data usage](https://code.claude.com/docs/en/data-usage.md): Learn about Anthropic's data usage policies for Claude
- [Claude Code on desktop](https://code.claude.com/docs/en/desktop.md): Run Claude Code tasks locally or on secure cloud infrastructure with the Claude desktop app
- [Development containers](https://code.claude.com/docs/en/devcontainer.md): Learn about the Claude Code development container for teams that need consistent, secure environments.
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions.md): Learn about integrating Claude Code into your development workflow with Claude Code GitHub Actions
- [Claude Code GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd.md): Learn about integrating Claude Code into your development workflow with GitLab CI/CD
- [Claude Code on Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai.md): Learn about configuring Claude Code through Google Vertex AI, including setup, IAM configuration, and troubleshooting.
- [Headless mode](https://code.claude.com/docs/en/headless.md): Run Claude Code programmatically without interactive UI
- [Hooks reference](https://code.claude.com/docs/en/hooks.md): This page provides reference documentation for implementing hooks in Claude Code.
- [Get started with Claude Code hooks](https://code.claude.com/docs/en/hooks-guide.md): Learn how to customize and extend Claude Code's behavior by registering shell commands
- [Identity and Access Management](https://code.claude.com/docs/en/iam.md): Learn how to configure user authentication, authorization, and access controls for Claude Code in your organization.
- [Interactive mode](https://code.claude.com/docs/en/interactive-mode.md): Complete reference for keyboard shortcuts, input modes, and interactive features in Claude Code sessions.
- [JetBrains IDEs](https://code.claude.com/docs/en/jetbrains.md): Use Claude Code with JetBrains IDEs including IntelliJ, PyCharm, WebStorm, and more
- [Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance.md): Legal agreements, compliance certifications, and security information for Claude Code.
- [LLM gateway configuration](https://code.claude.com/docs/en/llm-gateway.md): Learn how to configure Claude Code to work with LLM gateway solutions. Covers gateway requirements, authentication configuration, model selection, and provider-specific endpoint setup.
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp.md): Learn how to connect Claude Code to your tools with the Model Context Protocol.
- [Manage Claude's memory](https://code.claude.com/docs/en/memory.md): Learn how to manage Claude Code's memory across sessions with different memory locations and best practices.
- [Claude Code on Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry.md): Learn about configuring Claude Code through Microsoft Foundry, including setup, configuration, and troubleshooting.
- [Model configuration](https://code.claude.com/docs/en/model-config.md): Learn about the Claude Code model configuration, including model aliases like `opusplan`
- [Monitoring](https://code.claude.com/docs/en/monitoring-usage.md): Learn how to enable and configure OpenTelemetry for Claude Code.
