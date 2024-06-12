# PrivaSeer: A Large-Scale Privacy Policy Search Engine

PrivaSeer is a privacy policy search engine designed to address the lack of a publicly accessible large-scale privacy policy resource. It currently indexes 4 million privacy policies collected from the web, making it a comprehensive tool for privacy researchers and practitioners.

## Key Features:

- Search policies based on policy text using various facets such as sector of commerce, policy vagueness, policy readability, tracking technology mentioned, regulatory bodies mentioned, and regulations or cross-border agreements mentioned in the policy text.
- Rank search results by the popularity of the website of the policy, relevance based on the query, and the probability that a document is a privacy policy.
- Designed specifically to support privacy research, making it a valuable tool for researchers in the field.

## Implementation Details
PrivaSeer is implemented as a Django project and uses Elasticsearch for indexing and searching privacy policies.

## Access PrivaSeer
Visit [PrivaSeer](https://privaseer.ist.psu.edu/) to access the search engine.

## Screenshots
![Landing Page](landing-page.png)
*Figure 1: Snapshot of the landing page of PrivaSeer*

![Search Results Page](resultspage.png)
*Figure 2: Snapshot of the search results page of PrivaSeer*

## Citation

```
@inproceedings{srinath2021privaseer,
  title={PrivaSeer: A Privacy Policy Search Engine},
  author={Srinath, Mukund and Sundareswara, Soundarya Nurani and Giles, C Lee and Wilson, Shomir},
  booktitle={International Conference on Web Engineering},
  pages={286--301},
  year={2021},
  organization={Springer}
}
```
