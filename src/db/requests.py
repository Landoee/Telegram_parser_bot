from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Students

async def save_student(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    uni_name: str,
    group_name: str,
    course: int,
    subgroup_number: int
):
    student = await session.get(Students, telegram_id)
    
    if student:
        student.username = username
        student.uni_name = uni_name
        student.course = course
        student.group_name = group_name
        student.subgroup_number = subgroup_number
    else:
        student = Students(
            telegram_id=telegram_id,
            username=username,
            uni_name=uni_name,
            course=course,
            group_name=group_name,
            subgroup_number=subgroup_number
        )
        session.add(student)
        
    await session.commit()