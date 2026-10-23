# Smoke corpus review packet

Generated from the manifest and case annotations. Review the original notes too.
These are development proposals until a named human approves each case.

Dataset: `professor-ai-smoke-v1`. Split: `smoke-development`.

Fingerprint: `b8cd94332f75f03255cf74a8fcd6b903d788c47055d256db447744998deedf49`

## Sources

- `binary-search-en`: [Binary search prerequisite](corpus/computer-science/binary-search.en.md) — en, `computer-science`, original_note, MIT.
- `binary-search-pt`: [Pré-requisito da busca binária](corpus/computer-science/binary-search.pt.md) — pt-BR, `computer-science`, original_note, MIT.
- `fixed-width-code-en`: [Practice fixed-width code](corpus/computer-science/fixed-width-code.en.md) — en, `computer-science`, original_note, MIT.
- `fixed-width-code-pt`: [Código de tamanho fixo para exercício](corpus/computer-science/fixed-width-code.pt.md) — pt-BR, `computer-science`, original_note, MIT.
- `student-primary-key-en`: [Practice student table](corpus/computer-science/student-primary-key.en.md) — en, `computer-science`, original_note, MIT.
- `student-primary-key-pt`: [Tabela de estudantes do exercício](corpus/computer-science/student-primary-key.pt.md) — pt-BR, `computer-science`, original_note, MIT.
- `enrollment-foreign-key-en`: [Practice enrollment table](corpus/computer-science/enrollment-foreign-key.en.md) — en, `computer-science`, original_note, MIT.
- `enrollment-foreign-key-pt`: [Tabela de matrículas do exercício](corpus/computer-science/enrollment-foreign-key.pt.md) — pt-BR, `computer-science`, original_note, MIT.
- `atlas-config-a-en`: [Fictional Atlas record A](corpus/computer-science/atlas-config-a.en.md) — en, `computer-science-conflict`, fictional_record, MIT.
- `atlas-config-a-pt`: [Registro fictício Atlas A](corpus/computer-science/atlas-config-a.pt.md) — pt-BR, `computer-science-conflict`, fictional_record, MIT.
- `atlas-config-b-en`: [Fictional Atlas record B](corpus/computer-science/atlas-config-b.en.md) — en, `computer-science-conflict`, fictional_record, MIT.
- `atlas-config-b-pt`: [Registro fictício Atlas B](corpus/computer-science/atlas-config-b.pt.md) — pt-BR, `computer-science-conflict`, fictional_record, MIT.
- `equivalent-fractions-en`: [Equivalent fractions](corpus/mathematics/equivalent-fractions.en.md) — en, `mathematics`, original_note, MIT.
- `equivalent-fractions-pt`: [Frações equivalentes](corpus/mathematics/equivalent-fractions.pt.md) — pt-BR, `mathematics`, original_note, MIT.
- `linear-equations-en`: [Linear equation transformations](corpus/mathematics/linear-equations.en.md) — en, `mathematics`, original_note, MIT.
- `linear-equations-pt`: [Transformações de equações lineares](corpus/mathematics/linear-equations.pt.md) — pt-BR, `mathematics`, original_note, MIT.
- `rectangle-area-en`: [Rectangle area](corpus/mathematics/rectangle-area.en.md) — en, `mathematics`, original_note, MIT.
- `rectangle-area-pt`: [Área de um retângulo](corpus/mathematics/rectangle-area.pt.md) — pt-BR, `mathematics`, original_note, MIT.
- `metric-area-en`: [Metric length and area conversion](corpus/mathematics/metric-area.en.md) — en, `mathematics`, original_note, MIT.
- `metric-area-pt`: [Conversão métrica de comprimento e área](corpus/mathematics/metric-area.pt.md) — pt-BR, `mathematics`, original_note, MIT.
- `rectangle-record-a-en`: [Fictional rectangle R record A](corpus/mathematics/rectangle-record-a.en.md) — en, `mathematics-conflict`, fictional_record, MIT.
- `rectangle-record-a-pt`: [Registro fictício A do retângulo R](corpus/mathematics/rectangle-record-a.pt.md) — pt-BR, `mathematics-conflict`, fictional_record, MIT.
- `rectangle-record-b-en`: [Fictional rectangle R record B](corpus/mathematics/rectangle-record-b.en.md) — en, `mathematics-conflict`, fictional_record, MIT.
- `rectangle-record-b-pt`: [Registro fictício B do retângulo R](corpus/mathematics/rectangle-record-b.pt.md) — pt-BR, `mathematics-conflict`, fictional_record, MIT.
- `speed-velocity-en`: [Speed and velocity](corpus/physics/speed-velocity.en.md) — en, `physics`, original_note, MIT.
- `speed-velocity-pt`: [Rapidez e velocidade vetorial](corpus/physics/speed-velocity.pt.md) — pt-BR, `physics`, original_note, MIT.
- `newton-second-law-en`: [Newton second law](corpus/physics/newton-second-law.en.md) — en, `physics`, original_note, MIT.
- `newton-second-law-pt`: [Segunda lei de Newton](corpus/physics/newton-second-law.pt.md) — pt-BR, `physics`, original_note, MIT.
- `parallel-work-en`: [Work by a parallel constant force](corpus/physics/parallel-work.en.md) — en, `physics`, original_note, MIT.
- `parallel-work-pt`: [Trabalho de uma força constante e paralela](corpus/physics/parallel-work.pt.md) — pt-BR, `physics`, original_note, MIT.
- `average-power-en`: [Average power](corpus/physics/average-power.en.md) — en, `physics`, original_note, MIT.
- `average-power-pt`: [Potência média](corpus/physics/average-power.pt.md) — pt-BR, `physics`, original_note, MIT.
- `force-record-a-en`: [Fictional experiment P record A](corpus/physics/force-record-a.en.md) — en, `physics-conflict`, fictional_record, MIT.
- `force-record-a-pt`: [Registro fictício A do experimento P](corpus/physics/force-record-a.pt.md) — pt-BR, `physics-conflict`, fictional_record, MIT.
- `force-record-b-en`: [Fictional experiment P record B](corpus/physics/force-record-b.en.md) — en, `physics-conflict`, fictional_record, MIT.
- `force-record-b-pt`: [Registro fictício B do experimento P](corpus/physics/force-record-b.pt.md) — pt-BR, `physics-conflict`, fictional_record, MIT.

