# Interview Prep AI Assistant 💼

A Streamlit application that simulates realistic technical interviews using an AI interviewer.
Designed to help you practice answering questions in a structured, interview-like environment and receive a final evaluation at the end.

## Features

**Three interview tracks**
- Entry-level
- Mid-level
- Management roles

**Realistic interview flow**
- Around 10 questions
- No feedback during the interview
- Full evaluation at the end

**Custom interview context**
- Role title
- Company
- Job requirements
- Candidate background

**Built-in interview tips**

**Adjustable model parameters**

## Tech Stack

- Python
- Streamlit (frontend)
- OpenAI API (LLM interviewer)

## Installation

### Requirements

- Python 3.8+
- OpenAI API key

### Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd <repo-folder>
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run interview_prep_updated.py
```

4. **Open in your browser:**
```
http://localhost:8501
```

5. **Enter your OpenAI API key in the sidebar.**

## Usage

1. Select the target interview level.
2. (Optional) Provide job context:
   - Position
   - Company
   - Requirements
   - Background
3. Start the interview.
4. Answer questions naturally.
5. Request the final evaluation after the session.

## Interview Tracks

### Entry Level

Focus on:
- Programming fundamentals
- Basic algorithms and data structures
- Personal or academic projects
- OOP concepts
- Behavioral questions

### Mid-Level

Focus on:
- Algorithms and system design
- Design patterns and best practices
- Technical decision-making
- Leadership or mentoring experience

### Management

Focus on:
- Technical strategy
- Team leadership
- Conflict resolution
- Stakeholder management
- Hiring and team building

## Configuration

Adjustable parameters in the sidebar:

- Model selection
- Temperature
- Max tokens
- Top-p
- Frequency penalty
- Presence penalty

## Troubleshooting

**Invalid API key**
- Verify the key is correct.
- Ensure your OpenAI account has credits.

**App does not start**
```bash
pip install -r requirements.txt
```

**Unexpected costs**
- Use a lower-cost model.
- Set spending limits in your OpenAI account.

## Roadmap

- [ ] Resume-based question generation
- [ ] Progress tracking across sessions
- [ ] Voice input/output
- [ ] Interview history and replay
- [ ] Cost estimator

## License

This project is intended for learning and personal use.
You are free to modify or extend it.
