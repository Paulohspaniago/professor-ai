# Practice enrollment table

In this fictional SQLite schema, foreign key enforcement is enabled. enrollments.student_id is NOT NULL and REFERENCES students(student_id). Every stored enrollment must reference an existing student identifier. This foreign key alone does not forbid multiple enrollments for the same student.