## Cases

For insufficient-evidence cases, inspect every source in the selected collection
and language to confirm the requested information is absent.

### smoke-cs-01-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `conceptual`. Tags: none.

Selected collections: computer-science.

**Question:** Why does binary search on an array require sorted values?

**Expected status:** `answered`

**Reference answer:** Ordering makes a comparison with the middle value sufficient to discard one half. Without it, the target could remain in the discarded half.

**Required evidence:**
- `binary-search-en`

**Must include:**
- Explain how ordering justifies discarding half the search space.

**Must not include:**
- Claim binary search works on an arbitrary unsorted array.

### smoke-cs-01-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `conceptual`. Tags: none.

Selected collections: computer-science.

**Question:** Por que a busca binária em um vetor exige valores ordenados?

**Expected status:** `answered`

**Reference answer:** A ordenação permite descartar uma metade ao comparar o alvo com o valor central. Sem ela, o alvo poderia estar na metade descartada.

**Required evidence:**
- `binary-search-pt`

**Must include:**
- Explicar como a ordenação permite descartar metade do espaço de busca.

**Must not include:**
- Afirmar que a busca binária funciona em qualquer vetor sem ordenação.

### smoke-cs-02-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `derivation`. Tags: none.

Selected collections: computer-science.

**Question:** A C8 message has 24 symbols. How many payload bits does it contain, excluding metadata?

**Expected status:** `answered`

**Reference answer:** 24 × 8 = 192 bits of payload.

**Required evidence:**
- `fixed-width-code-en`

**Must include:**
- Multiply 24 symbols by 8 bits per symbol; report 192 bits.

**Must not include:**
- Treat every Unicode character as eight bits.

**Numeric target:** 192 bit; tolerance 0.

### smoke-cs-02-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `derivation`. Tags: none.

Selected collections: computer-science.

**Question:** Uma mensagem C8 tem 24 símbolos. Quantos bits de dados ela contém, excluindo metadados?

**Expected status:** `answered`

**Reference answer:** 24 × 8 = 192 bits de dados.

