from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Professor(Base):
    __tablename__ = 'professores'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String)
    senha = Column(String)
    papel = Column(String)

class Disciplina(Base):
    __tablename__ = 'disciplinas'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    codigo = Column(String)
    turmas = relationship("Turma", back_populates="disciplina")

class Turma(Base):
    __tablename__ = 'turmas'
    id = Column(Integer, primary_key=True)
    ano = Column(Integer)
    semestre = Column(String)
    disciplina_id = Column(Integer, ForeignKey('disciplinas.id'))

    disciplina = relationship("Disciplina", back_populates="turmas")
    notas = relationship("Nota", back_populates="turmas")

class Aluno(Base):
    __tablename__ = 'alunos'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    matricula = Column(String)
    #notas = relationship("Nota", back_populates="alunos")

class Nota(Base):
    __tablename__ = 'notas'
    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id'))
    turma_id = Column(Integer, ForeignKey('turmas.id'))
    notas = Column(Float)
    #aluno = relationship("Aluno", back_populates="notas")
    turmas = relationship("Turma", back_populates="notas")

# Apenas a definição da tabela Professor está presente aqui.
# Precisamos adicionar apenas os códigos relacionados à tabela Professor
# e, em seguida, tentar popular essa tabela novamente.

# Códigos para outras tabelas como Disciplina, Turma, Aluno, Nota e Frequencia
# devem ser excluídos temporariamente para evitar confusões.
