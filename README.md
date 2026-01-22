<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/flai-logo-dark.svg?v=2" />
    <source media="(prefers-color-scheme: light)" srcset="images/flai-logo-light.svg?v=2" />
    <img width="180" alt="flAI Logo" src="images/flai-logo-dark.svg?v=2" />
</picture>
  <br/>
  <br/>
  <a href="https://flai.gh.nos.pt/">https://flai.gh.nos.pt</a>
</p>

# Build applications with GitHub Copilot agent mode

<!-- ![](../../actions/workflows/0-start-course.yml/badge.svg?branch=main) -->
<img src="https://github.com/user-attachments/assets/1b3ea5df-f18d-4ed8-9ae6-f96dc1861818" alt="octofit-tracker" width="300"/>

_Build an application with GitHub Copilot agent mode in less than an hour._

## Welcome

People love how GitHub Copilot helps them write code faster and with fewer errors.
But what if GitHub could create a multi-tier application with a presentation, logic, and data layers based on requirements written in natural language?
In this exercise, we will prompt GitHub Copilot agent mode to create a complete application.

- **Who is this for**: Intermediate developers familiar with GitHub Copilot, basic GitHub, and basic web development
- **What you'll learn**: We'll introduce GitHub Copilot agent mode and how to use it for application development.
- **What you'll build**: You'll use GitHub Copilot agent mode to create a fitness application as the gym teacher of a high school.
- **Prerequisites**: Skills Exercise: <a href="https://github.com/nosportugal/flai-workshop-github-copilot-100">Getting Started with GitHub Copilot</a>.
- **How long**: This course takes less than one hour to complete.

## Application Architecture

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#4a90d9', 'primaryTextColor': '#fff', 'primaryBorderColor': '#2d5a87', 'lineColor': '#5c6bc0', 'secondaryColor': '#81c784', 'tertiaryColor': '#fff3e0'}, 'flowchart': {'nodeSpacing': 50, 'rankSpacing': 80, 'padding': 40}}}%%
flowchart LR
    User((👤 User))
    
    subgraph Codespaces [☁️ GitHub Codespaces]
        subgraph App [🏋️ OctoFit Tracker App]
            Frontend[⚛️ React<br/>Frontend]
            Backend[🐍 Django<br/>Backend]
            Database[(🍃 MongoDB<br/>Database)]
        end
    end
    
    User --> Frontend
    Frontend <--> Backend
    Backend <--> Database
    
    style User stroke-width:3px
    style Frontend stroke-width:3px,fill:#b3e5fc,color:#000
    style Backend stroke-width:3px,fill:#c8e6c9,color:#000
    style Database stroke-width:3px,fill:#ffe0b2,color:#000
    style Codespaces stroke-width:3px
    style App stroke-width:3px,stroke:#ff6b35
    
    linkStyle default stroke-width:3px
```

In this exercise, you will:

1. Start up a preconfigured development environment for making a multi-tier application.
1. Prompt in GitHub Copilot Chat and select the edit tab and select agent mode from the edit/agent drop-down.
1. In this exercise I primarily used the latest default LLM.
1. Try other LLM models to see other output.
1. For each step open up a new Copilot Chat session by hitting the plus `+` icon in the Copilot Chat pane.

### How to start this exercise

Simply copy the exercise to your account, then give your favorite Octocat (Mona) **about 20 seconds** to prepare the first lesson, then **refresh the page**.

[![](https://img.shields.io/badge/Copy%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/new?template_owner=nosportugal&template_name=flai-workshop-github-copilot-800&owner=%40me&name=flai-workshop-github-copilot-800&description=Exercise:+Build+applications+with+GitHub+Copilot+agent+mode&visibility=public)

<details>
<summary>Having trouble? 🤷</summary><br/>

When copying the exercise, we recommend the following settings:

- For owner, choose your personal account or an organization to host the repository.

- We recommend creating a public repository, since private repositories will use Actions minutes.

If the exercise isn't ready in 20 seconds, please check the "Actions" tab of your repository (or visit `https://github.com/<YOUR-USERNAME>/<YOUR-REPO>/actions`).

- Check to see if a job is running. Sometimes it simply takes a bit longer.

- If the page shows a failed job, please submit an issue. Nice, you found a bug! 🐛

</details>

---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)
