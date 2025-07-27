import asyncio
from .end_services import calc_job_fit, validate_exp, calc_acc, gen_emotion_report

async def main():
    resume_id = "test_resume_123"
    scores = await calc_acc(resume_id)
    print("Accuracy Scores:")
    for q, score in scores.items():
        print(f"{q}: {score}")

    score = await calc_job_fit(resume_id)
    print("Job-Fit Score:", score)

    result = await validate_exp(resume_id)
    print("Experience Validation Results:")
    for q, val in result.items():
        print(f"{q}: {val}")

    report = await gen_emotion_report("test_resume_123")
    print("Emotion Report:")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
