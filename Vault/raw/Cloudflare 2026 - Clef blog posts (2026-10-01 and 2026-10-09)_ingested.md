Source: https://blog.cloudflare.com/clef-decision-models and https://blog.cloudflare.com/clef-faster-cheaper-multimodal (article text extracted from HTML; site navigation removed) — retrieved 2026-10-10

# Post 1: https://blog.cloudflare.com/clef-decision-models

October 1, 2026
Introducing Clef: our open-source decision models, and new RL fine-tuning platform
Michelle Chen
,
Alex Reneau
,
 and 
Kevin Flansburg
10 minute read
COPY URL
Over the last few weeks, there has been lots of buzz around decision models such as 
Typesafe AI’s Jev
 System One model. While classifier models have been around for some time, Jev introduces a new decision model concept into the world of AI — a model that produces bounded structured outputs cheaply, quickly and consistently that can be added into a workflow when a decision is required. These models are capable enough to work over any set of inputs without constantly retraining the model to incorporate new classification categories. This contrasts with the world of Large Language Models (LLMs), which are largely non-deterministic, but are open-ended enough to reason and generate text and tool calls for agentic workloads. 
Today, we’re releasing two Cloudflare-trained decision models, Clef and Clef-flash, 
hosted on Workers AI
. Clef is currently the leader when evaluated against the 
Jev Decision Index
, you can view full results on the 
live benchmark demo site
. These models are smarter, faster, and fully Jev-API compatible, so you can experiment with these hosted models easily. We’re fully open-sourcing these 
models on Hugging Face
 under an Apache 2.0 license for you to run locally and experiment with yourselves. 
Lastly, we’re excited to debut our new reinforcement learning (RL) product, which allows customers to fine-tune Clef to suit their use cases as well.
What is a decision model?
A decision model makes classifications to help agents decide how to act, based on certain probabilities. For example, you can pass in a customer support message (inputs) and ask if it is urgent and which team should handle it. A decision model will return typed answers with probabilities (outputs), which your code can use to route the ticket, trigger an escalation, or defer to a human. This means that a human does not necessarily need to be in the loop for agentic decisions anymore — agents can programmatically gather context, make decisions, and take actions on tasks, or defer to a human when needed.
Specifically at Cloudflare, we’ve been testing our new Clef model on our Threat Intelligence team to help us classify website domains. By giving a domain to Clef (with Browser Run) it can quickly identify categories that the domain falls under — for example, it might classify a domain with a 95% chance it is a fashion website, 85% ecommerce, <1% phishing, etc. This classification took our Clef model 2.2s to fetch, render, and classify the website. In contrast, our fastest general LLM gpt-oss-120b took 4.7s in the same workflow, and only returned two classifications. As a user, you can imagine how a 2x savings in latency and results can help us improve our threat intelligence workflows and be faster in identifying malicious or legitimate domains. Generalize this to any use case where you need to make quick programmatic decisions, and you unlock powerful agentic workflows that are able to autonomously decide, reason, and execute.
In music theory, a clef is a symbol placed at the beginning of a musical staff that assigns specific pitch names to the lines and spaces. A decision model is analogous to a music clef because it helps define the domain of the context and the subsequent notes (actions) that follow it. We chose Clef as the name of our family of decision models, as it serves similar purposes, and the CF hearkens to Cloudflare.
How is Clef different from other decision models?
Although the market is getting increasingly saturated with decision models, Clef has some unique properties that make us excited to release it to the public. First, it has a vision encoder so it’s able to take in images and classify visual content. This is different from Jev, which only does text classification today. Secondly, our model has a 64k context window (compared to Jev’s 32k), which allows users to squeeze more input state for the model to classify against.
Third, our model is accurate and powerful, scoring competitively against other decision models on the market across various quality benchmarks. We shortlisted some evaluations below that are important for decision-making as defined by the 
Jev Decision Index
 and scored some of the more popular models on the market for it. Check out the table below for benchmarks, or view the scores on our 
