# CodeReviewAI

CodeReviewAI is a Python-based project designed to review and analyze code using GitHub and OpenAI APIs. 
This guide explains how to set up, run, and test the project using the `lets` CLI for streamlined commands.

---

### Part 1.

## Requirements

Ensure the following tools are installed on your system:

- **Docker**: [Installation Guide](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Installation Guide](https://docs.docker.com/compose/install/)
- **lets CLI**: [Installation Guide](https://lets-cli.org/docs/installation/)
- **Python**: Version 3.13 (if not using Docker)

---

## Project Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/xx1y-arch/codereviewai
   cd app

2. **Set Up Environment Variables**: \
  Create a .env file in the root of the project with the following content
   ```bash
   GITHUB_API_KEY=<your_github_api_key>
   OPENAI_API_KEY=<your_openai_api_key>

3. **Run commands using LETS CLI**
    ```bash
    lets run   # run app
    lets test  # run tests

____

### Part 2. What if.

1. **Database and Caching** \
Database: Use a high-performance database like PostgreSQL/Aurora[sql] or DynamoDB/MongoDB[nosql], optimized for handling concurrent requests and transactions.
- Sharding can be used to distribute load across multiple instances. 
- Implement replication (master-slave or read-only replicas) to distribute read traffic and ensure high availability. \
Caching: Implement caching with Redis/Memorycache to store intermediate results, such as file metadata, analysis results, or frequently accessed repository data. \
This reduces redundant API calls to GitHub and OpenAI.

2. **Asynchronous Task Processing** \
Offload the review requests to a task queue system like Celery (with Redis(pubsub/sorted sets) or RabbitMQ as the broker) or AWS SQS. Workers will process tasks asynchronously, ensuring the system can handle spikes in traffic.
Prioritize tasks based on urgency, such as large repositories or "VIP" users, and ensure retries in case of failures.

3. **Rate Limit Handling** \
GitHub API: Use pagination to fetch large repositories incrementally. Respect the API rate limits by implementing exponential backoff and inspecting the X-RateLimit-Reset header to schedule retries.
OpenAI API: Batch file analysis whenever possible to reduce the number of API calls. Monitor usage and provision multiple API keys/accounts if allowed, to distribute load.

4. **Infrastructure Scaling** [Scalability] \
Deploy the system on a Kubernetes/AWS ECS cluster to scale pods dynamically based on CPU/memory utilization or queue length.

5. **Cost Management** [Cost] \
Monitor usage with tools like Prometheus to optimize spending with the help of different kinds of metrics .
Use FaaS solutions like AWS Lambda for non-persistent tasks, minimizing costs during low traffic.

6. **Error Handling and Observability** [Realibility] \
Set up distributed tracing (e.g., with OpenTelemetry, Jaeger) to monitor and debug system performance.
Use centralized logging and tools like ELK Stack or Grafana to track failures and to set alerts, especially when API rate limits are exceeded.
