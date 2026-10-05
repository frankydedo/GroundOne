---
source_url: https://huggingface.co/datasets/lytang/C2D-and-D2C-MiniCheck
raw_source: https://huggingface.co/datasets/lytang/C2D-and-D2C-MiniCheck/raw/main/README.md
accessed: 2026-10-05
---

# Dataset card - MiniCheck C2D/D2C synthetic data (lytang/C2D-and-D2C-MiniCheck, Hugging Face)

---
configs:
- config_name: default
  data_files:
  - split: c2d
    path: data/c2d-*
  - split: d2c
    path: data/d2c-*
dataset_info:
  features:
  - name: claim
    dtype: string
  - name: doc
    dtype: string
  - name: label
    dtype: int64
  splits:
  - name: c2d
    num_bytes: 8932849
    num_examples: 7076
  - name: d2c
    num_bytes: 6868458
    num_examples: 7319
  download_size: 2288457
  dataset_size: 15801307
language:
- en
size_categories:
- 10K<n<100K
license: mit
---

# Usage

C2D and D2C sysnthetic data are used to train the MiniCheck models from the work ([GitHub Repo](https://github.com/Liyan06/MiniCheck)):

📃 **MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents** ([link](https://arxiv.org/pdf/2404.10774.pdf))


**C2D:** We start with any human-written claim statement. The goal is to generate synthetic documents that require models be able to check multiple facts in the claim against multiple sentences each.

**D2C:** We start with any human-written document to start with. The goal is to generate claims and pair them with portions of the human written document, which, once again, require multi-sentence, multi-fact reasoning to check the claims.