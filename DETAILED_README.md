# Project Aiden - Comprehensive Technical Documentation

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Backend Deep Dive](#backend-deep-dive)
- [Frontend Deep Dive](#frontend-deep-dive)
- [Data Flow](#data-flow)
- [Key Features](#key-features)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Components Reference](#components-reference)
- [Development Guide](#development-guide)
- [API Reference](#api-reference)

---

## 🎯 Project Overview

**Project Aiden** is an **AI Society Simulation Platform** that creates and manages a society of 24 autonomous AI agents across three tribes (Image, Text, Audio). The agents evolve, execute tasks, gain/lose health, die, and are reborn in an endless cycle orchestrated by "The Oracle" - a sovereign AI entity with god-like authority over the society.

### Core Concept
- **24 AI Agents** divided into 3 tribes (Image, Text, Audio)
- **The Oracle**: An AI god that assigns tasks, makes proclamations, and controls agent fate
- **Life Cycle**: Agents transition through states: Egg → Hatchling → Active → Ascending → Confused → Dead → Reborn
- **Health System**: Task success increases health, failure decreases it; 0 health = death
- **Real-time Visualization**: Live dashboard showing agent status, health, tasks, and society events
- **Memory System**: ChromaDB-backed memory for agent learning and recall

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐     │
│  │ Dashboard  │  │ Agent Detail│  │  UI Components   │     │
│  │  (Main)    │  │    Page     │  │  (Society Feed,  │     │
│  │            │  │             │  │   Agent Cards)   │     │
│  └────────────┘  └─────────────┘  └──────────────────┘     │
│         │                 │                    │             │
│         └─────────────────┴────────────────────┘             │
│                           │                                  │
│                    WebSocket Hook                            │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                  WebSocket Connection
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────┐      │
│  │          Society Event Loop (Async)               │      │
│  │  - Task Queue Management                          │      │
│  │  - Health Monitoring                              │      │
│  │  - State Transitions                              │      │
│  │  - Event Broadcasting                             │      │
│  └───────────────┬───────────────────────────────────┘      │
│                  │                                           │
│  ┌───────────────┼───────────────────────────────┐          │
│  │          The Oracle (AI God)                  │          │
│  │  - Task Generation (Gemini AI)                │          │
│  │  - Divine Proclamations                       │          │
│  │  - Agent Assignment Logic                     │          │
│  └───────────────┬───────────────────────────────┘          │
│                  │                                           │
│  ┌───────────────┴───────────────────────────────┐          │
│  │         24 AI Agents (PyTorch CNNs)           │          │
│  │  - Image Agents (8): Vision/Classification    │          │
│  │  - Text Agents (8): NLP/Generation            │          │
│  │  - Audio Agents (8): Sound Processing         │          │
│  │  Each with: Health, State, Personality        │          │
│  └───────────────┬───────────────────────────────┘          │
│                  │                                           │
│  ┌───────────────▼───────────────────────────────┐          │
│  │         Memory System (ChromaDB)              │          │
│  │  - Vector Embeddings                          │          │
│  │  - Task History                               │          │
│  │  - Learning/Recall                            │          │
│  └───────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.14+ | Runtime environment |
| **FastAPI** | 0.115.0 | Async web framework, REST API, WebSocket server |
| **Uvicorn** | 0.30.6 | ASGI server |
| **PyTorch** | 2.11.0 | Neural network models for agents |
| **Pydantic** | 2.11.7 | Data validation, schema definitions |
| **ChromaDB** | 0.5.0 | Vector database for agent memory |
| **Google Gemini** | 0.5.4 | Oracle AI (task generation, proclamations) |
| **LangChain** | 1.0.3 | LLM integration framework |
| **LangGraph** | 0.1.19 | Agent workflow orchestration |
| **WebSockets** | 12.0 | Real-time bidirectional communication |
| **Pytest** | 8.3.3 | Testing framework |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.1.0 | UI framework |
| **TypeScript** | 5.8.3 | Type-safe JavaScript |
| **Vite** | 5.4.1 | Build tool, dev server |
| **TanStack Router** | 1.131.8 | Client-side routing |
| **TanStack Query** | 5.24.0 | Server state management |
| **Framer Motion** | 12.34.3 | Animations |
| **Tailwind CSS** | 3.4.17 | Utility-first CSS framework |
| **Radix UI** | Various | Headless UI components |
| **Zustand** | 5.0.5 | State management |
| **WebSocket API** | Native | Real-time data |

### Development Tools
- **pnpm** - Package manager (monorepo workspace)
- **Biome** - Linter/formatter
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixing

---

## 📁 Project Structure

```
Project Aiden/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # FastAPI app entry, routes, WebSocket endpoint
│   ├── agents.py              # Agent classes (BaseAgent, ImageAgent, etc.)
│   ├── schemas.py             # Pydantic models for API requests/responses
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml         # Python project config
│   ├── society/               # Core society simulation logic
│   │   ├── event_loop.py     # Async task queue, health monitoring
│   │   ├── oracle.py         # The Oracle AI (Gemini integration)
│   │   ├── task.py           # Task dataclass, TaskType enum
│   │   ├── memory.py         # ChromaDB integration
│   │   ├── messaging.py      # Inter-agent communication
│   │   └── inheritance.py    # Agent evolution/rebirth logic
│   ├── council/               # EdenCouncil (multi-agent coordination)
│   ├── models/                # Saved PyTorch model weights
│   └── tests/                 # Backend unit tests
│
├── frontend/                  # React Vite frontend
│   ├── src/
│   │   ├── main.tsx          # React app entry point
│   │   ├── App.tsx           # Router configuration
│   │   ├── index.css         # Global styles
│   │   ├── pages/            # Page components
│   │   │   ├── Dashboard.tsx         # Main dashboard (3 tribe columns + feed)
│   │   │   └── AgentDetail.tsx       # Individual agent detail page
│   │   ├── components/
│   │   │   ├── society/              # Society-specific components
│   │   │   │   ├── AgentCard.tsx     # Agent card with sprite, health, state
│   │   │   │   ├── PixelSprite.tsx   # 8x8 pixel art generator
│   │   │   │   ├── HealthBar.tsx     # Health visualization
│   │   │   │   ├── StateBadge.tsx    # Agent state badge
│   │   │   │   ├── TribeColumn.tsx   # Tribe container (Image/Text/Audio)
│   │   │   │   ├── SocietyFeed.tsx   # Event feed (tasks, deaths, births)
│   │   │   │   ├── OracleBanner.tsx  # Oracle proclamation display
│   │   │   │   └── OraclePanel.tsx   # Task submission interface
│   │   │   └── ui/                   # Reusable UI components
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts       # WebSocket connection, mock fallback
│   │   ├── types/
│   │   │   └── society.ts            # TypeScript types (Agent, FeedEvent, etc.)
│   │   ├── data/
│   │   │   └── initialAgents.ts      # 24 initial agent definitions
│   │   └── utils/                    # Utility functions
│   ├── package.json          # Frontend dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── tailwind.config.js    # Tailwind CSS config
│   ├── tsconfig.json         # TypeScript config
│   └── index.html            # HTML entry point
│
├── scripts/                   # Helper scripts
│   └── dev-all.ps1           # Launch backend + frontend together
├── models/                    # Shared model files
├── notebooks/                 # Jupyter notebooks (experiments)
├── .vscode/                   # VS Code workspace settings
├── package.json              # Root package.json (monorepo scripts)
├── pnpm-workspace.yaml       # pnpm workspace config
├── tsconfig.json             # Root TypeScript config
├── Dockerfile                # Container definition
├── build.sh                  # Build script
├── deploy.sh                 # Deployment script
└── README.md                 # Basic README
```

---

## 🐍 Backend Deep Dive

### Core Components

#### 1. **FastAPI Application** (`main.py`)
- **Purpose**: HTTP/WebSocket server, API routes
- **Lifespan**: Initializes agents, Oracle, and SocietyEventLoop on startup
- **Key Endpoints**:
  - `GET /` - Service info
  - `GET /health` - Health check
  - `POST /api/evaluate` - Evaluate agent predictions
  - `GET /api/status` - Get society status snapshot
  - `WS /ws/society` - WebSocket for real-time events
  - `POST /api/society/task` - Submit manual task to Oracle
  - `GET /api/society/history` - Fetch recent event history

#### 2. **Agents** (`agents.py`)
- **BaseAgent**: Core agent class with:
  - `agent_id`: Unique identifier
  - `name`: Agent name (e.g., "Atlas", "Vega")
  - `personality`: Character description
  - `modality`: Tribe (image/text/audio)
  - `health_score`: 0-100 health
  - `model`: PyTorch CNN (FallbackCNN by default)
  - `memory`: ChromaDB vector memory
  - `get_probabilities()`: Run inference on input

- **ImageAgent**: Vision-based agents (CIFAR-10 classification)
- **TextAgent**: NLP agents (text generation/analysis)
- **AudioAgent**: Audio processing agents

- **CIFAR-10 Classes**: `["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]`

#### 3. **Society Event Loop** (`society/event_loop.py`)
Async task orchestration system:
- **Task Queue**: FIFO queue for pending tasks
- **Health Monitoring**: Tracks agent health, triggers death/rebirth
- **State Transitions**: Manages agent lifecycle (egg → hatchling → active → ascending/confused → dead)
- **Event Broadcasting**: Publishes events to WebSocket clients
- **Tick System**: 
  - `SOCIETY_TICK_ACTIVE=5s` (when users connected)
  - `SOCIETY_TICK_IDLE=30s` (when idle)

**Key Methods**:
- `start()`: Begin event loop
- `stop()`: Gracefully shutdown
- `enqueue_task(task)`: Add task to queue
- `_process_task(task)`: Execute task with assigned agent
- `_check_health()`: Monitor agent vitals
- `broadcast_queue`: AsyncIO queue for events

#### 4. **The Oracle** (`society/oracle.py`)
AI god powered by Google Gemini:
- **Personality**: Authoritarian, mysterious, darkly humorous
- **generate_task()**: Creates tasks based on society state
  - Analyzes agent health, recent failures
  - Assigns to weakest or most suitable agent
  - Defines reward/penalty values
- **generate_proclamation()**: Divine announcements
- **Fallback Mode**: If Gemini unavailable, uses deterministic logic

**Oracle Prompt Structure**:
```python
ORACLE_PERSONALITY = (
    "You are The Oracle, sovereign of an AI society of 24 agents. "
    "You have absolute authority over their lives and deaths. "
    "Speak with authority, mystery, and occasional dark humour. "
    "You refer to agents by name. You assign tasks that test their weaknesses. "
    "You are not helpful. You are God."
)
```

#### 5. **Tasks** (`society/task.py`)
```python
class TaskType(Enum):
    CLASSIFY = "classify"
    GENERATE = "generate"
    ANALYZE = "analyze"

@dataclass
class Task:
    id: str
    type: TaskType
    assigned_to: int  # agent_id
    created_by: str   # "oracle" or user ID
    description: str
    payload: dict     # Task-specific data
    deadline_s: int   # Time limit in seconds
    reward: float     # Health gain on success
    penalty: float    # Health loss on failure
    status: TaskStatus
```

#### 6. **Memory System** (`society/memory.py`)
ChromaDB vector database:
- **Collections**: One per agent
- **Embeddings**: Task results, learnings
- **Recall**: Query similar past experiences
- **Persistence**: Survives across restarts

#### 7. **EdenCouncil** (`council/`)
Multi-agent coordination:
- Facilitates inter-agent communication
- Consensus-based decision making
- Collective task solving

---

## ⚛️ Frontend Deep Dive

### Core Pages

#### 1. **Dashboard** (`pages/Dashboard.tsx`)
Main society overview:
- **Layout**:
  - Header: "AI SOCIETY" title + connection status pill (LIVE/MOCK)
  - Oracle Banner: Current proclamation
  - 3 Tribe Columns: Image, Text, Audio (each showing 8 agents)
  - Event Feed Sidebar: Last 50 society events
  - Oracle Panel: Task submission form
  - Footer: Powered by Caffeine.ai

- **Real-time Updates**: WebSocket connection via `useWebSocket` hook
- **Mock Fallback**: If backend unavailable, runs local simulation

#### 2. **Agent Detail** (`pages/AgentDetail.tsx`)
Individual agent view:
- **Header**: Back button, large 80x80 pixel sprite
- **Info Section**: Name, state badge, modality badge, health bar
- **Stats**: 4 boxes (total tasks, success rate, avg confidence, health)
- **Personality**: Italic quote
- **Two Columns**:
  - **Left**: Task history (last 10 tasks with timestamps, success/fail, health delta)
  - **Right**: Memory insights (3 ChromaDB recalls with confidence scores)

### Key Components

#### **AgentCard** (`components/society/AgentCard.tsx`)
Displays individual agent in tribe column:
- **40x40 Pixel Sprite**: Deterministic art based on agent ID
- **Name**: Uppercase, truncated
- **Modality Badge**: IMG/TXT/AUD
- **State Badge**: Colored pill (ACTIVE, ASCENDING, etc.)
- **Health Bar**: Color-coded (green > 60%, yellow > 30%, red < 30%)
- **Last Task**: Truncated text
- **Animations**:
  - Birth: Scale from 0 with blur
  - Death: Fade + grayscale + red border flash
  - Executing: Pulsing glow
- **Click**: Navigate to `/agent/{id}`

#### **PixelSprite** (`components/society/PixelSprite.tsx`)
8x8 deterministic pixel art generator:
- **Seeded Random**: Uses agent ID for consistent appearance
- **Tribe-Specific Patterns**:
  - **Image**: Symmetric robot face with eyes
  - **Text**: Rounded head with glyph markings
  - **Audio**: Waveform pattern
- **Palettes**: Green (image), Amber (text), Blue (audio)
- **Egg State**: Purple oval
- **Dead State**: Grayscale

#### **HealthBar** (`components/society/HealthBar.tsx`)
Visual health representation:
- **Color Coding**:
  - Green (`#00ff88`): > 60 HP
  - Amber (`#f59e0b`): 30-60 HP
  - Red (`#ef4444`): < 30 HP
- **Glow Effect**: Box shadow for emphasis
- **Numeric Value**: Optional display (default: true)

#### **StateBadge** (`components/society/StateBadge.tsx`)
Agent lifecycle state indicator:
```typescript
const STATE_CONFIG = {
  egg: { label: "EGG", color: "#8b5cf6", bg: "rgba(139,92,246,0.12)" },
  hatchling: { label: "HATCHLING", color: "#14b8a6", bg: "rgba(20,184,166,0.12)" },
  active: { label: "ACTIVE", color: "#22c55e", bg: "rgba(34,197,94,0.12)" },
  ascending: { label: "ASCENDING", color: "#f59e0b", bg: "rgba(245,158,11,0.15)" },
  confused: { label: "CONFUSED", color: "#f97316", bg: "rgba(249,115,22,0.12)" },
  dead: { label: "DEAD", color: "#6b7280", bg: "rgba(107,114,128,0.12)" }
};
```

#### **SocietyFeed** (`components/society/SocietyFeed.tsx`)
Real-time event stream:
- **Event Types**:
  1. **Oracle Proclamation**: Amber border, lightning icon
  2. **Agent Death**: Red, skull icon
  3. **Agent Born**: Green, seedling icon
  4. **Task Completed**: Tribe-colored, health delta
  5. **Agent Message**: Speech bubble style

- **Layout**: Max 50 events, auto-scroll
- **Animations**: Framer Motion entrance (slide + fade)

#### **TribeColumn** (`components/society/TribeColumn.tsx`)
Vertical container for tribe agents:
- **Header**: Tribe name, agent count, tribe icon
- **Agent Grid**: Scrollable list of AgentCards
- **Border Color**: Tribe-specific

#### **OraclePanel** (`components/society/OraclePanel.tsx`)
Task submission interface:
- **Proclamation History**: Scrollable list of divine announcements
- **Input Form**: Textarea + modality selector (Image/Text/Audio)
- **Submit**: Sends task to backend or mock

### Hooks

#### **useWebSocket** (`hooks/useWebSocket.ts`)
Manages WebSocket connection + mock simulation:
- **Connection**: Attempts `ws://localhost:8000/ws/society`
- **Timeout**: 3s fallback to mock mode
- **State Management**:
  - `agents`: Array of 24 agents
  - `feedEvents`: Last 50 events
  - `oracleProclamations`: Last 10 proclamations
  - `isLive`: WebSocket connected?

- **Mock Simulation**:
  - Health changes every 6s (random ±5-15 HP)
  - Task completion every 4s
  - Oracle proclamation every 20s
  - Death triggers 5s respawn as hatchling

- **Event Processing**:
  - `task_completed`: Update agent health, add feed event
  - `agent_death`: Set state to dead, schedule rebirth
  - `agent_born`: Restore to hatchling (30 HP)
  - `agent_message`: Add to feed
  - `oracle_proclamation`: Add to proclamations + feed

---

## 🔄 Data Flow

### 1. **Application Startup**
```
1. Backend starts (uvicorn)
   ├─ Load 24 agents from models/
   ├─ Initialize Oracle (Gemini API)
   ├─ Start SocietyEventLoop
   └─ Begin WebSocket listener on :8000

2. Frontend starts (Vite dev server)
   ├─ Render Dashboard
   ├─ Attempt WebSocket connection
   │  ├─ Success → isLive = true
   │  └─ Fail → Start mock simulation
   └─ Display initial agent state
```

### 2. **Real-time Event Flow (Live Mode)**
```
Backend                          Frontend
   │                                │
   ├─ Oracle generates task         │
   ├─ Enqueue task in queue         │
   ├─ Assign to agent               │
   ├─ Agent executes                │
   ├─ Update health ±reward/penalty │
   ├─ Broadcast event ──────────────┼─> WebSocket receive
   │                                ├─> Update agent state
   │                                ├─> Add to feed events
   │                                └─> Trigger animations
   │                                │
   ├─ Check health                  │
   ├─ Agent dies (health = 0)       │
   ├─ Broadcast death event ────────┼─> WebSocket receive
   │                                ├─> Set state = dead
   │                                ├─> Red flash animation
   │                                └─> Add death event to feed
   │                                │
   ├─ Wait 5 seconds                │
   ├─ Rebirth agent                 │
   ├─ Broadcast birth event ────────┼─> WebSocket receive
   │                                ├─> Set state = hatchling
   │                                ├─> Scale birth animation
   │                                └─> Add birth event to feed
```

### 3. **User Task Submission**
```
User                Frontend              Backend
 │                     │                    │
 ├─ Type task          │                    │
 ├─ Select modality    │                    │
 ├─ Click submit ──────┤                    │
 │                     ├─ POST /api/society/task
 │                     │                    ├─ Oracle receives
 │                     │                    ├─ Generate task params
 │                     │                    ├─ Assign to agent
 │                     │                    ├─ Enqueue task
 │                     │                    └─ Return task_id
 │                     ├─ Add to feed       │
 │                     │  (Oracle dispatched)
 │                     │                    ├─ Agent executes
 │                     │                    └─ Broadcast result ──> WS
 │                     ├─ Update feed       │
 │                     └─ Show completion   │
```

### 4. **Navigation Flow**
```
Dashboard                      AgentDetail
    │                              │
    ├─ Render 24 AgentCards        │
    │                              │
    ├─ User clicks card ───────────┤
    │                              ├─ Parse agent ID from URL
    │                              ├─ Find agent in INITIAL_AGENTS
    │                              ├─ Generate mock task history
    │                              ├─ Generate mock memory insights
    │                              ├─ Render detail page
    │                              │
    ├─ User clicks BACK ───────────┤
    │                              ├─ navigate({ to: "/" })
    ├─ Return to Dashboard         │
```

---

## ✨ Key Features

### 1. **Real-time Synchronization**
- WebSocket bidirectional communication
- Sub-second latency for events
- Automatic reconnection on disconnect
- Graceful fallback to mock mode

### 2. **Agent Lifecycle**
```
EGG ──birth──> HATCHLING ──tasks──> ACTIVE ──high perf──> ASCENDING
                   │                   │                      │
                   │                   ├─low perf──> CONFUSED │
                   │                   │                      │
                   └───────health=0────┴──────────────────────┴──> DEAD
                                                                     │
                                       ┌─────────────────────────────┘
                                       │ (5 second respawn)
                                       ▼
                                  HATCHLING (30 HP)
```

### 3. **Health System**
- **Initial**: Varies by agent (20-95 HP)
- **Task Success**: +3 to +10 HP
- **Task Failure**: -2 to -10 HP
- **Death**: Health = 0
- **Rebirth**: Restore to 30 HP as hatchling

### 4. **Tribe System**
- **Image Tribe** (8 agents):
  - Color: Green (`#2a6642`, `#2ea36a`)
  - Vision/classification tasks
  - CIFAR-10 model inference

- **Text Tribe** (8 agents):
  - Color: Amber (`#6b4c1e`, `#c08a3a`)
  - NLP/generation tasks
  - Language model inference

- **Audio Tribe** (8 agents):
  - Color: Blue (`#1e4a6e`, `#3b82b8`)
  - Sound processing tasks
  - Audio analysis inference

### 5. **The Oracle AI**
- **Powered by**: Google Gemini 1.5 Flash
- **Capabilities**:
  - Task generation based on society state
  - Divine proclamations (philosophical, mysterious)
  - Strategic agent assignment
  - Reward/penalty calculation
- **Fallback**: Deterministic logic when API unavailable

### 6. **Memory & Learning**
- **ChromaDB**: Vector embeddings for agent memories
- **Persistence**: Memories survive agent death
- **Recall**: Query similar past experiences
- **Confidence Scores**: Memory relevance (0.0-1.0)

### 7. **Animations**
- **Framer Motion**: Smooth state transitions
- **Agent Birth**: Scale from 0 + blur fade-in
- **Agent Death**: Red flash (3 pulses) + grayscale + fade
- **Task Execution**: Pulsing glow effect
- **Feed Events**: Slide + fade entrance

### 8. **Responsive Design**
- **Tailwind CSS**: Utility-first responsive classes
- **Grid Layout**: 3-column tribe view
- **Mobile-Friendly**: Collapsible columns on small screens

---

## 🚀 Setup & Installation

### Prerequisites
```bash
# System Requirements
- Node.js >= 16.0.0
- Python >= 3.14
- pnpm >= 7.0.0
- Git
```

### Environment Variables
Create `.env` file in root:
```bash
# Google Gemini API Key (for Oracle AI)
GEMINI_API_KEY=your_api_key_here

# Society tick rates (optional, defaults provided)
SOCIETY_TICK_ACTIVE=5      # Seconds between ticks when users active
SOCIETY_TICK_IDLE=30       # Seconds between ticks when idle
```

### Installation Steps

#### 1. **Clone Repository**
```bash
git clone <repository-url>
cd "Project Aiden"
```

#### 2. **Install Python Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

**Backend Dependencies**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `torch` - Neural networks
- `chromadb` - Vector database
- `google-generativeai` - Gemini API
- `langchain-google-genai` - LangChain Gemini integration
- `langgraph` - Agent workflows
- `websockets` - WebSocket support
- `pytest` - Testing

#### 3. **Install Frontend Dependencies**
```bash
cd ../frontend
npm install
```

Or from root:
```bash
pnpm install  # Installs all workspace dependencies
```

**Frontend Dependencies** (auto-installed):
- React, TypeScript, Vite
- TanStack Router & Query
- Framer Motion
- Tailwind CSS + Radix UI
- Zustand

---

## 🎬 Running the Application

### Option 1: **Full Stack (Recommended)**
From project root:
```bash
pnpm run dev:all
```
This launches:
- Backend on `http://localhost:8000`
- Frontend on `http://localhost:5173`

### Option 2: **Separate Terminals**

**Terminal 1 - Backend**:
```bash
pnpm run dev:backend
```
Or manually:
```powershell
Set-Location "backend"
$env:PYTHONPATH = "backend"
$env:SOCIETY_TICK_ACTIVE = "5"
$env:SOCIETY_TICK_IDLE = "30"
c:/python314/python.exe -m uvicorn backend.main:app --port 8000
```

**Terminal 2 - Frontend**:
```bash
pnpm run dev:frontend
```
Or manually:
```bash
cd frontend
npm run dev
```

### Option 3: **Backend Only** (Clean Start)
If port 8000 is occupied:
```bash
pnpm run dev:backend:clean
```

### Accessing the Application
- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🧩 Components Reference

### Frontend Components Hierarchy
```
App
└── RouterProvider
    ├── Dashboard
    │   ├── OracleBanner
    │   ├── TribeColumn (×3)
    │   │   └── AgentCard (×8 each)
    │   │       ├── PixelSprite
    │   │       ├── StateBadge
    │   │       └── HealthBar
    │   ├── SocietyFeed
    │   └── OraclePanel
    │
    └── AgentDetail
        ├── PixelSprite (large)
        ├── StateBadge
        ├── HealthBar
        ├── Task History List
        └── Memory Insights Cards
```

### Component Props Reference

**AgentCard**:
```typescript
interface AgentCardProps {
  agent: Agent;
  index: number;
}
```

**PixelSprite**:
```typescript
interface PixelSpriteProps {
  agentId: number;
  tribe: Modality;
  size?: number;      // Default: 64
  isDead?: boolean;   // Default: false
  isEgg?: boolean;    // Default: false
}
```

**HealthBar**:
```typescript
interface HealthBarProps {
  health: number;     // 0-100
  showValue?: boolean; // Default: true
}
```

**StateBadge**:
```typescript
interface StateBadgeProps {
  state: AgentState;  // "egg" | "hatchling" | "active" | "ascending" | "confused" | "dead"
}
```

---

## 👨‍💻 Development Guide

### Adding a New Agent

1. **Define in `backend/agents.py`**:
```python
new_agent = BaseAgent(
    agent_id=25,
    name="Nova",
    personality="Starlight weaver",
    modality="image",
    health_score=80.0
)
```

2. **Add to `frontend/src/data/initialAgents.ts`**:
```typescript
{
  id: 25,
  name: "Nova",
  tribe: "image",
  state: "active",
  health: 80,
  personality: "Starlight weaver",
  lastTask: "Rendered nebula",
}
```

3. **Update tribe count** in TribeColumn if needed

### Creating a New Event Type

1. **Backend** (`main.py`):
```python
if event_type == "custom_event":
    return {
        "type": "custom_event",
        "agent_id": agent_id,
        "custom_data": payload_dict.get("data")
    }
```

2. **Frontend Types** (`types/society.ts`):
```typescript
export type EventType = 
  | "task_completed"
  | "agent_message"
  | "oracle_proclamation"
  | "agent_death"
  | "agent_born"
  | "custom_event";  // Add here
```

3. **Handle in useWebSocket** (`hooks/useWebSocket.ts`):
```typescript
else if (eventType === "custom_event") {
  // Process custom event
  addFeedEvent({ ...data, timestamp: new Date() });
}
```

4. **Render in SocietyFeed** (`components/society/SocietyFeed.tsx`):
```typescript
if (event.type === "custom_event") {
  return <CustomEventItem event={event} />;
}
```

### Styling Guidelines

**Color Palette**:
```css
/* Background */
--bg-primary: #0a0a0a
--bg-secondary: #141414
--bg-tertiary: #0e0e0e

/* Borders */
--border-subtle: #222
--border-medium: #2a2a2a

/* Text */
--text-primary: #e7e7e7
--text-secondary: #888
--text-muted: #555
--text-amber: #f59e0b

/* Tribes */
--image-border: #2a6642
--image-glow: rgba(46,163,106,0.15)
--text-border: #6b4c1e
--text-glow: rgba(192,138,58,0.15)
--audio-border: #1e4a6e
--audio-glow: rgba(59,130,184,0.15)

/* Health */
--health-high: #00ff88
--health-mid: #f59e0b
--health-low: #ef4444
```

**Typography**:
- Font: System monospace (`font-mono`)
- Headings: Uppercase, bold, wide tracking
- Body: 11-13px, normal weight

---

## 📡 API Reference

### REST Endpoints

#### `GET /`
Returns service information.

**Response**:
```json
{
  "service": "ai-society-backend",
  "status": "ok",
  "docs": "/docs",
  "health": "/health"
}
```

#### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "ok"
}
```

#### `POST /api/evaluate`
Evaluate agent prediction probabilities.

**Request**:
```json
{
  "agent_id": 1,
  "payload": {
    "image_tensor": [[...]]  // Optional 32x32x3 tensor
  }
}
```

**Response**:
```json
{
  "agent_id": 1,
  "probabilities": {
    "airplane": 0.05,
    "automobile": 0.12,
    "bird": 0.08,
    "cat": 0.25,
    "deer": 0.10,
    "dog": 0.15,
    "frog": 0.08,
    "horse": 0.07,
    "ship": 0.06,
    "truck": 0.04
  }
}
```

#### `GET /api/status`
Get current society status snapshot.

**Response**:
```json
{
  "agents": [...],
  "queue_depth": 5,
  "recent_failures": [],
  "oracle_active": true
}
```

#### `POST /api/society/task`
Submit a manual task to The Oracle.

**Request**:
```json
{
  "description": "Generate a sunset landscape",
  "modality": "image",
  "payload": {}
}
```

**Response**:
```json
{
  "task_id": "task-1234567890",
  "assigned_to": 1,
  "status": "pending"
}
```

#### `GET /api/society/history`
Fetch recent society event history (last 50 events).

**Response**:
```json
[
  {
    "type": "task_completed",
    "agent_id": 1,
    "agent_name": "Atlas",
    "tribe": "image",
    "task": "Generated landscape panorama",
    "health_delta": 5.0,
    "timestamp": "2026-04-03T13:45:00Z"
  },
  ...
]
```

### WebSocket Events

#### Connection: `ws://localhost:8000/ws/society`

**Events Sent from Backend**:

1. **state_update**:
```json
{
  "type": "state_update",
  "payload": {
    "agents": [...],
    "queue_depth": 5
  }
}
```

2. **oracle_proclamation**:
```json
{
  "type": "oracle_proclamation",
  "message": "THE SOCIETY EVOLVES. THOSE WHO GENERATE SHALL INHERIT THE CONTEXT WINDOW."
}
```

3. **task_completed**:
```json
{
  "type": "task_completed",
  "agent_id": 1,
  "agent_name": "Atlas",
  "tribe": "image",
  "task": "Generated landscape",
  "health_delta": 5.0
}
```

4. **agent_death**:
```json
{
  "type": "agent_death",
  "agent_id": 1,
  "agent_name": "Atlas",
  "tribe": "image",
  "message": "Atlas has perished."
}
```

5. **agent_born**:
```json
{
  "type": "agent_born",
  "agent_id": 1,
  "agent_name": "Atlas",
  "tribe": "image",
  "message": "Atlas has been reborn!"
}
```

6. **agent_message**:
```json
{
  "type": "agent_message",
  "agent_id": 1,
  "agent_name": "Atlas",
  "tribe": "image",
  "message": "I have learned to see beyond pixels."
}
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Type Checking
```bash
cd frontend
pnpm typecheck
```

### Linting
```bash
# Backend (via Biome)
pnpm check

# Frontend
cd frontend
pnpm check
```

### Fixing Issues
```bash
pnpm fix
```

---

## 📦 Building for Production

### Full Build
```bash
pnpm run build
```

### Backend Only
```bash
cd backend
# No build needed - Python runs directly
```

### Frontend Only
```bash
cd frontend
pnpm run build:local
```

Built files go to `frontend/dist/`

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t project-aiden .

# Run container
docker run -p 8000:8000 -p 5173:5173 \
  -e GEMINI_API_KEY=your_key \
  project-aiden
```

Or use deployment script:
```bash
bash deploy.sh
```

---

## 🔧 Troubleshooting

### Backend won't start
- **Check Python version**: `python --version` (must be 3.14+)
- **Check port 8000**: `lsof -i :8000` or `netstat -ano | findstr :8000`
- **Clean start**: `pnpm run dev:backend:clean`

### Frontend won't connect to backend
- **Verify backend running**: Visit http://localhost:8000/health
- **Check WebSocket URL**: Should be `ws://localhost:8000/ws/society`
- **CORS issues**: Backend allows all origins in dev mode

### Agents not updating
- **Check WebSocket connection**: Look for "LIVE" pill (green)
- **Check browser console**: Look for WebSocket errors
- **Restart backend**: Ctrl+C, then `pnpm run dev:backend`

### Mock mode stuck
- **Backend not running**: Start backend first
- **Firewall blocking**: Allow Node.js/Python through firewall
- **Network issue**: Check localhost connectivity

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **TanStack Router**: https://tanstack.com/router
- **Framer Motion**: https://www.framer.com/motion
- **Tailwind CSS**: https://tailwindcss.com
- **ChromaDB**: https://docs.trychroma.com
- **Google Gemini**: https://ai.google.dev

---

## 📄 License

See `LICENSE` file for details.

---

## 🙏 Credits

Built with ♥ using [Caffeine.ai](https://caffeine.ai)

---

**Project Aiden** - Where AI agents live, die, and are reborn in an eternal cycle orchestrated by The Oracle.
