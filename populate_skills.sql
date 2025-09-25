-- Script SQL para popular Skills (Habilidades) no sistema RH Acqua
-- Execute este script diretamente no banco PostgreSQL para adicionar as habilidades necessárias

-- Inserir Job Categories primeiro (caso não existam)
INSERT INTO vacancies_jobcategory (name, description, is_active) VALUES
('Medicina', 'Categoria para profissionais médicos', true),
('Enfermagem', 'Categoria para profissionais de enfermagem', true),
('Administração', 'Categoria para profissionais administrativos', true),
('Técnico', 'Categoria para profissionais técnicos', true),
('Apoio', 'Categoria para profissionais de apoio', true)
ON CONFLICT (name) DO NOTHING;

-- Inserir Skills (Habilidades)
INSERT INTO vacancies_skill (name, description, category_id) VALUES
-- Habilidades Médicas
('Cardiologia', 'Especialização em doenças do coração', (SELECT id FROM vacancies_jobcategory WHERE name = 'Medicina' LIMIT 1)),
('Pediatria', 'Especialização em medicina infantil', (SELECT id FROM vacancies_jobcategory WHERE name = 'Medicina' LIMIT 1)),
('Cirurgia Geral', 'Conhecimentos em procedimentos cirúrgicos gerais', (SELECT id FROM vacancies_jobcategory WHERE name = 'Medicina' LIMIT 1)),
('Emergência', 'Atendimento médico de emergência', (SELECT id FROM vacancies_jobcategory WHERE name = 'Medicina' LIMIT 1)),
('Anestesiologia', 'Especialização em anestesia e dor', (SELECT id FROM vacancies_jobcategory WHERE name = 'Medicina' LIMIT 1)),

-- Habilidades de Enfermagem
('Cuidados Intensivos', 'Experiência em UTI e cuidados críticos', (SELECT id FROM vacancies_jobcategory WHERE name = 'Enfermagem' LIMIT 1)),
('Enfermagem Cirúrgica', 'Assistência em procedimentos cirúrgicos', (SELECT id FROM vacancies_jobcategory WHERE name = 'Enfermagem' LIMIT 1)),
('Medicação', 'Administração segura de medicamentos', (SELECT id FROM vacancies_jobcategory WHERE name = 'Enfermagem' LIMIT 1)),
('Curativos', 'Técnicas de curativos e feridas', (SELECT id FROM vacancies_jobcategory WHERE name = 'Enfermagem' LIMIT 1)),
('Atendimento ao Paciente', 'Comunicação e cuidado humanizado', (SELECT id FROM vacancies_jobcategory WHERE name = 'Enfermagem' LIMIT 1)),

-- Habilidades Administrativas
('Gestão de Equipe', 'Liderança e coordenação de pessoas', (SELECT id FROM vacancies_jobcategory WHERE name = 'Administração' LIMIT 1)),
('Excel Avançado', 'Domínio avançado da planilha Excel', (SELECT id FROM vacancies_jobcategory WHERE name = 'Administração' LIMIT 1)),
('SAP', 'Sistema de gestão empresarial SAP', (SELECT id FROM vacancies_jobcategory WHERE name = 'Administração' LIMIT 1)),
('Contabilidade', 'Conhecimentos contábeis e financeiros', (SELECT id FROM vacancies_jobcategory WHERE name = 'Administração' LIMIT 1)),
('Recursos Humanos', 'Gestão de pessoas e processos de RH', (SELECT id FROM vacancies_jobcategory WHERE name = 'Administração' LIMIT 1)),

-- Habilidades Técnicas
('Manutenção de Equipamentos', 'Reparo e manutenção de equipamentos médicos', (SELECT id FROM vacancies_jobcategory WHERE name = 'Técnico' LIMIT 1)),
('Informática', 'Conhecimentos em informática e sistemas', (SELECT id FROM vacancies_jobcategory WHERE name = 'Técnico' LIMIT 1)),
('Radiologia', 'Operação de equipamentos de raio-X', (SELECT id FROM vacancies_jobcategory WHERE name = 'Técnico' LIMIT 1)),
('Laboratório', 'Análises clínicas e laboratoriais', (SELECT id FROM vacancies_jobcategory WHERE name = 'Técnico' LIMIT 1)),
('Segurança do Trabalho', 'Normas e procedimentos de segurança', (SELECT id FROM vacancies_jobcategory WHERE name = 'Técnico' LIMIT 1)),

-- Habilidades de Apoio
('Limpeza Hospitalar', 'Técnicas de limpeza e desinfecção hospitalar', (SELECT id FROM vacancies_jobcategory WHERE name = 'Apoio' LIMIT 1)),
('Logística', 'Gestão de materiais e suprimentos', (SELECT id FROM vacancies_jobcategory WHERE name = 'Apoio' LIMIT 1)),
('Recepção', 'Atendimento ao público e telefone', (SELECT id FROM vacancies_jobcategory WHERE name = 'Apoio' LIMIT 1)),
('Segurança', 'Controle de acesso e vigilância', (SELECT id FROM vacancies_jobcategory WHERE name = 'Apoio' LIMIT 1)),
('Alimentação', 'Preparo e distribuição de refeições', (SELECT id FROM vacancies_jobcategory WHERE name = 'Apoio' LIMIT 1)),

-- Habilidades Soft Skills (sem categoria específica)
('Comunicação', 'Habilidades de comunicação verbal e escrita', NULL),
('Trabalho em Equipe', 'Capacidade de colaborar efetivamente', NULL),
('Liderança', 'Habilidades de liderança e influência', NULL),
('Resolução de Problemas', 'Capacidade analítica e tomada de decisão', NULL),
('Adaptabilidade', 'Flexibilidade para mudanças e novos desafios', NULL),
('Organização', 'Capacidade de organizar tarefas e tempo', NULL),
('Empatia', 'Capacidade de compreender e se conectar com outros', NULL),
('Ética Profissional', 'Conduta profissional e responsabilidade', NULL)
ON CONFLICT (name) DO NOTHING;

-- Verificar quantas skills foram inseridas
SELECT COUNT(*) as total_skills FROM vacancies_skill;

-- Mostrar algumas skills inseridas
SELECT s.name, c.name as categoria
FROM vacancies_skill s
LEFT JOIN vacancies_jobcategory c ON s.category_id = c.id
ORDER BY c.name, s.name
LIMIT 10;
