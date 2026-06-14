"""
Пример использования медицинского агента
Example usage of the Medical Agent
"""

import asyncio
from src.core.agent import MedicalAgent
from src.voice.speech_to_text import SpeechRecognizer
from src.voice.text_to_speech import TextToSpeech
from src.medical.questionnaire import Questionnaire
from src.medical.rag import RAGSystem


async def example_basic_usage():
    """Базовое использование агента"""
    print("=== Пример 1: Базовое использование ===\n")
    
    # Инициализируем агента
    agent = MedicalAgent(debug=True)
    
    # Сообщение пациента
    patient_msg = "У меня болит горло и поднялась температура"
    response = await agent.process_patient_message(patient_msg)
    print(f"Пациент: {patient_msg}")
    print(f"Агент: {response}\n")


async def example_with_questionnaire():
    """Использование с анкетой"""
    print("=== Пример 2: Сбор анамнеза через анкету ===\n")
    
    questionnaire = Questionnaire(language="uk")
    
    # Симулируем заполнение анкеты
    answers = {
        "age": "35",
        "gender": "male",
        "main_complaint": "Кашель и температура",
        "symptom_duration": "3_5_days",
        "temperature": "high",
        "other_symptoms": "Боль в горле, усталость",
        "allergies": "На пенициллин",
        "medications": "Нет",
        "chronic_diseases": "Нет"
    }
    
    # Заполняем анкету
    for i, question in enumerate(questionnaire.questions):
        answer = answers.get(question["id"], "")
        if questionnaire.answer_current_question(answer):
            print(f"✓ Вопрос {i+1}: {questionnaire.questions[i-1]['text']['uk']}")
            print(f"  Ответ: {answer}\n")
    
    # Получаем информацию о пациенте
    patient_info = questionnaire.get_patient_info()
    print(f"Информация о пациенте:")
    for key, value in patient_info.items():
        print(f"  {key}: {value}\n")


async def example_rag_system():
    """Использование RAG системы"""
    print("=== Пример 3: RAG система ===\n")
    
    rag = RAGSystem()
    
    # Создаем пример документов
    from src.medical.rag import Document
    
    docs = [
        Document(
            id="1",
            title="Лечение ОРВИ",
            content="ОРВИ лечится симптоматически. Рекомендуется отдых, обильное питье, жаропонижающие средства.",
            category="treatment",
            metadata={"disease": "ОРВИ", "severity": "mild"}
        ),
        Document(
            id="2",
            title="Диагностика гриппа",
            content="Грипп диагностируется ПЦР тестом. Часто сопровождается высокой температурой и мышечной болью.",
            category="diagnosis",
            metadata={"disease": "грипп", "test": "ПЦР"}
        ),
    ]
    
    for doc in docs:
        rag.knowledge_base.add_document(doc)
    
    # Поиск информации
    query = "Как лечить ОРВИ?"
    context = rag.knowledge_base.get_context_for_query(query)
    
    print(f"Запрос: {query}")
    print(f"Найденная информация:\\n{context}\n")


async def example_voice_interaction():
    \"\"\"Использование голосового взаимодействия\"\"\"
    print(\"=== Пример 4: Голосовое взаимодействие ===\")
    print(\"Примечание: Требует наличие микрофона и динамиков\")\n    
    try:
        # Инициализируем компоненты
        tts = TextToSpeech()
        
        # Синтезируем и проигрываем речь
        text = \"Добро пожаловать в медицинского помощника. Пожалуйста, опишите ваши симптомы.\"\n        print(f\"Произносим: {text}\")\n        await tts.speak(text)\n        \n    except Exception as e:\n        print(f\"Ошибка: {e}\")\n\n\nasync def example_full_workflow():\n    \"\"\"Полный рабочий процесс\"\"\"\n    print(\"=== Пример 5: Полный рабочий процесс ===\")\n    print()\n    \n    # 1. Инициализируем агента\n    agent = MedicalAgent(debug=True)\n    \n    # 2. Пациент дает информацию\n    symptoms = [\n        \"У меня болит горло\",\n        \"Поднялась температура 38.5\",\n        \"Есть кашель\"\n    ]\n    \n    print(\"📋 Сбор симптомов:\\n\")\n    for symptom in symptoms:\n        response = await agent.process_patient_message(symptom)\n        print(f\"Пациент: {symptom}\")\n        print(f\"Агент: {response}\\n\")\n    \n    # 3. Врач запрашивает резюме\n    doctor_message = \"Дай резюме анамнеза\"\n    response = await agent.process_doctor_message(doctor_message)\n    print(f\"Врач: {doctor_message}\")\n    print(f\"Агент: {response}\\n\")\n    \n    # 4. Врач запрашивает предложения диагнозов\n    doctor_message = \"Какие диагнозы ты предлагаешь?\"\n    response = await agent.process_doctor_message(doctor_message)\n    print(f\"Врач: {doctor_message}\")\n    print(f\"Агент: {response}\\n\")\n\n\nasync def main():\n    \"\"\"Главная функция для запуска примеров\"\"\"\n    print(\"\\n\" + \"=\"*60)\n    print(\"  Примеры использования Медицинского ИИ-Помощника\")\n    print(\"=\"*60 + \"\\n\")\n    \n    try:\n        # Запускаем примеры\n        await example_basic_usage()\n        await example_with_questionnaire()\n        await example_rag_system()\n        # await example_voice_interaction()  # Раскомментируйте если есть аудиооборудование\n        await example_full_workflow()\n        \n        print(\"\\n\" + \"=\"*60)\n        print(\"✓ Все примеры завершены успешно!\")\n        print(\"=\"*60 + \"\\n\")\n        \n    except Exception as e:\n        print(f\"\\n✗ Ошибка: {e}\")\n        import traceback\n        traceback.print_exc()\n\n\nif __name__ == \"__main__\":\n    asyncio.run(main())\n