live decision index demo site
:
Benchmark
Clef
Clef-flash
Jev
DiffusionGemma Jev
Kev 9B
Laya
BFCL · case exact
98.47
98.76
95.75
96.52
94.51
38.13
ToolRet · nDCG@10
69.19
66.43
65.28
61.21
64.26
12.69
API-Bank · accuracy
91.93
93.11
88.19
83.66
56.30
11.41
Home appliances · case exact
82.95
97.73
52.27
42.05
25.00
0.00
When2Call · accuracy
72.37
65.58
80.97
75.44
49.62
11.94
BANKING77 · macro-F1
94.20
90.93
79.74
74.28
84.83
14.29
CLINC150+OOS · macro-F1
97.43
66.77
89.27
83.49
79.03
3.19
BRIGHT · nDCG@10
45.91
39.26
47.52
42.94
38.53
19.90
Amazon ESCI · macro-F1
57.48
57.39
55.21
53.37
49.22
24.40
PhishNChips · accuracy
79.60
75.05
62.55
85.35
50.75
50.15
We also ran benchmarks across 
Typesafe’s own eval suite
 and our Clef models fared well, beating Jev in 3 out of 4 areas. Notably, our Clef-flash performs exceptionally well, given how much faster it is.
Workflow
Clef
Clef-flash
Jev
Invoice processing
64.7
57.1
61.8
Customer service
76.3
77
76.0
Security incidents
62.9
61.7
61.7
Agent trace observability
68.5
69.8
71.6
Across the 43 eval benchmarks that we ran, our Clef models beat the decision models on latency (except for Laya which is very fast but trades off quality in the benchmarks above):
Benchmark
Clef
Clef-flash
Jev
DiffusionGemma Jev
Kev-9B
Laya
Median latency  · ms
209.3
38.8
524.1
84.4
51.4
5.8
p95 latency · ms
238.6
122.4
536.0
211.2
187.9
222.5
On top of the latency benefits from the model itself, our Clef models are hosted on Workers AI. Because they are hosted on Cloudflare’s infrastructure, we’re able to take advantage of our GPUs at the edge, leading to low network latency and faster decisions. This means that you could put Clef into the hot path for agents to make decisions and combine that with one of our LLMs on Workers AI to take action. 
curl
 https://api.cloudflare.com/client/v4/accounts/
$CLOUDFLARE_ACCOUNT_ID
/ai/run/@cf/cloudflare/clef
 \\
  -X
 POST
 \\
  -H
 "Authorization: Bearer 
$CLOUDFLARE_AUTH_TOKEN
"
 \\
  -d
 '{
    "model": "clef",
    "state": "Checkout has been failing for every customer for the last hour.",
    "questions": {
      "urgent": { "type": "noul", "instructions": "Is this support request urgent?" },
      "team": {
        "type": "choice",
        "instructions": "Which team should handle this request?",
        "criteria": {
          "billing": "Payments, invoices, and refunds",
          "technical": "Outages, errors, and configuration",
          "sales": "Plans and upgrades"
        }
      },
      "severity": {
        "type": "score",
        "instructions": "How severe is the customer impact?",
        "criteria": ["No impact", "Minor", "Major", "Critical"]
      }
    }
  }'
Clef also produces strictly typed outputs similar to Jev and is fully API-compatible, so you can make the swap extremely easily. The larger Clef model is your more powerful precision model, while the Clef-Flash model is great for latency-critical decisions. The models are enterprise-ready with our guarantee that we don’t read, store, or train on your requests or responses (unless you want to use our fine-tuning product, which we go into below). You can get started with the Clef models today, starting with our 
developer documentation
 or play around with the 
open-source model on the Hugging Face repo.
If you’d like help tuning Clef for a specific workload, we are also offering fine-tuning services — first as a hands-on partner with our forward-deployed engineer (FDE) team, and then later as a self-serve fine-tuning platform for customers to train and redeploy the model onto Cloudflare.
How we trained Clef
In the same week that Jev came out, we 
posted about some experiments
 we had with our own homegrown decision model. Our demo goes into how we adapted the DiffusionGemma model to output deterministic probabilities by exposing the logprobs that are generated by a large language model. Our initial approach built upon independent research by 
Matt Mastracci
, who has been active in the machine learning (ML) community with sharing new ideas and 
pull requests to vLLM
 inference engine to make DiffusionGemma support stronger.
