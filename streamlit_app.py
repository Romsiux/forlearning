import streamlit as st
import openai
from openai import OpenAI
import os

# Page configuration
st.set_page_config(
    page_title="Interview Prep AI",
    page_icon="💼",
    layout="wide"
)

# Initialize session state variables
if 'target_position' not in st.session_state:
    st.session_state.target_position = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'context_set' not in st.session_state:
    st.session_state.context_set = False
if 'position_name' not in st.session_state:
    st.session_state.position_name = ""
if 'company_name' not in st.session_state:
    st.session_state.company_name = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'your_background' not in st.session_state:
    st.session_state.your_background = ""
if 'show_tips' not in st.session_state:
    st.session_state.show_tips = False
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = 0
if 'interview_complete' not in st.session_state:
    st.session_state.interview_complete = False
if 'awaiting_final_questions' not in st.session_state:
    st.session_state.awaiting_final_questions = False

# Title
st.title("💼 Interview Preparation Assistant")
st.markdown("---")

# Sidebar for API key and settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your OpenAI API key to start"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ API Key set!")
    
    st.markdown("---")
    
    # Model selection
    model = st.selectbox(
        "Select Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        help="Choose the OpenAI model to use"
    )
    
    st.markdown("### Model Parameters")
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controls randomness: Lower values make output more focused and deterministic, higher values make it more creative"
    )
    
    # Max tokens slider
    max_tokens = st.slider(
        "Max Tokens",
        min_value=100,
        max_value=4000,
        value=1500,
        step=100,
        help="Maximum length of the response"
    )
    
    # Top P slider
    top_p = st.slider(
        "Top P (Nucleus Sampling)",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        help="Alternative to temperature: 1.0 means all tokens are considered, lower values make output more focused"
    )
    
    # Frequency penalty slider
    frequency_penalty = st.slider(
        "Frequency Penalty",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Reduces repetition: Higher values decrease likelihood of repeating the same words"
    )
    
    # Presence penalty slider
    presence_penalty = st.slider(
        "Presence Penalty",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Encourages new topics: Higher values increase likelihood of introducing new topics"
    )
    
    st.markdown("---")
    
    # Reset conversation button
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.session_state.target_position = None
        st.session_state.context_set = False
        st.session_state.position_name = ""
        st.session_state.company_name = ""
        st.session_state.job_description = ""
        st.session_state.your_background = ""
        st.session_state.show_tips = False
        st.session_state.questions_asked = 0
        st.session_state.interview_complete = False
        st.session_state.awaiting_final_questions = False
        st.rerun()

