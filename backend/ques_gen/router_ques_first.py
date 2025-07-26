from fastapi import APIRouter, Request, HTTPException
from ques_gen.input_handler import extract_inputs
from ques_gen.fetch_chunks import fetch_resume_chunks
from ques_gen.ques_first import generate_first_question

router = APIRouter()

@router.post("/generate-first-question")
async def generate_first_question_api(request: Request):
    data = await request.json()
    try:
        inputs = extract_inputs(data)

        chunk_data = fetch_resume_chunks(namespace=inputs.resume_id, role=inputs.role)
        chunks = chunk_data["chunks"]

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No resume chunks found for resume_id '{inputs.resume_id}'."
            )

        question = generate_first_question(inputs.role, chunks)

        return {
            "question": question,
            "namespace": inputs.resume_id
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating first question")



if __name__ == "__main__":
    from input_handler import extract_inputs
    from fetch_chunks import fetch_resume_chunks
    from ques_first import generate_first_question

    print("🚀 Starting test of generate_first_question flow...\n")

    # Sample test input
    test_input = {
        "role": "Frontend Developer",
        "resume_id": "sample_resume"
    }

    try:
        print("🔍 Step 1: Extracting input...")
        inputs = extract_inputs(test_input)
        print(f"✅ Inputs extracted: role={inputs.role}, resume_id={inputs.resume_id}\n")

        print("🔍 Step 2: Fetching chunks from Pinecone...")
        chunk_data = fetch_resume_chunks(namespace=inputs.resume_id)
        num_chunks = len(chunk_data['chunks'])
        print(f"✅ Retrieved {num_chunks} chunks from namespace '{inputs.resume_id}'\n")

        print("🔍 Step 3: Generating first question with Gemini...")
        question = generate_first_question(inputs.role, chunk_data["chunks"])
        print("✅ Gemini response received!\n")

        print("🎯 Final Output:")
        print("------------------------------")
        print(f"🧠 Question: {question}")
        print("------------------------------")

    except Exception as e:
        print("❌ Error during test execution:", str(e))
