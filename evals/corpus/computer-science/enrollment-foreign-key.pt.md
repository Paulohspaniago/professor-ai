# Tabela de matrículas do exercício

Neste esquema fictício SQLite, a verificação de chaves estrangeiras está ativada. enrollments.student_id é NOT NULL e REFERENCES students(student_id). Cada matrícula deve apontar para um identificador de estudante existente. Essa chave estrangeira, sozinha, não proíbe várias matrículas para o mesmo estudante.
