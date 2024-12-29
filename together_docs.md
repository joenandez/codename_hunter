Get up to speed with our API in one minute.

Together AI makes it easy to run leading open-source models using only a few lines of code.

## 

1\. Register for an account

[](https://docs.together.ai/docs/quickstart#1-register-for-an-account)

First, [register for an account](https://api.together.xyz/settings/api-keys) to get an API key. New accounts come with $1 to get started.

Once you've registered, set your account's API key to an environment variable named `TOGETHER_API_KEY`:

```
<p><span>export</span> <span>TOGETHER_API_KEY</span><span>=</span>xxxxx
</p>
```

## 

2\. Install your preferred library

[](https://docs.together.ai/docs/quickstart#2-install-your-preferred-library)

Together provides an official library for Python and TypeScript, or you can call our HTTP API in any language you want:

## 

3\. Run your first query against a model

[](https://docs.together.ai/docs/quickstart#3-run-your-first-query-against-a-model)

Choose a model to query. In this example, we'll do a chat completion on Llama 3.1 8B with streaming:

```
<p><span>from</span> <span>together</span> <span>import</span> <span>Together</span>

<span>client</span> <span>=</span> <span>Together</span>()

<span>stream</span> <span>=</span> <span>client</span>.<span>chat</span>.<span>completions</span>.<span>create</span>(
  <span>model</span><span>=</span><span>"meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"</span>,
  <span>messages</span><span>=</span>[{<span>"role"</span>: <span>"user"</span>, <span>"content"</span>: <span>"What are the top 3 things to do in New York?"</span>}],
  <span>stream</span><span>=</span><span>True</span>,
)

<span>for</span> <span>chunk</span> <span>in</span> <span>stream</span>:
  <span>print</span>(<span>chunk</span>.<span>choices</span>[<span>0</span>].<span>delta</span>.<span>content</span> <span>or</span> <span>""</span>, <span>end</span><span>=</span><span>""</span>, <span>flush</span><span>=</span><span>True</span>)
</p>
```

Congratulations – you've just made your first query to Together AI!

## [](https://docs.together.ai/docs/quickstart#next-steps)

-   Explore [our cookbook](https://github.com/togethercomputer/together-cookbook) for Python recipes with Together AI
-   Explore [our demos](https://together.ai/demos) for full-stack open source example apps.
-   Check out the [Together AI playground](https://api.together.xyz/playground) to try out different models.
-   See [our integrations](https://docs.together.ai/docs/integrations) with leading LLM frameworks.

## [](https://docs.together.ai/docs/quickstart#resources)

-   [Discord](https://discord.com/invite/9Rk6sSeWEG)
-   [Pricing](https://www.together.ai/pricing)
-   [Support](https://www.together.ai/contact)

Updated about 1 month ago

___

-   [Table of Contents](https://docs.together.ai/docs/quickstart#)
-   -   [1\. Register for an account](https://docs.together.ai/docs/quickstart#1-register-for-an-account)
    -   [2\. Install your preferred library](https://docs.together.ai/docs/quickstart#2-install-your-preferred-library)
    -   [3\. Run your first query against a model](https://docs.together.ai/docs/quickstart#3-run-your-first-query-against-a-model)
    -   [Next steps](https://docs.together.ai/docs/quickstart#next-steps)
    -   [Resources](https://docs.together.ai/docs/quickstart#resources)