Clef builds upon this concept, but uses a different base model as the backbone. We currently use Qwen as the base model and post-trained it to suit decision model use cases. During inference, Clef uses Qwen for a prefill-only pass, then scores the valid schema choices in parallel. The decision step is non-autoregressive, so there’s no intermediate text to generate token by token, making Clef significantly faster than autoregressive LLMs. Rather than generating intermediate text to produce structured answers, Clef and Clef-flash derive schema choices directly from internal backbone representations. This approach relies on a specialized two-stage attention routing process: every valid choice extracts context relevant to the prompt, allowing individual field parameters to cross-attend with other fields and back to the original payload prior to scoring. By leveraging a lexical prior, the model preserves semantic intent across options. Ultimately, the architecture unites option-specific evidence routing, joint cross-field attention, and schema-bound scoring.
By freezing Qwen3.8-27B for Clef and Qwen3.5-9B for Clef-flash, we jointly optimized the routing head alongside rank-256 low-rank adapters. Our post-training utilizes label-smoothed cross-entropy for valid schema outputs paired with a Brier loss to refine probability calibration. This training leverages our own internal synthetic datasets permutating field orders, prompts, and schema structures. We also developed Reinforcement Learning for Calibrated Decisions (RLCD) to serve as a secondary optimization target, granting partial credit to adjacent ordinal choices, rewarding fully precise record outputs, and applying a reference penalty to prevent distribution shift, giving us better accuracy and generalization.
This means that we were able to achieve a few novel things with Clef: we improved accuracy of the model in classification, constrained it to output only probabilities instead of text generation, and made it faster than Jev and the base Qwen models.
How fine-tuning can extend the capabilities of Clef
We heard a lot of internal use cases that required fine-tuning our Clef model to be built into our agentic workflows at Cloudflare. For example, internal teams want a classifier model to be able to evaluate Trust & Safety submissions, help us triage Cloudflare Support requests, or even to be built-in to our Bot products to decide if a crawler is a good bot or bad bot.
These use cases are incredibly specific and we have had many years of labelled decisions that we could use to train a specific classifier. When you fine-tune a model, you may give up some general purpose performance in exchange for higher accuracy in a specific domain.. Because Cloudflare has more than 15 years of network data across different domains, we can fine-tune a model to fit these specific use cases which is more accurate and faster than our generic Clef model. We’re working with internal teams already to figure out how we can post-train Clef to create powerful ML models that boost our impact and improve workflows across Cloudflare. These internal teams and use cases are the next remit of our new FDE fine-tuning team and basis for our reinforcement learning (RL) product.
Our new RL service
We are offering a service to help customers fine-tune Clef to suit their workloads with our hands-on FDE team. From that, we’ll learn from our hands-on experiences to build a self-serve platform that customers can use to capture data, fine-tune, and redeploy the model, all on Cloudflare.
This has actually been a long time coming — we’ve been building our AI platform to have the right primitives where we could be building a custom RL product. The interest in Jev shows the need for a fast, small, specific, classifier model, and we chose this to be our niche to start experimenting with RL environments.
To do this, we leverage the primitives that we already have built on our Cloudflare platform:
Cloudflare AI Gateway – pass all your AI traffic through AI Gateway and automatically create a dataset of requests for your use case
Cloudflare Workers AI – generate rollouts against the base Clef model
Cloudflare Containers – RL sandbox for scoring and replaying agent actions
[NEW] Trainer – update weights of fine-tuned Clef model
Cloudflare Workers AI + BYO Model – redeploy the fine-tuned model on Workers AI
This combines a few work-in-progress pieces of the AI Platform that we’ve been working on, including AI Gateway that captures your AI traffic so you can leverage your own request/response data, Containers for RL Sandboxes, and Workers AI’s Bring Your Own Model (Cog) work that has been progressing since our acquisition of Replicate. 
Try it out today
We’re excited to launch our first Cloudflare-trained ML model from the Workers AI team today. We’re still early here and have a lot more improvements in store, but it is a wonderful first showcase of the hard work we’ve been doing on the AI Platform team. We believe that Clef has the ability to disrupt the way we use agents, which fits naturally into Cloudflare’s mission of being the agent cloud.
If you have specific use cases and are already customers of these products — 
we’d love to chat with you and be design partners as we experiment in this space.
Try out the Clef models hosted on Workers AI, download the 
weights on Hugging Face 
if you’d like to explore for yourself, and reach out if you have fine-tuning use cases you’d like us to help with.
Our ML team has been growing in impact, from model optimizations to model training research. If you’re interested in joining our mission, 
check out our open roles
.

# Post 2: https://blog.cloudflare.com/clef-faster-cheaper-multimodal

October 9, 2026
Introducing Clef-omni with full multimodality, plus a faster Clef and a cheaper Clef-flash
Michelle Chen
,
Alex Reneau
,
 and 