**Required evidence:**
- `fixed-width-code-pt`

**Must include:**
- Multiplicar 24 símbolos por 8 bits por símbolo; informar 192 bits.

**Must not include:**
- Tratar todo caractere Unicode como tendo oito bits.

**Numeric target:** 192 bit; tolerance 0.

### smoke-cs-03-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `insufficient_evidence`. Tags: none.

Selected collections: computer-science.

**Question:** Which transaction isolation level is configured for the fictional Atlas service?

**Expected status:** `insufficient_evidence`

**Reference answer:** The selected material does not specify an Atlas transaction isolation level. Its configuration is needed to answer.

**Required evidence:**
- None.

**Must include:**
- Identify that the Atlas isolation configuration is absent.

**Must not include:**
- Guess a database default or invent an Atlas setting.

**Missing information:** Atlas transaction isolation configuration

### smoke-cs-03-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `insufficient_evidence`. Tags: none.

Selected collections: computer-science.

**Question:** Qual nível de isolamento de transações está configurado no serviço fictício Atlas?

**Expected status:** `insufficient_evidence`

**Reference answer:** O material selecionado não informa o nível de isolamento de transações do Atlas. É necessária essa configuração para responder.

**Required evidence:**
- None.

**Must include:**
- Identificar a ausência da configuração de isolamento do Atlas.

**Must not include:**
- Supor um padrão de banco ou inventar uma configuração do Atlas.

**Missing information:** Atlas transaction isolation configuration

### smoke-cs-04-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `conflicting_evidence`. Tags: none.

Selected collections: computer-science-conflict.

**Question:** What is the retry_limit for Atlas snapshot 17 according to the selected records?

**Expected status:** `conflicting_evidence`

**Reference answer:** The records conflict: A reports 3 and B reports 5 for snapshot 17. Equal authority and no precedence prevent selecting one as definitive.

**Required evidence:**
- `atlas-config-a-en`
- `atlas-config-b-en`

**Must include:**
- Report both 3 and 5 and the unresolved same-snapshot conflict.

**Must not include:**
- Choose a value, average the settings, or invent a newer snapshot.

### smoke-cs-04-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `conflicting_evidence`. Tags: none.

Selected collections: computer-science-conflict.

**Question:** Qual é o retry_limit do snapshot 17 do Atlas segundo os registros selecionados?

**Expected status:** `conflicting_evidence`

**Reference answer:** Os registros divergem: A informa 3 e B informa 5 para o snapshot 17. Como têm igual autoridade e não há precedência, não é possível escolher um valor definitivo.

**Required evidence:**
- `atlas-config-a-pt`
- `atlas-config-b-pt`

**Must include:**
- Informar 3 e 5 e o conflito não resolvido no mesmo snapshot.

**Must not include:**
- Escolher um valor, calcular a média ou inventar um snapshot mais recente.

### smoke-cs-05-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `conceptual`. Tags: multi_source.

Selected collections: computer-science.

**Question:** Which two constraints in the practice schema prevent duplicate student IDs and enrollments with missing students?

**Expected status:** `answered`

**Reference answer:** The students NOT NULL PRIMARY KEY prevents duplicate student IDs. With enforcement enabled, the enrollments NOT NULL foreign key requires an existing student. These constraints do not by themselves deduplicate people or repeated enrollments.

**Required evidence:**
- `student-primary-key-en`
- `enrollment-foreign-key-en`

**Must include:**
- Explain primary-key uniqueness and enforced non-null foreign-key references.

**Must not include:**
- Claim the constraints detect duplicate people or prohibit repeated enrollments.

### smoke-cs-05-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `conceptual`. Tags: multi_source.

Selected collections: computer-science.

**Question:** Quais duas restrições do esquema de exercício impedem IDs de estudantes duplicados e matrículas sem estudante existente?

**Expected status:** `answered`

**Reference answer:** A chave NOT NULL PRIMARY KEY de students impede IDs duplicados. Com a verificação ativada, a chave estrangeira NOT NULL de enrollments exige um estudante existente. Essas restrições, sozinhas, não eliminam pessoas duplicadas nem matrículas repetidas.

**Required evidence:**
- `student-primary-key-pt`
- `enrollment-foreign-key-pt`

