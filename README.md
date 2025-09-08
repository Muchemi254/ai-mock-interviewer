# AI Mock Interviewer 🤖🎤

A cloud-native AI-powered mock interview system that conducts timed interviews based on job descriptions and candidate CVs. Features real-time voice interaction, intelligent follow-up questions, comprehensive feedback, and hybrid local/cloud AI processing for optimal cost and performance.

## 🚀 Features

- **Real-time Voice Interaction**: WebSocket-based live interviews with STT/TTS capabilities
- **JD/CV Analysis**: Advanced parsing and matching of job descriptions and candidate CVs
- **Intelligent Question Generation**: Context-aware questions based on role requirements
- **Adaptive Follow-ups**: Dynamic follow-up questions based on candidate responses
- **Comprehensive Feedback**: Multi-dimensional scoring with personalized improvement plans
- **Hybrid AI Processing**: Local models for low-latency tasks, cloud LLMs for complex reasoning
- **Admin Dashboard**: System monitoring, prompt management, and analytics

## 🏗️ System Architecture

### Microservices Design

The system is built with 12 independent microservices:

- API Gateway & Authentication
- JD-CV Processor
- Question Engine
- Dialog Manager
- STT/TTS Gateway
- Follow-up Decision
- Feedback Service
- Media Service
- Analytics Service
- Vector DB Service
- Admin Service
- Notification Service

### Technology Stack

- **Frontend**: Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI + Pydantic + asyncio
- **Databases**: PostgreSQL, Qdrant, Redis
- **AI Models**: Whisper.cpp, Coqui TTS, Ollama, Google Gemini, OpenAI GPT
- **Infrastructure**: Kubernetes, Docker, Helm, Terraform
- **Monitoring**: Prometheus, Grafana, OpenTelemetry, Loki

## 📋 Development Progress

### Phase Completion Status

| Phase | Name                    |     Status     | Completion Date |
| ----- | ----------------------- | :------------: | --------------- |
| 0     | Foundation Setup        | 🚧 In Progress | -               |
| 1     | Core Content Processing |   ⏳ Pending   | -               |
| 2     | Question Intelligence   |   ⏳ Pending   | -               |
| 3     | Session Management      |   ⏳ Pending   | -               |
| 4     | Audio Processing        |   ⏳ Pending   | -               |
| 5     | Intelligence Services   |   ⏳ Pending   | -               |
| 6     | Analytics & Admin       |   ⏳ Pending   | -               |

**Overall Progress: 15%** (as of YYYY-MM-DD)

### Detailed Phase Status

#### ✅ Phase 0: Foundation Setup (Complete)

- [ ] Database schemas created and tested
- [X] Shared models and utilities available
- [X] Basic authentication working
- [X] Gemini client functional with simple test
- [X] Docker compose environment working

#### 🚧 Phase 1: Core Content Processing (In Progress - 40%)

- [ ] Basic file parsing (PDF, DOCX, TXT)
- [ ] Skill extraction using Gemini
- [ ] Embeddings generation and storage
- [ ] JD-CV matching algorithms

#### ⏳ Phase 2: Question Intelligence (Pending)

- [ ] Question generation with Gemini
- [ ] Question selection and time allocation algorithms
- [ ] Question bank management and templates
- [ ] Vector DB integration for semantic search

## 🛠️ Installation & Setup

[Detailed installation instructions will be added as the project progresses]

## 📚 API Documentation

[API documentation will be linked here as services are completed]

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/development/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions about this project, please open an issue or contact the development team.