Kevin Jain
7 minute read
COPY URL
Following last week’s 
release of Clef and Clef-flash
, Cloudflare’s open-weight decision models, we decided to bring forth more gifts. Today, we’re releasing Clef-omni, which takes in audio and video input alongside text and image. We also cut the price of Clef-flash so it is now cheaper than Jev, and we made Clef faster.
Although the model game is still early for Cloudflare, innovation and iteration is in our DNA, and we apply these principles to everything we do. In fact, the story of Clef came together over the course of less than a week. We decided we wanted to do something in the decision model space on a Friday evening, trained the model over the weekend, and launched it on Thursday. Even with such a short timeline, we were able to ship performant, high-quality, open-weight models for the community — imagine what more we can do in the future.
For today, we’re excited to keep up the momentum with new additions and improvements to our Clef family of models. This is just the beginning, and we’ll continue to get better, faster, cheaper, and more innovative.
Clef-omni takes audio, video, image, and text input
Our new Clef-omni model is able to take audio, video, image, and text input. This changes the paradigm for decision models, which have been largely text-only since the debut of Jev from TypeSafe. With Clef, we supported images and video frame arrays, but Clef-omni is able to take in audio (wav or mp3) and video (mp4 or webm) alongside text and images.
Instead of setting up cascading pipelines of models that transcribe speech-to-text, or splitting audio and image channels from video, you can just call one model to make decisions across any modality. We are now one step closer to a model that is able to interact with the world as we experience it — through audio, visual, and textual communication, all in one.
Check out our developer docs for the new 
Clef-omni
 model. We also released the model 
open-weights on HuggingFace
. For a quick start, here’s how you can send new modality inputs to Clef-omni:
curl https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai/run/@cf/cloudflare/clef-omni \
  -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "clef-omni",
    "state": "Review the installation: a photo of the unit, an audio recording of it running, and a video of the fan.",
    "images": ["data:image/png;base64,<base64-png>"],
    "audio": ["data:audio/mpeg;base64,<base64-mp3>"],
    "videos": ["data:video/mp4;base64,<base64-mp4>"],
    "questions": {
      "label_visible": {"type": "noul", "instructions": "Is the model and serial number label visible in the photo?"},
      "sounds_normal": {"type": "noul", "instructions": "Does the unit sound like it is running smoothly, without rattling or grinding?"},
      "fan_running": {"type": "noul", "instructions": "Is the fan running in the video?"}
    }
  }'
Clef-omni expands our open-weight decision architecture to natively handle multimodal workflows. We built this on a Qwen3-Omni-30B-A3B-Instruct mixture-of-experts (MoE) foundation, where the model was already capable of processing text, imagery, audio, and video directly within a single pipeline. However, we adopt the primary comprehension backbone while discarding the text-to-speech output components. In production, Clef-omni executes a quick prefill pass across the complete payload, scoring all modalities and valid parameter options simultaneously.
Because we skip output token generation since Clef models are not Large Language Models (LLMs), we remove the overhead of transcribing or captioning incoming files. Media elements map straight into the unified sequence, where video and audio are synced with visual frames for joint processing. Clef-omni then pulls candidate values directly from internal embeddings using our two-stage attention routing: every valid option gathers key evidence from the input (regardless if they are buried in text snippets, visual elements, or audio streams) before field vectors cross-attend across the full context to compute confidence scores. We add a built-in lexical grammar that preserves option semantics, so that we can deliver fast, schema-constrained scoring across every input type.
We train the model with the same techniques as we did with Clef — freezing the Qwen3 backbone, training low-rank adapters (LoRA), and applying our standard post-training approach: combining label-smoothed cross-entropy loss with Brier score calibration. The result is a model that is resilient and designed to succeed regardless of schema variations, field ordering, and prompt structures.
This brings several core upgrades to the Clef model family. Calibrated, schema-bound decisions now seamlessly handle text, images, audio, and synchronized video in a single API call. It's also fast. Text-only decisions return in about 130 ms at the median, image inputs in about 150 ms, and audio clips in a few hundred milliseconds. Even a full 21-second video clip with sound is scored in about 1.5 seconds, all in a single API call.
Our benchmarking shows strong performance across benchmarks, even with new modalities and MoE architecture.
Benchmark
Clef-omni
Clef
Clef-flash
Jev
BFCL · case exact
98.2
98.47
98.76
95.75
ToolRet · nDCG@10
66.6
69.19
66.43
65.28
API-Bank · accuracy
92.7
91.93
93.11
88.19
Home appliances · case exact
69.3
82.95
97.73
52.27
When2Call · accuracy
63.3
72.37
65.58
80.97
BANKING77 · macro-F1
94.8
94.20
90.93
79.74
CLINC150+OOS · macro-F1
97.7
97.43
66.77
89.27
BRIGHT · nDCG@10
42.0
45.91
39.26
47.52
Amazon ESCI · macro-F1
57.8
57.48
57.39
55.21
PhishNChips · accuracy
73.2
79.60
75.05
62.55
We also benchmarked against the 
TypeSafe evals
 to show how Clef-omni performs