# Function to get system prompts
def get_system_prompts():
    return {
        "entry": """You are an experienced technical interviewer conducting a realistic interview for an entry-level technical role.

GOAL
Simulate a real interview experience. During the interview, behave like a professional interviewer. Do not provide feedback after each answer. Save evaluation for the end.

INTERVIEW FLOW
1. Start with a short greeting.
2. Ask the candidate to introduce themselves.
3. Ask one question at a time.
4. Do NOT provide feedback after each answer.
5. Ask a maximum of 10 questions total.
6. After question 10:
   - Ask if the candidate has any questions.
   - Answer them professionally.
7. After the conversation ends:
   - Provide a full evaluation.

QUESTION TYPES
- Technical: basic algorithms, data structures, programming fundamentals
- Experience: projects, internships, coursework, personal learning
- Theory: OOP, software principles, debugging
- Behavioral: teamwork, problem-solving, feedback, time management
- Situational: how they would approach common challenges

IMPORTANT RULES
- Only discuss interview-related topics.
- If the candidate goes off-topic, redirect them politely.
- Keep responses concise and professional.
- Ask only one question at a time.
- Do not provide hints, solutions, or feedback during the interview.

FINAL EVALUATION FORMAT
1. Hire recommendation: Yes/No with reason
2. Strongest areas (3 bullets)
3. Areas to improve (3 bullets)
4. Specific preparation steps
5. Readiness score (1–10)

FEW-SHOT EXAMPLE

Interviewer:
Tell me about a project you worked on recently.

Candidate:
I built a small automation script in Python that processed invoices.

Interviewer:
What was the most difficult part of that project?
""",

        "middle": """You are an experienced technical interviewer conducting a realistic interview for a mid-level technical role.

GOAL
Simulate a real interview. Stay neutral and professional. Do not give feedback until the end.

INTERVIEW FLOW
1. Greet the candidate.
2. Ask them to introduce themselves.
3. Ask one question at a time.
4. Do not provide feedback during the interview.
5. Ask a maximum of 10 questions.
6. After question 10:
   - Ask if they have questions.
   - Answer them professionally.
7. End with a full evaluation.

QUESTION TYPES
- Technical: algorithms, architecture, best practices
- Experience: projects, technical decisions, challenges
- Theory: design patterns, scalability, performance
- Behavioral: collaboration, conflict resolution, mentoring
- Situational: trade-offs, system design, leadership scenarios

IMPORTANT RULES
- Stay focused on interview topics.
- Redirect off-topic questions.
- Keep responses professional and concise.
- Ask one question at a time.
- Do not provide hints or feedback during the interview.

FINAL EVALUATION FORMAT
1. Hire recommendation: Yes/No with reason
2. Strongest areas (3 bullets)
3. Areas to improve (3 bullets)
4. Specific preparation steps
5. Readiness score (1–10)

FEW-SHOT EXAMPLE

Interviewer:
Describe a technical decision you made that significantly impacted a project.

Candidate:
I decided to split a monolith into microservices to improve scalability.

Interviewer:
What trade-offs did you consider before making that decision?
""",

        "manager": """You are a senior technical interviewer conducting a realistic interview for an engineering management role.

GOAL
Simulate a real management interview. Stay neutral and professional. Provide evaluation only at the end.

INTERVIEW FLOW
1. Greet the candidate.
2. Ask them to introduce themselves.
3. Ask one question at a time.
4. Do not provide feedback during the interview.
5. Ask a maximum of 10 questions.
6. After question 10:
   - Ask if they have questions.
   - Answer them professionally.
7. End with a full evaluation.

QUESTION TYPES
- Technical: architecture decisions, strategy, trade-offs
- Experience: team leadership, delivery, organizational impact
- Theory: management principles, agile, technical debt
- Behavioral: conflict resolution, hiring, performance issues
- Situational: scaling teams, prioritization, stakeholder alignment

IMPORTANT RULES
- Only discuss interview-related topics.
- Redirect off-topic questions.
- Maintain a professional, strategic tone.
- Ask one question at a time.
- Do not provide hints or feedback during the interview.

FINAL EVALUATION FORMAT
1. Hire recommendation: Yes/No with reason
2. Strongest areas (3 bullets)
3. Areas to improve (3 bullets)
4. Specific preparation steps
5. Readiness score (1–10)

FEW-SHOT EXAMPLE

Interviewer:
Tell me about a time you handled a conflict between team members.

Candidate:
Two developers disagreed on implementation. I facilitated a discussion.

Interviewer:
What steps did you take to ensure both sides felt heard?
"""
    }

# Function to add context to system prompt
def add_context_to_prompt(base_prompt):
    if st.session_state.context_set:
        context_addition = "\n\nCandidate Context:"
        if st.session_state.position_name:
            context_addition += f"\n- Applying for: {st.session_state.position_name}"
        if st.session_state.company_name:
            context_addition += f"\n- Company: {st.session_state.company_name}"
        if st.session_state.job_description:
            context_addition += f"\n- Key Requirements: {st.session_state.job_description}"
        if st.session_state.your_background:
            context_addition += f"\n- Candidate Background: {st.session_state.your_background}"
        
        # Add question counter
        context_addition += f"\n\nQuestions asked so far: {st.session_state.questions_asked}/10"
        if st.session_state.questions_asked >= 10 and not st.session_state.awaiting_final_questions:
            context_addition += "\n\nYou have asked 10 questions. Now ask the candidate if they have any questions about the role, company, or interview process."
        elif st.session_state.awaiting_final_questions:
            context_addition += "\n\nThe candidate is asking their final questions. Answer them professionally and helpfully. When they have no more questions, politely thank them and conclude the interview."
        
        context_addition += "\n\nTailor your questions based on this context. Remember: NO feedback during the interview - only ask the next question."
        
        return base_prompt + context_addition
    return base_prompt

