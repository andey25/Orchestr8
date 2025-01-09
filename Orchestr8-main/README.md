# Orchestr8
Orchestr8 is the first-ever orchestration framework for managing a fleet of parallel devin workers. We break a github repository down into a set of isolated github issues that can be solved concurrently and then optimally assign issues to each worker to minimize the mean completion time and maximize bandwidth. This is achieved through a sophisticated server mechanism that dynamically routes tasks to worker Devin nodes, ensuring optimal utilization of resources and faster delivery of results.

- We tried to solve some of the biggest pain points that people experience using devin:
    - It can be slow - our system can 10x speed through parallelization
    - It can fail - our system support automatic retries for failed jobs (+ ReAct reflection to improve reasoning)
    