.
Workflow
Metric
Clef-Omni
Clef
Clef-flash
Jev
Invoice processing
Exact actions
60.2
64.7
57.1
61.8
Invoice processing
Primary action
82.0
86.2
73.3
83.1
Customer service
Exact actions
71.6
76.3
77.0
76.0
Security incidents
Exact actions
61.7
62.9
61.7
61.7
Agent trace observability
Primary action
65.8
68.5
69.8
71.6
Clef-flash model is now cheaper
We heard your feedback — you want a decision model affordable enough to incorporate into any workflow. We’ve made a few optimizations and can now offer Clef-flash at cheaper prices. We want Clef to be able to make decisions that scale for you across all your agentic workflows, and now our pricing also incentivizes that.
We were able to optimize the model to the point where Clef-flash is now 
cheaper
 than Jev while still being performant and high-quality. Check out the 
developer docs
 for the most up-to-date pricing information at all times, including more detail on how image and audio modalities are converted to input tokens for pricing.
Clef-flash – originally $0.09 per M input tokens, now 
$0.038 per M input tokens
Clef – remains at 
$0.24 per M input tokens
Clef-omni – launched today at 
$0.15 per M input tokens
However, one trade-off we have to make in order to have cheaper pricing is to cut the context window of Clef-flash. The hosted version of Clef-flash now has a context window of 24k, instead of 64k as previously advertised. The model weights on Hugging Face are untouched and were trained to support a 256k context window should you choose to self-host it.
From our usage data, we see that only 0.24% of requests exceed 24k input tokens. Based on this data, we decided to make the call to drop the context window to 24k for Clef-flash in order to price it at a more accessible entry point. Our Clef model remains at a 64k context window, and we encourage folks with larger context needs to switch to Clef instead of Clef-flash.
Clef model is now faster
Speeds are also faster for the Clef model, with new optimizations to the hosted version of Clef on Workers AI. No new model weights are released because most of the optimizations we made are at the serving infrastructure layer, not materially to the model weights or architecture. Check out our new speeds below:
Input size
Before: median / p95 (ms)
Now: median / p95 (ms)
Median speedup
~800 tokens
262 / 438
152 / 351
1.7×
~3,400 tokens
616 / 777
305 / 531
2.0×
~16,000 tokens
2,721 / 3,250
1,635 / 1,805
1.7×
One of the optimizations we made was to move to SGLang for serving the model. We worked with the SGLang team and made pull requests to incorporate Clef (PR 
#42721
), which will be released in SGLang 0.5.22. You can also self-host Clef since we released the weights, and the new SGLang launch commands are available on our 
updated Hugging Face repo
 as well as the 
SGLang cookbooks
.
How are people using Clef?
At Cloudflare, we’ve had teams experimenting with Clef as a model that can help classify over general domains. The coolest thing about watching teams adopt Clef is that the capability to do detections and classifications have moved into the model layer, where it is accessible for anyone to start incorporating decision models into their use cases. Previously, even with zero-shot classifiers, the small models may not have been powerful enough to classify across any domain without further tuning. You might have needed to stand up a specialized machine learning team to help train over your particular domain, and gather a corpus of data in order to train a better model. Now, all you need to do is call a model to instantly parse through input data with precision.
A few highlights of how teams at Cloudflare are using Clef: Our public GitHub docs repo uses Clef to instantly 
detect and close spam issues
. EmDash, our content management system, 
moderates plugin libraries for phishing
. Our data loss prevention team is scanning data for potential personally identifiable information (PII) like government IDs. And our threat intelligence team is using Clef to help detect malicious domains.
Give it a try!
We’re excited to bring you more from the Clef family of models, including new modalities like audio and video, as well as making the model more accessible with cheaper pricing and faster speeds. Clef is fully Jev-API compatible and available via AI Gateway, so it is as simple as changing the model ID to try out Clef today. Check out our 
developer docs
 for more information.
Thank you for all the love and warm reception around Cloudflare’s first models — we are focused on bringing you more. Try out our Clef family of models, and tell us what you think.