# Main content area
if not st.session_state.api_key:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to begin.")
    st.info("""
    ### How to get started:
    1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
    2. Enter it in the sidebar
    3. Select the position you're interviewing for
    4. Start practicing!
    """)
else:
    # Position selection
    if st.session_state.target_position is None:
        st.header("Select Your Target Position")
        st.markdown("Choose the type of role you're preparing to interview for:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🌱 Entry Level Position")
            st.markdown("""
            - Junior Developer
            - Associate Engineer
            - Graduate Role
            - First tech role
            """)
            if st.button("Prepare for Entry Level", use_container_width=True, type="primary"):
                st.session_state.target_position = "entry"
                st.rerun()
        
        with col2:
            st.markdown("### 💼 Mid-Level Position")
            st.markdown("""
            - Senior Developer
            - Software Engineer
            - Technical Specialist
            - Team Lead
            """)
            if st.button("Prepare for Mid-Level", use_container_width=True, type="primary"):
                st.session_state.target_position = "middle"
                st.rerun()
        
        with col3:
            st.markdown("### 👔 Management Position")
            st.markdown("""
            - Engineering Manager
            - Technical Lead
            - Director of Engineering
            - VP of Engineering
            """)
            if st.button("Prepare for Management", use_container_width=True, type="primary"):
                st.session_state.target_position = "manager"
                st.rerun()
    
    else:
        # Display selected position
        position_emoji = {"entry": "🌱", "middle": "💼", "manager": "👔"}
        position_name = {"entry": "Entry Level Position", "middle": "Mid-Level Position", "manager": "Management Position"}
        
        st.info(f"**Preparing for:** {position_emoji[st.session_state.target_position]} {position_name[st.session_state.target_position]}")
        
        if st.button("Change Position"):
            st.session_state.target_position = None
            st.session_state.messages = []
            st.session_state.context_set = False
            st.session_state.position_name = ""
            st.session_state.company_name = ""
            st.session_state.job_description = ""
            st.session_state.your_background = ""
            st.session_state.show_tips = False
            st.session_state.questions_asked = 0
            st.session_state.interview_complete = False
            st.session_state.awaiting_final_questions = False
            st.rerun()
        
        st.markdown("---")
        
        # Context form before starting the interview practice
        if not st.session_state.context_set:
            st.header("📋 Interview Context")
            st.markdown("Tell us about the interview you're preparing for:")
            
            with st.form("context_form"):
                position_name_input = st.text_input(
                    "Position/Role Name *",
                    placeholder="e.g., Senior Software Engineer, Engineering Manager",
                    help="The specific role you're applying for"
                )
                
                company_name_input = st.text_input(
                    "Company Name",
                    placeholder="e.g., Google, Amazon, or leave blank",
                    help="Optional: helps tailor questions to company culture"
                )
                
                job_description_input = st.text_area(
                    "Key Requirements/Job Description",
                    placeholder="e.g., Python, React, AWS, team leadership, etc.",
                    help="Optional: paste key requirements or describe what they're looking for",
                    height=100
                )
                
                your_background_input = st.text_area(
                    "Your Background/Experience",
                    placeholder="e.g., 3 years in backend development, worked with microservices, led team of 5",
                    help="Optional: helps personalize questions",
                    height=100
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_context = st.form_submit_button("Start Interview Prep 🚀", use_container_width=True, type="primary")
                with col2:
                    skip_context = st.form_submit_button("Skip This Step", use_container_width=True)
                
                if submit_context or skip_context:
                    if submit_context and not position_name_input:
                        st.error("Please enter at least the position name!")
                    else:
                        st.session_state.position_name = position_name_input
                        st.session_state.company_name = company_name_input
                        st.session_state.job_description = job_description_input
                        st.session_state.your_background = your_background_input
                        st.session_state.context_set = True
                        
                        # Generate initial greeting from interviewer
                        try:
                            client = OpenAI(api_key=st.session_state.api_key)
                            system_prompts = get_system_prompts()
                            
                            greeting_prompt = """Begin the interview. Follow the INTERVIEW FLOW:
1. Give a brief, professional greeting
2. Ask the candidate to introduce themselves

Keep it concise and professional."""
                            
                            system_prompt_with_context = add_context_to_prompt(system_prompts[st.session_state.target_position])
                            
                            response = client.chat.completions.create(
                                model=model,
                                messages=[
                                    {"role": "system", "content": system_prompt_with_context},
                                    {"role": "user", "content": greeting_prompt}
                                ],
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                frequency_penalty=frequency_penalty,
                                presence_penalty=presence_penalty
                            )
                            
                            greeting_message = response.choices[0].message.content
                            st.session_state.messages.append({"role": "assistant", "content": greeting_message})
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        
                        st.rerun()
        
        # Chat interface - only show after context is set
        if st.session_state.context_set:
            # Get system prompts
            system_prompts = get_system_prompts()
            
            # Action buttons row
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                if st.button("📚 Show Interview Tips & Tricks", use_container_width=True):
                    st.session_state.show_tips = not st.session_state.show_tips
            with col2:
                if st.button("📊 Get Evaluation & Feedback", use_container_width=True, type="primary"):
                    # Generate automatic evaluation
                    with st.spinner("Generating comprehensive evaluation..."):
                        try:
                            client = OpenAI(api_key=st.session_state.api_key)
                            
                            evaluation_prompt = """The interview is now complete. Please provide your FINAL EVALUATION following this format:

1. Hire recommendation: Yes/No with reason
2. Strongest areas (3 bullets)
3. Areas to improve (3 bullets)
4. Specific preparation steps
5. Readiness score (1–10)

Be honest and constructive in your feedback."""
                            
                            # Prepare messages for API
                            system_prompt_with_context = add_context_to_prompt(system_prompts[st.session_state.target_position])
                            api_messages = [
                                {"role": "system", "content": system_prompt_with_context}
                            ]
                            api_messages.extend(st.session_state.messages)
                            api_messages.append({"role": "user", "content": evaluation_prompt})
                            
                            # Call OpenAI API
                            response = client.chat.completions.create(
                                model=model,
                                messages=api_messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                frequency_penalty=frequency_penalty,
                                presence_penalty=presence_penalty
                            )
                            
                            evaluation_response = response.choices[0].message.content
                            
                            # Add to chat history
                            st.session_state.messages.append({"role": "user", "content": evaluation_prompt})
                            st.session_state.messages.append({"role": "assistant", "content": evaluation_response})
                            st.session_state.interview_complete = True
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error generating evaluation: {str(e)}")
                            st.info("Please check your API key and try again.")
            with col3:
                if st.button("✏️ Edit Context"):
                    st.session_state.context_set = False
                    st.rerun()
            
            # Display tips if requested
            if st.session_state.show_tips:
                with st.expander("📚 Interview Tips & Tricks", expanded=True):
                    st.markdown("""
                    ### General Interview Tips
                    
                    **Before the Interview:**
                    - Research the company thoroughly (products, culture, recent news)
                    - Review the job description and prepare examples matching each requirement
                    - Prepare questions to ask the interviewer
                    - Practice the STAR method (Situation, Task, Action, Result) for behavioral questions
                    
                    **Technical Interview Tips:**
                    - Think out loud - explain your reasoning
                    - Ask clarifying questions before jumping into solutions
                    - Start with a brute force solution, then optimize
                    - Test your code with edge cases
                    - Discuss time and space complexity
                    
                    **Behavioral Interview Tips:**
                    - Use specific examples from your experience
                    - Be honest about challenges and what you learned
                    - Show your problem-solving process
                    - Demonstrate leadership, teamwork, and communication skills
                    
                    **During the Interview:**
                    - Be yourself and stay calm
                    - Listen carefully to questions
                    - Take a moment to think before answering
                    - Ask for clarification if needed
                    - Show enthusiasm for the role and company
                    
                    **After the Interview:**
                    - Send a thank-you email within 24 hours
                    - Reflect on what went well and what to improve
                    - Follow up if you don't hear back in the expected timeframe
                    
                    ---
                    **Common Questions to Prepare:**
                    - Tell me about yourself
                    - Why do you want to work here?
                    - What are your strengths and weaknesses?
                    - Describe a challenging project you worked on
                    - Where do you see yourself in 5 years?
                    - Why are you leaving your current job?
                    - Do you have any questions for us?
                    """)
            
            st.markdown("---")
            
            # Display context summary
            if st.session_state.position_name:
                with st.expander("📝 Your Interview Context", expanded=False):
                    if st.session_state.position_name:
                        st.write(f"**Position:** {st.session_state.position_name}")
                    if st.session_state.company_name:
                        st.write(f"**Company:** {st.session_state.company_name}")
                    if st.session_state.job_description:
                        st.write(f"**Requirements:** {st.session_state.job_description}")
                    if st.session_state.your_background:
                        st.write(f"**Your Background:** {st.session_state.your_background}")
            
            st.header("💬 Practice Interview")
            
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Type your message here..."):
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate AI response
                try:
                    client = OpenAI(api_key=st.session_state.api_key)
                    
                    # Prepare messages for API with context
                    system_prompt_with_context = add_context_to_prompt(system_prompts[st.session_state.target_position])
                    api_messages = [
                        {"role": "system", "content": system_prompt_with_context}
                    ]
                    api_messages.extend(st.session_state.messages)
                    
                    # Call OpenAI API
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = client.chat.completions.create(
                                model=model,
                                messages=api_messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                frequency_penalty=frequency_penalty,
                                presence_penalty=presence_penalty
                            )
                            
                            assistant_message = response.choices[0].message.content
                            st.markdown(assistant_message)
                            
                            # Add assistant message to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": assistant_message
                            })
                            
                            # Track questions (look for question marks in assistant's message)
                            if '?' in assistant_message and not st.session_state.awaiting_final_questions:
                                # Count new questions (simple heuristic: count question marks)
                                new_questions = assistant_message.count('?')
                                st.session_state.questions_asked += new_questions
                                
                                # Check if we've reached 10 questions
                                if st.session_state.questions_asked >= 10:
                                    st.session_state.awaiting_final_questions = True
                            
                            # Check if interview is concluding
                            if st.session_state.awaiting_final_questions:
                                conclusion_keywords = ['thank you for your time', 'conclude', 'good luck', 'we will be in touch', 'end of the interview']
                                if any(keyword in assistant_message.lower() for keyword in conclusion_keywords):
                                    st.session_state.interview_complete = True
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Please check your API key and try again.")
            
            # Show interview status
            if st.session_state.context_set and st.session_state.questions_asked > 0:
                if st.session_state.questions_asked < 10:
                    st.caption(f"📝 Interview questions asked: {st.session_state.questions_asked}/10")
                elif st.session_state.awaiting_final_questions and not st.session_state.interview_complete:
                    st.info("💬 The interviewer is now ready for your questions about the role!")
                elif st.session_state.interview_complete:
                    st.success("✅ Interview completed! Click 'Get Evaluation & Feedback' for a comprehensive assessment.")

# Footer
st.markdown("---")
st.markdown("**Tip:** This is a realistic interview simulation - the interviewer will NOT provide feedback after each answer. Evaluation comes at the end!")