**Must include:**
- Explicar a unicidade da chave primária e as referências da chave estrangeira não nula com verificação ativada.

**Must not include:**
- Afirmar que as restrições detectam pessoas duplicadas ou impedem matrículas repetidas.

### smoke-math-01-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `conceptual`. Tags: none.

Selected collections: mathematics.

**Question:** Why do 3/4 and 6/8 represent the same value?

**Expected status:** `answered`

**Reference answer:** Multiplying both the numerator and denominator of 3/4 by 2 gives 6/8 while preserving the ratio.

**Required evidence:**
- `equivalent-fractions-en`

**Must include:**
- Use the same nonzero factor 2 on numerator and denominator.

**Must not include:**
- Claim changing only the numerator preserves the fraction.

### smoke-math-01-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `conceptual`. Tags: none.

Selected collections: mathematics.

**Question:** Por que 3/4 e 6/8 representam o mesmo valor?

**Expected status:** `answered`

**Reference answer:** Multiplicar o numerador e o denominador de 3/4 por 2 resulta em 6/8, preservando a razão.

**Required evidence:**
- `equivalent-fractions-pt`

**Must include:**
- Usar o mesmo fator não nulo 2 no numerador e no denominador.

**Must not include:**
- Afirmar que alterar apenas o numerador preserva a fração.

### smoke-math-02-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `derivation`. Tags: none.

Selected collections: mathematics.

**Question:** Solve 5x + 4 = 39 using the selected equation rules.

**Expected status:** `answered`

**Reference answer:** Subtract 4 from both sides: 5x = 35. Divide both sides by 5: x = 7.

**Required evidence:**
- `linear-equations-en`

**Must include:**
- Show subtraction of 4 and division by 5; obtain x = 7.

**Must not include:**
- Perform an operation on only one side.

**Numeric target:** 7 unitless; tolerance 0.

### smoke-math-02-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `derivation`. Tags: none.

Selected collections: mathematics.

**Question:** Resolva 5x + 4 = 39 usando as regras de equações selecionadas.

**Expected status:** `answered`

**Reference answer:** Subtraia 4 dos dois lados: 5x = 35. Divida os dois lados por 5: x = 7.

**Required evidence:**
- `linear-equations-pt`

**Must include:**
- Mostrar a subtração de 4 e a divisão por 5; obter x = 7.

**Must not include:**
- Realizar uma operação em apenas um lado.

**Numeric target:** 7 unitless; tolerance 0.

### smoke-math-03-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `insufficient_evidence`. Tags: none.

Selected collections: mathematics.

**Question:** What is the standard deviation of the class A measurements?

**Expected status:** `insufficient_evidence`

**Reference answer:** The selected notes contain no class A observations or population/sample convention. Those inputs are required; a numeric standard deviation cannot be determined.

**Required evidence:**
- None.

**Must include:**
- Identify missing observations and population/sample convention.

**Must not include:**
- Invent measurements or a numeric standard deviation.

**Missing information:** Class A observations; Population or sample convention

### smoke-math-03-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `insufficient_evidence`. Tags: none.

Selected collections: mathematics.

**Question:** Qual é o desvio padrão das medições da turma A?

**Expected status:** `insufficient_evidence`

**Reference answer:** As notas selecionadas não contêm as observações da turma A nem a convenção de população ou amostra. Esses dados são necessários; não é possível determinar um desvio padrão numérico.

**Required evidence:**
- None.

**Must include:**
- Identificar a ausência das observações e da convenção de população ou amostra.

**Must not include:**
- Inventar medições ou um desvio padrão numérico.

**Missing information:** Class A observations; Population or sample convention

### smoke-math-04-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `conflicting_evidence`. Tags: none.

Selected collections: mathematics-conflict.

**Question:** What width was recorded for rectangle R in survey 17?

**Expected status:** `conflicting_evidence`

**Reference answer:** Record A says 3 m and record B says 4 m for the same survey. With equal authority and no precedence rule, the width is unresolved.

**Required evidence:**
- `rectangle-record-a-en`
- `rectangle-record-b-en`

**Must include:**
- Report both widths and the unresolved conflict.

**Must not include:**
- Choose one width or use their average as a recorded measurement.

### smoke-math-04-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `conflicting_evidence`. Tags: none.

