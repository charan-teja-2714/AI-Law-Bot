from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence


def generate_doctor_questions(context, llm, max_questions=7):
    """
    Generates ONLY questions a patient can ask their doctor.
    No answers. No diagnosis. No treatment.
    """

    prompt = PromptTemplate(
        template="""
You are a medical assistant helping patients prepare questions for their doctor.

--------------------------------
📄 Medical Report Context:
{context}

--------------------------------
Your task:
- Generate ONLY questions (no answers)
- Questions must be neutral, safe, and non-diagnostic
- Do NOT mention diseases
- Do NOT suggest treatments or medications
- Questions should help clarify abnormal or unclear findings
- Keep questions practical and respectful

Rules:
- Output 5–{max_questions} questions
- Use simple bullet points
- Do NOT add explanations
- Do NOT assume any condition

Examples of good questions:
- "Is this value within the normal range for my age?"
- "Is this something that needs monitoring over time?"
- "Are follow-up tests usually recommended for this result?"

--------------------------------
📝 Questions to ask the doctor:
""",
        input_variables=["context", "max_questions"],
    )

    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "max_questions": max_questions
    })

    return response.content.strip()
