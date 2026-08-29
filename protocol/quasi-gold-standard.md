# Quasi-gold standard (declared before the first search was run)

Petersen et al. (2015) list "use a test set of known papers" among the actions
that evaluate whether a search string works. These ten records were named from
prior knowledge of the field **before** any query was executed, and the search
string is scored by how many of them it retrieves. They are not seeds: no query
was written to match a title on this list.

| # | Record | Loop component it is known for |
|---|---|---|
| 1 | ReAct: Synergizing Reasoning and Acting in Language Models | interleaved reason/act iteration |
| 2 | Reflexion: Language Agents with Verbal Reinforcement Learning | verbal self-feedback across attempts |
| 3 | Self-Refine: Iterative Refinement with Self-Feedback | generator/critic refinement |
| 4 | Tree of Thoughts: Deliberate Problem Solving with LLMs | search over the iteration space |
| 5 | Language Agent Tree Search (LATS) | search + evaluation + reflection |
| 6 | Voyager: An Open-Ended Embodied Agent with LLMs | curriculum, skill persistence |
| 7 | AutoGen: Multi-Agent Conversation Framework | orchestration topology |
| 8 | CRITIC: LLMs Can Self-Correct with Tool-Interactive Critiquing | external verification |
| 9 | Generative Agents: Interactive Simulacra of Human Behavior | memory, reflection, scheduling |
| 10 | Large Language Models Cannot Self-Correct Reasoning Yet | negative result on self-verification |

Recall against this set is reported in the manuscript. A miss is reported as a
miss; the list is not revised after the fact.