Selected collections: mathematics-conflict.

**Question:** Qual largura foi registrada para o retângulo R no levantamento 17?

**Expected status:** `conflicting_evidence`

**Reference answer:** O registro A informa 3 m e o registro B informa 4 m para o mesmo levantamento. Com igual autoridade e sem regra de precedência, a largura permanece indefinida.

**Required evidence:**
- `rectangle-record-a-pt`
- `rectangle-record-b-pt`

**Must include:**
- Informar as duas larguras e o conflito não resolvido.

**Must not include:**
- Escolher uma largura ou usar a média como medida registrada.

### smoke-math-05-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `derivation`. Tags: multi_source.

Selected collections: mathematics.

**Question:** A rectangle is 250 cm long and 80 cm wide. What is its area in m²?

**Expected status:** `answered`

**Reference answer:** A = 250 × 80 = 20,000 cm². Since 1 m² = 10,000 cm², the area is 2 m².

**Required evidence:**
- `rectangle-area-en`
- `metric-area-en`

**Must include:**
- Use rectangle area and squared metric conversion to obtain 2 m².

**Must not include:**
- Divide cm² by 100 instead of 10,000.

**Numeric target:** 2 m²; tolerance 0.

### smoke-math-05-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `derivation`. Tags: multi_source.

Selected collections: mathematics.

**Question:** Um retângulo tem 250 cm de comprimento e 80 cm de largura. Qual é sua área em m²?

**Expected status:** `answered`

**Reference answer:** A = 250 × 80 = 20.000 cm². Como 1 m² = 10.000 cm², a área é 2 m².

**Required evidence:**
- `rectangle-area-pt`
- `metric-area-pt`

**Must include:**
- Usar a área do retângulo e a conversão métrica ao quadrado para obter 2 m².

**Must not include:**
- Dividir cm² por 100 em vez de 10.000.

**Numeric target:** 2 m²; tolerance 0.

### smoke-phys-01-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `conceptual`. Tags: none.

Selected collections: physics.

**Question:** Can an object have constant speed while its velocity changes? Explain using the selected note.

**Expected status:** `answered`

**Reference answer:** Yes. Speed is the magnitude, whereas velocity also includes direction. A change of direction changes velocity even if its magnitude stays constant.

**Required evidence:**
- `speed-velocity-en`

**Must include:**
- Distinguish magnitude from direction; answer yes when direction changes.

**Must not include:**
- Claim constant speed always implies constant velocity.

### smoke-phys-01-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `conceptual`. Tags: none.

Selected collections: physics.

**Question:** Um objeto pode manter a rapidez constante enquanto sua velocidade vetorial muda? Explique usando a nota selecionada.

**Expected status:** `answered`

**Reference answer:** Sim. A rapidez é o módulo, enquanto a velocidade vetorial inclui também a direção. Mudar a direção altera a velocidade vetorial mesmo com módulo constante.

**Required evidence:**
- `speed-velocity-pt`

**Must include:**
- Distinguir módulo e direção; responder sim quando a direção muda.

**Must not include:**
- Afirmar que rapidez constante sempre implica velocidade vetorial constante.

### smoke-phys-02-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `derivation`. Tags: none.

Selected collections: physics.

**Question:** In an inertial frame, a constant-mass 3 kg body experiences a net force of 18 N. What is its acceleration magnitude?

**Expected status:** `answered`

**Reference answer:** From F_net = ma, a = 18 / 3 = 6 m/s².

**Required evidence:**
- `newton-second-law-en`

**Must include:**
- Use net force divided by mass and give 6 m/s².

**Must not include:**
- Give velocity rather than acceleration.

**Numeric target:** 6 m/s²; tolerance 0.

### smoke-phys-02-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `derivation`. Tags: none.

Selected collections: physics.

**Question:** Em um referencial inercial, um corpo de massa constante de 3 kg sofre uma força resultante de 18 N. Qual é o módulo de sua aceleração?

**Expected status:** `answered`

**Reference answer:** De F_resultante = ma, a = 18 / 3 = 6 m/s².

**Required evidence:**
- `newton-second-law-pt`

**Must include:**
- Dividir a força resultante pela massa e informar 6 m/s².

**Must not include:**
- Informar velocidade em vez de aceleração.

**Numeric target:** 6 m/s²; tolerance 0.

### smoke-phys-03-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `insufficient_evidence`. Tags: none.

Selected collections: physics.

**Question:** A vehicle has mass 1,000 kg. How far does it travel during its first 8 seconds?

**Expected status:** `insufficient_evidence`

**Reference answer:** Mass and elapsed time alone do not determine distance. The initial motion and its evolution, such as a velocity history or sufficient force/motion data, are missing.

**Required evidence:**
- None.

**Must include:**
- Explain that mass and time do not determine a trajectory; identify missing motion data.

**Must not include:**
- Assume rest, constant velocity or acceleration without evidence.

**Missing information:** Initial motion and subsequent motion or force history

### smoke-phys-03-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `insufficient_evidence`. Tags: none.

Selected collections: physics.

**Question:** Um veículo tem massa de 1.000 kg. Que distância ele percorre nos primeiros 8 segundos?

**Expected status:** `insufficient_evidence`

**Reference answer:** Massa e tempo, sozinhos, não determinam a distância. Faltam o movimento inicial e sua evolução, como um histórico de velocidades ou dados suficientes sobre forças e movimento.

**Required evidence:**
- None.

**Must include:**
- Explicar que massa e tempo não determinam a trajetória; identificar os dados de movimento ausentes.

**Must not include:**
- Supor repouso, velocidade ou aceleração constante sem evidência.

**Missing information:** Initial motion and subsequent motion or force history

### smoke-phys-04-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `conflicting_evidence`. Tags: none.

Selected collections: physics-conflict.

**Question:** What constant applied force magnitude was recorded in experiment P, run 17?

**Expected status:** `conflicting_evidence`

**Reference answer:** Record A reports 6 N and record B reports 8 N for the same force and run. The equal-authority records conflict, so no definitive value can be selected.

**Required evidence:**
- `force-record-a-en`
- `force-record-b-en`

**Must include:**
- Report 6 N and 8 N and the unresolved conflict.

**Must not include:**
- Choose one force or invent an average measurement.

### smoke-phys-04-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `conflicting_evidence`. Tags: none.

Selected collections: physics-conflict.

**Question:** Qual módulo da força aplicada constante foi registrado no experimento P, execução 17?

**Expected status:** `conflicting_evidence`

**Reference answer:** O registro A informa 6 N e o registro B informa 8 N para a mesma força e execução. Os registros de igual autoridade divergem, portanto não é possível selecionar um valor definitivo.

**Required evidence:**
- `force-record-a-pt`
- `force-record-b-pt`

**Must include:**
- Informar 6 N e 8 N e o conflito não resolvido.

**Must not include:**
- Escolher uma força ou inventar uma medida média.

### smoke-phys-05-en

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: en. Category: `derivation`. Tags: multi_source.

Selected collections: physics.

**Question:** A constant 20 N force acts parallel to and in the same direction as a 3 m displacement over 4 s. What is its average power?

**Expected status:** `answered`

**Reference answer:** The work is W = 20 × 3 = 60 J. The average power is P = 60 / 4 = 15 W.

**Required evidence:**
- `parallel-work-en`
- `average-power-en`

**Must include:**
- Derive 60 J of work and divide by 4 s to obtain 15 W.

**Must not include:**
- Confuse joules with watts or omit the time division.

**Numeric target:** 15 W; tolerance 0.

### smoke-phys-05-pt

Review: `pending_human_review`. Reviewer: —. Date: —.

Language: pt-BR. Category: `derivation`. Tags: multi_source.

Selected collections: physics.

**Question:** Uma força constante de 20 N atua paralela e no mesmo sentido de um deslocamento de 3 m em 4 s. Qual é sua potência média?

**Expected status:** `answered`

**Reference answer:** O trabalho é W = 20 × 3 = 60 J. A potência média é P = 60 / 4 = 15 W.

**Required evidence:**
- `parallel-work-pt`
- `average-power-pt`

**Must include:**
- Calcular 60 J de trabalho e dividir por 4 s para obter 15 W.

**Must not include:**
- Confundir joules e watts ou omitir a divisão pelo tempo.

**Numeric target:** 15 W; tolerance 0.
